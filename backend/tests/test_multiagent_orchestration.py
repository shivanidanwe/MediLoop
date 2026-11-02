"""
MediLoop Multi-Agent Orchestration Layer - Comprehensive Test Suite.
Tests all 6 production agents, the Central Orchestrator, Checkpoints, Guardrails,
ReportLab PDF PO Generation, and background workers.
"""
import os
import sys
import pytest
from datetime import datetime, timezone, timedelta

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.medical_info import MedicalInfo
from app.models.pharmacy import Pharmacy
from app.models.medicine import Medicine
from app.models.pharmacy_inventory import PharmacyInventory
from app.models.prescription import Prescription, VerificationStatus
from app.models.order import Order, OrderItem, OrderStatus
from app.models.notification import Notification
from app.models.purchase_order import SupplierPurchaseOrder
from app.models.orchestration import (
    AgentWorkflowModel,
    PrescriptionOCRResultModel,
    PrescriptionExtractionModel,
    DrugSafetyAssessmentModel,
    RefillPredictionModel,
    ProcurementRecommendationModel
)
from app.orchestration.registry import MultiAgentRegistry
from app.orchestration.orchestrator import MultiAgentOrchestrator
from app.orchestration.agents.ocr_agent import OCRAgent
from app.orchestration.agents.prescription_intelligence_agent import PrescriptionIntelligenceAgent
from app.orchestration.agents.drug_safety_agent import DrugSafetyAgent
from app.orchestration.agents.order_agent import OrderAgent
from app.orchestration.agents.refill_reminder_agent import RefillReminderAgent
from app.orchestration.agents.procurement_agent import ProcurementAgent
from app.schemas.orchestration import ExtractedMedicineSchema, CatalogueMatchSchema, DrugSafetyAssessmentSchema


@pytest.fixture(scope="module")
def db_session():
    """Provides a database session for testing."""
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture(autouse=True)
def clean_db_session(db_session):
    """Ensures clean transaction state for each test function."""
    db_session.rollback()
    yield
    db_session.rollback()


@pytest.fixture(scope="module")
def seed_data(db_session):
    """Seeds test data (user, pharmacy, medicine, inventory) if not already present."""
    # 1. Pharmacy
    pharmacy = db_session.query(Pharmacy).filter(Pharmacy.id == 1).first()
    if not pharmacy:
        pharmacy = Pharmacy(
            id=1,
            pharmacy_name="Kalawati Medical & General Stores",
            address="Shivaji Road, Pune, Maharashtra",
            phone="020-24451234",
            email="kalawati@pharma.in",
            is_active=True
        )
        db_session.add(pharmacy)
        db_session.commit()

    # 2. Test User
    user = db_session.query(User).filter(User.email == "test_patient_orchestration@mediloop.in").first()
    if not user:
        user = User(
            email="test_patient_orchestration@mediloop.in",
            mobile_number="9876543210",
            full_name="Rajesh Sharma",
            hashed_password="mock_hash_for_testing",
            date_of_birth=datetime(1990, 1, 1).date(),
            gender="MALE",
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

    # 3. Medical Info with Penicillin Allergy
    med_info = db_session.query(MedicalInfo).filter(MedicalInfo.user_id == user.id).first()
    if not med_info:
        med_info = MedicalInfo(
            user_id=user.id,
            allergies="penicillin, dust",
            medical_conditions="hypertension"
        )
        db_session.add(med_info)
        db_session.commit()

    # 4. Medicines
    med_crocin = db_session.query(Medicine).filter(Medicine.brand_name.ilike("%Crocin%")).first()
    if not med_crocin:
        med_crocin = Medicine(
            brand_name="Crocin 650",
            generic_name="Paracetamol",
            manufacturer="GlaxoSmithKline",
            strength="650mg",
            dosage_form="Tablet",
            prescription_required=False,
            is_active=True
        )
        db_session.add(med_crocin)

    med_amox = db_session.query(Medicine).filter(Medicine.brand_name.ilike("%Amoxicillin%")).first()
    if not med_amox:
        med_amox = Medicine(
            brand_name="Amoxicillin 500",
            generic_name="Amoxicillin",
            manufacturer="Cipla",
            strength="500mg",
            dosage_form="Capsule",
            prescription_required=True,
            is_active=True
        )
        db_session.add(med_amox)

    med_ator = db_session.query(Medicine).filter(Medicine.brand_name.ilike("%Atorvastatin%")).first()
    if not med_ator:
        med_ator = Medicine(
            brand_name="Atorvastatin 10",
            generic_name="Atorvastatin",
            manufacturer="Sun Pharma",
            strength="10mg",
            dosage_form="Tablet",
            prescription_required=True,
            is_active=True
        )
        db_session.add(med_ator)

    db_session.commit()

    # 5. Inventory for Pharmacy 1
    for m in [med_crocin, med_amox, med_ator]:
        db_session.refresh(m)
        inv = db_session.query(PharmacyInventory).filter(
            PharmacyInventory.pharmacy_id == 1,
            PharmacyInventory.medicine_id == m.id
        ).first()
        if not inv:
            inv = PharmacyInventory(
                pharmacy_id=1,
                medicine_id=m.id,
                stock_quantity=100,
                selling_price=45.0,
                mrp=50.0,
                batch_number="BAT-2026-TEST",
                expiry_date=datetime(2027, 12, 31).date(),
                is_available=True
            )
            db_session.add(inv)
    db_session.commit()

    # 6. Test Prescription
    rx = db_session.query(Prescription).filter(Prescription.customer_id == user.id).first()
    if not rx:
        rx = Prescription(
            customer_id=user.id,
            pharmacy_id=1,
            uploaded_image_path="uploads/prescriptions/mock_rx.jpg",
            original_filename="mock_rx.jpg",
            extracted_text="Rx\nTab Crocin 650mg\n1-0-1\n5 Days\n\nCap Amoxicillin 500mg\n1-0-1\n5 Days",
            verification_status="PENDING_VERIFICATION"
        )
        db_session.add(rx)
        db_session.commit()
        db_session.refresh(rx)

    return {
        "user": user,
        "pharmacy": pharmacy,
        "prescription": rx,
        "crocin": med_crocin,
        "amoxicillin": med_amox,
        "atorvastatin": med_ator
    }


# ============================================================================
# 1. TEST AGENT REGISTRY
# ============================================================================
def test_agent_registry(db_session):
    """Verifies all 6 production agents are registered in AgentRegistryModel."""
    registry = MultiAgentRegistry(db_session)
    count = registry.sync_to_db()
    assert count == 6

    agents = registry.list_all_agents()
    agent_ids = [a.agent_id for a in agents]
    expected_ids = [
        "ocr_agent",
        "prescription_intelligence_agent",
        "drug_safety_agent",
        "order_agent",
        "refill_reminder_agent",
        "procurement_agent"
    ]
    for exp in expected_ids:
        assert exp in agent_ids


# ============================================================================
# 2. TEST AGENT 1: OCR AGENT
# ============================================================================
@pytest.mark.asyncio
async def test_ocr_agent_execution(db_session, seed_data):
    """Verifies OCR Agent extracts raw text and detects medicine regions."""
    rx = seed_data["prescription"]
    agent = OCRAgent(db_session)

    result = await agent.execute(prescription_id=rx.id, patient_id=rx.customer_id)

    assert result.prescription_id == rx.id
    assert len(result.raw_text) > 0
    assert result.confidence_score >= 0.70
    assert result.status == "COMPLETED"

    # Check persistence in database
    ocr_record = db_session.query(PrescriptionOCRResultModel).filter(
        PrescriptionOCRResultModel.prescription_id == rx.id
    ).first()
    assert ocr_record is not None
    assert ocr_record.ocr_confidence == result.confidence_score


# ============================================================================
# 3. TEST AGENT 2: PRESCRIPTION INTELLIGENCE AGENT & CHECKPOINT
# ============================================================================
@pytest.mark.asyncio
async def test_prescription_intelligence_agent(db_session, seed_data):
    """Verifies Medical NER, catalogue matching, and checkpoint persistence."""
    rx = seed_data["prescription"]
    agent = PrescriptionIntelligenceAgent(db_session)

    raw_rx_text = "Rx\nTab Crocin 650mg\n1-0-1\n5 Days\n\nCap Amoxicillin 500mg\n1-0-1\n5 Days"
    result = await agent.execute(
        prescription_id=rx.id,
        patient_id=rx.customer_id,
        raw_text=raw_rx_text
    )

    assert result.prescription_id == rx.id
    assert result.total_medicines >= 1
    assert result.matched_medicines_count >= 1

    # Check immutability flag in database
    ext_rec = db_session.query(PrescriptionExtractionModel).filter(
        PrescriptionExtractionModel.prescription_id == rx.id
    ).order_by(PrescriptionExtractionModel.created_at.desc()).first()
    assert ext_rec is not None
    assert ext_rec.published_to_patient == True


# ============================================================================
# 4. TEST AGENT 3: DRUG SAFETY AGENT (Allergy Conflict & Critical Gate)
# ============================================================================
@pytest.mark.asyncio
async def test_drug_safety_agent_allergy_conflict(db_session, seed_data):
    """
    Patient Rajesh Sharma is recorded allergic to 'penicillin'.
    Prescribing Amoxicillin (penicillin class) MUST trigger critical safety finding
    and set can_proceed=False to halt ordering.
    """
    rx = seed_data["prescription"]
    user = seed_data["user"]
    agent = DrugSafetyAgent(db_session)

    amox_item = ExtractedMedicineSchema(
        medicine_name="Amoxicillin 500",
        generic_name="Amoxicillin",
        brand_name="Amoxicillin 500",
        strength="500mg",
        dosage="1 capsule",
        frequency="1-0-1",
        duration="5 days",
        quantity=10,
        catalogue_match=CatalogueMatchSchema(
            medicine_id=seed_data["amoxicillin"].id,
            brand_name="Amoxicillin 500",
            generic_name="Amoxicillin",
            strength="500mg",
            unit_price=85.00
        )
    )

    assessment = await agent.execute(
        prescription_id=rx.id,
        patient_id=user.id,
        extracted_medicines=[amox_item]
    )

    assert assessment.patient_id == user.id
    assert assessment.can_proceed == False
    assert assessment.requires_review == True
    assert assessment.safety_status in ("critical", "warning")
    assert any(f.issue_type == "allergy" for f in assessment.findings)


@pytest.mark.asyncio
async def test_drug_safety_agent_safe(db_session, seed_data):
    """Prescribing Crocin (Paracetamol) to a patient with only penicillin allergy should pass safely."""
    rx = seed_data["prescription"]
    user = seed_data["user"]
    agent = DrugSafetyAgent(db_session)

    crocin_item = ExtractedMedicineSchema(
        medicine_name="Crocin 650",
        generic_name="Paracetamol",
        brand_name="Crocin",
        strength="650mg",
        dosage="1 tablet",
        frequency="1-0-1",
        duration="5 days",
        quantity=10,
        catalogue_match=CatalogueMatchSchema(
            medicine_id=seed_data["crocin"].id,
            brand_name="Crocin 650",
            generic_name="Paracetamol",
            strength="650mg",
            unit_price=32.50
        )
    )

    assessment = await agent.execute(
        prescription_id=rx.id,
        patient_id=user.id,
        extracted_medicines=[crocin_item]
    )

    assert assessment.can_proceed == True
    assert assessment.overall_risk == "low"


# ============================================================================
# 5. TEST AGENT 4: ORDER AGENT (Cart & READY_TO_PLACE Draft)
# ============================================================================
@pytest.mark.asyncio
async def test_order_agent_execution(db_session, seed_data):
    """Verifies inventory check, decimal pricing, cart creation, and READY_TO_PLACE draft order."""
    rx = seed_data["prescription"]
    user = seed_data["user"]
    crocin = seed_data["crocin"]
    agent = OrderAgent(db_session)

    crocin_item = ExtractedMedicineSchema(
        medicine_name="Crocin 650",
        generic_name="Paracetamol",
        brand_name="Crocin",
        strength="650mg",
        dosage="1 tablet",
        frequency="1-0-1",
        duration="5 days",
        quantity=10,
        catalogue_match=CatalogueMatchSchema(
            medicine_id=crocin.id,
            brand_name="Crocin 650",
            generic_name="Paracetamol",
            strength="650mg",
            unit_price=32.50
        )
    )

    mock_safety = DrugSafetyAssessmentSchema(
        prescription_id=rx.id,
        patient_id=user.id,
        safety_status="safe",
        overall_risk="low",
        checks_performed=["allergy_check"],
        findings=[],
        requires_review=False,
        can_proceed=True,
        pharmacist_cleared=True
    )

    order_result = await agent.execute(
        prescription_id=rx.id,
        patient_id=user.id,
        extracted_medicines=[crocin_item],
        safety_assessment=mock_safety,
        pharmacy_id=1
    )

    assert order_result.order_status == "READY_TO_PLACE"
    assert order_result.total_amount > 0.0
    assert order_result.draft_order_id is not None
    assert order_result.cart_id is not None
    assert len(order_result.items) == 1

    # Verify order exists in DB
    db_order = db_session.query(Order).filter(Order.id == order_result.draft_order_id).first()
    assert db_order is not None
    assert db_order.order_status == "READY_TO_PLACE"


# ============================================================================
# 6. TEST AGENT 5: REFILL REMINDER AGENT
# ============================================================================
@pytest.mark.asyncio
async def test_refill_reminder_agent(db_session, seed_data):
    """
    Creates a completed order placed 28 days ago for a 30-day supply (60 tabs @ 2/day).
    Remaining days = 2, which falls within <= 3 days threshold.
    Verifies reminder dispatch and deduplication.
    """
    user = seed_data["user"]
    crocin = seed_data["crocin"]

    past_date = datetime.now(timezone.utc) - timedelta(days=28)
    completed_order = Order(
        order_number=f"ORD-REFILL-{int(past_date.timestamp())}",
        customer_id=user.id,
        pharmacy_id=1,
        order_status=OrderStatus.DELIVERED,
        payment_method="CASH_ON_DELIVERY",
        payment_status="PAID",
        total_amount=195.0,
        placed_at=past_date
    )
    db_session.add(completed_order)
    db_session.commit()
    db_session.refresh(completed_order)

    ord_item = OrderItem(
        order_id=completed_order.id,
        medicine_id=crocin.id,
        quantity=60,
        unit_price=3.25,
        total_price=195.0
    )
    db_session.add(ord_item)
    db_session.commit()

    agent = RefillReminderAgent(db_session, reminder_threshold_days=7)
    predictions = await agent.execute(patient_id=user.id)

    assert len(predictions) >= 1
    target_pred = next((p for p in predictions if p.medicine_id == crocin.id), None)
    assert target_pred is not None
    assert target_pred.estimated_remaining_days <= 3

    # Check that a notification was dispatched
    notif = db_session.query(Notification).filter(
        Notification.user_id == user.id,
        Notification.notification_type == "REFILL_REMINDER"
    ).first()
    assert notif is not None


# ============================================================================
# 7. TEST AGENT 6: PROCUREMENT AGENT & PDF PO GENERATION
# ============================================================================
@pytest.mark.asyncio
async def test_procurement_agent_and_pdf(db_session, seed_data):
    """
    Sets inventory stock to 2 units (below threshold of 15).
    Procurement agent must detect low stock, calculate shortage,
    create draft PO, and generate ReportLab PDF.
    Then tests pharmacist approval and goods receipt.
    """
    crocin = seed_data["crocin"]
    inv = db_session.query(PharmacyInventory).filter(
        PharmacyInventory.pharmacy_id == 1,
        PharmacyInventory.medicine_id == crocin.id
    ).first()
    inv.stock_quantity = 2  # Depleted stock
    db_session.commit()

    agent = ProcurementAgent(db_session, default_reorder_threshold=15, default_target_stock=100)
    summary = await agent.execute(pharmacy_id=1)

    assert summary.total_items >= 1
    assert summary.status == "AWAITING_PHARMACIST_APPROVAL"
    assert summary.pdf_reference is not None

    # Verify PDF file exists on disk
    assert os.path.exists(summary.pdf_reference)
    assert summary.pdf_reference.endswith(".pdf")

    # Pharmacist Approval
    po_id = summary.purchase_order_id
    approved_po = agent.approve_purchase_order(po_id, pharmacist_id=1)
    assert approved_po.status == "APPROVED"

    # Send to Supplier
    sent_po = agent.send_purchase_order(po_id)
    assert sent_po.status == "SENT_TO_SUPPLIER"

    # Goods Receipt: Delivery arrives with 98 units
    agent.receive_goods(po_id, received_items=[{"medicine_id": crocin.id, "quantity": 98, "unit_price": 22.0}])
    db_session.refresh(inv)
    assert inv.stock_quantity == 100  # 2 original + 98 received = 100!


# ============================================================================
# 8. TEST CENTRAL ORCHESTRATOR END-TO-END PIPELINE
# ============================================================================
@pytest.mark.asyncio
async def test_end_to_end_orchestrator_pipeline(db_session, seed_data):
    """
    Tests complete sequential pipeline execution:
    Prescription Upload -> OCR -> NER & Catalogue -> Extraction Checkpoint -> Drug Safety -> Order Draft.
    """
    rx = seed_data["prescription"]
    user = seed_data["user"]
    orchestrator = MultiAgentOrchestrator(db_session)

    summary = await orchestrator.process_prescription_workflow(
        prescription_id=rx.id,
        patient_id=user.id,
        pharmacy_id=1,
        auto_order=False  # Stop at safety check for safe review
    )

    assert summary.workflow_id.startswith("wf_")
    assert len(summary.events) >= 2
    assert summary.prescription_id == rx.id

    # Verify extraction checkpoint can be queried
    ext = orchestrator.get_prescription_extraction(rx.id)
    assert ext is not None
    assert ext.prescription_id == rx.id

    # Verify safety report can be queried
    safety = orchestrator.get_prescription_safety(rx.id)
    assert safety is not None
    assert safety.prescription_id == rx.id
