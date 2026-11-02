"""
MediLoop Multi-Agent Orchestration Layer - FastAPI Router.
Provides authenticated endpoints for:
- Prescription processing pipeline
- Workflow status & timeline queries
- Extraction display checkpoint (immutable patient-facing results)
- Drug safety assessment & re-evaluation
- Order preparation (READY_TO_PLACE draft)
- Agent registry & execution logs
- Autonomous Procurement (recommendations, approvals, PDF download, goods receipt)
- Autonomous Refill Reminders (predictions & manual triggers)
"""
import os
import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_pharmacist, oauth2_scheme
from app.core.security import decode_access_token
from app.models.user import User
from app.models.pharmacist import Pharmacist
from app.models.purchase_order import SupplierPurchaseOrder
from app.models.orchestration import (
    AgentExecutionModel,
    ProcurementRecommendationModel,
    RefillPredictionModel
)
from app.schemas.orchestration import (
    WorkflowSummarySchema,
    PrescriptionExtractionSchema,
    DrugSafetyAssessmentSchema,
    OrderPreparationSchema,
    AgentRegistrySchema,
    ProcurementRecommendationSchema,
    ProcurementDraftSummarySchema,
    RefillPredictionSchema,
    ProcurementApprovalRequestSchema,
    SafetyReevaluationRequestSchema
)
from app.orchestration.orchestrator import MultiAgentOrchestrator
from app.orchestration.registry import MultiAgentRegistry
from app.orchestration.agents.procurement_agent import ProcurementAgent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orchestration", tags=["Multi-Agent Orchestration"])


def get_optional_actor(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[Any]:
    """Helper to retrieve user or pharmacist if authenticated; returns None if public/system."""
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload or not payload.get("sub"):
        return None
    try:
        sub_id = int(payload.get("sub"))
        role = payload.get("role")
        if role == "pharmacist":
            return db.query(Pharmacist).filter(Pharmacist.id == sub_id).first()
        return db.query(User).filter(User.id == sub_id).first()
    except Exception:
        return None


# ----------------------------------------------------------------------------
# 1. PRIMARY SEQUENTIAL PRESCRIPTION PIPELINE
# ----------------------------------------------------------------------------
@router.post("/prescriptions/{prescription_id}/process", response_model=WorkflowSummarySchema)
async def process_prescription_workflow(
    prescription_id: int,
    pharmacy_id: int = Query(1, description="Target pharmacy ID"),
    auto_order: bool = Query(True, description="Whether to automatically prepare draft order if safety screening passes"),
    payload: Optional[Dict[str, Any]] = Body(None),
    actor: Optional[Any] = Depends(get_optional_actor),
    db: Session = Depends(get_db)
):
    """
    Triggers the multi-agent orchestration pipeline for an uploaded prescription:
    OCR Agent -> Prescription Intelligence Agent -> Extraction Checkpoint -> Drug Safety Agent -> Order Agent.
    """
    patient_id = None
    if actor and isinstance(actor, User):
        patient_id = actor.id

    patient_selection = payload.get("patient_selection") if payload else None

    orchestrator = MultiAgentOrchestrator(db)
    try:
        summary = await orchestrator.process_prescription_workflow(
            prescription_id=prescription_id,
            patient_id=patient_id,
            pharmacy_id=pharmacy_id,
            patient_selection=patient_selection,
            auto_order=auto_order
        )
        return summary
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        logger.exception(f"Orchestration pipeline execution error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Pipeline error: {str(e)}")


@router.get("/workflows/{workflow_id}", response_model=WorkflowSummarySchema)
def get_workflow_status(
    workflow_id: str,
    db: Session = Depends(get_db)
):
    """Retrieves full workflow execution status, current step, and audit events."""
    orchestrator = MultiAgentOrchestrator(db)
    wf = orchestrator.get_workflow_details(workflow_id)
    if not wf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workflow '{workflow_id}' not found.")
    return wf


# ----------------------------------------------------------------------------
# 2. EXTRACTION DISPLAY CHECKPOINT (Patient App & Pharmacist Dashboard)
# ----------------------------------------------------------------------------
@router.get("/prescriptions/{prescription_id}/extraction", response_model=PrescriptionExtractionSchema)
def get_prescription_extraction(
    prescription_id: int,
    db: Session = Depends(get_db)
):
    """
    Extraction Display Checkpoint:
    Retrieves the consolidated, immutable extracted medicines, strengths, frequencies,
    quantities, and catalogue matching details for display in the mobile application.
    """
    orchestrator = MultiAgentOrchestrator(db)
    ext = orchestrator.get_prescription_extraction(prescription_id)
    if not ext:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prescription extraction has not yet been performed or completed for Prescription #{prescription_id}."
        )
    return ext


# ----------------------------------------------------------------------------
# 3. DRUG SAFETY ASSESSMENT & RE-EVALUATION
# ----------------------------------------------------------------------------
@router.get("/prescriptions/{prescription_id}/safety", response_model=DrugSafetyAssessmentSchema)
def get_prescription_safety(
    prescription_id: int,
    db: Session = Depends(get_db)
):
    """Retrieves clinical safety findings, interaction alerts, allergy conflicts, and risk ratings."""
    orchestrator = MultiAgentOrchestrator(db)
    safety = orchestrator.get_prescription_safety(prescription_id)
    if not safety:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No drug safety assessment found for Prescription #{prescription_id}."
        )
    return safety


@router.post("/prescriptions/{prescription_id}/safety/re-evaluate", response_model=DrugSafetyAssessmentSchema)
async def re_evaluate_safety(
    prescription_id: int,
    req: SafetyReevaluationRequestSchema,
    actor: Optional[Any] = Depends(get_optional_actor),
    db: Session = Depends(get_db)
):
    """
    Controlled clinical re-evaluation of safety findings.
    Enables registered pharmacists to override or clarify non-fatal warnings after clinical review.
    """
    orchestrator = MultiAgentOrchestrator(db)
    try:
        updated = await orchestrator.re_evaluate_safety(
            prescription_id=prescription_id,
            cleared_by_pharmacist=req.cleared_by_pharmacist,
            pharmacist_notes=req.pharmacist_notes
        )
        return updated
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))


# ----------------------------------------------------------------------------
# 4. ORDER PREPARATION (READY_TO_PLACE Draft)
# ----------------------------------------------------------------------------
@router.post("/orders/{prescription_id}/prepare", response_model=OrderPreparationSchema)
@router.post("/prescriptions/{prescription_id}/prepare-order", response_model=OrderPreparationSchema)
async def prepare_prescription_order(
    prescription_id: int,
    pharmacy_id: int = Query(1, description="Target pharmacy ID"),
    patient_selection: Optional[Dict[str, Any]] = Body(None),
    actor: Optional[Any] = Depends(get_optional_actor),
    db: Session = Depends(get_db)
):
    """
    Executes Agent 4 (Order Agent) to prepare cart and create READY_TO_PLACE draft order
    based on patient's confirmed medicine selection and verified safety clearance.
    """
    orchestrator = MultiAgentOrchestrator(db)
    ext = orchestrator.get_prescription_extraction(prescription_id)
    if not ext:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Extraction must be completed first.")

    safety = orchestrator.get_prescription_safety(prescription_id)
    if not safety:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Safety assessment must be completed first.")

    if not safety.can_proceed and not safety.pharmacist_cleared:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order preparation blocked by serious drug safety finding. Requires pharmacist clearance."
        )

    patient_id = ext.patient_id
    from app.orchestration.agents.order_agent import OrderAgent
    agent = OrderAgent(db)
    result = await agent.execute(
        prescription_id=prescription_id,
        patient_id=patient_id,
        extracted_medicines=ext.extracted_medicines,
        safety_assessment=safety,
        pharmacy_id=pharmacy_id,
        patient_selection=patient_selection
    )
    return result


# ----------------------------------------------------------------------------
# 5. AGENT REGISTRY & EXECUTION MONITORING
# ----------------------------------------------------------------------------
@router.get("/agents", response_model=List[AgentRegistrySchema])
def list_registered_agents(db: Session = Depends(get_db)):
    """Lists all 6 registered orchestration agents with versions, dependencies, and statuses."""
    registry = MultiAgentRegistry(db)
    return registry.list_all_agents()


@router.get("/agents/{agent_id}/status")
def get_agent_status(agent_id: str, db: Session = Depends(get_db)):
    """Retrieves operational status, health, and recent execution counts for an agent."""
    registry = MultiAgentRegistry(db)
    agent = registry.get_agent_metadata(agent_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent '{agent_id}' not found.")

    recent_runs = db.query(AgentExecutionModel).filter(
        AgentExecutionModel.agent_id == agent_id
    ).order_by(AgentExecutionModel.started_at.desc()).limit(10).all()

    success_count = sum(1 for r in recent_runs if r.status == "COMPLETED")
    fail_count = sum(1 for r in recent_runs if r.status == "FAILED")

    return {
        "agent": agent,
        "recent_executions_sample": len(recent_runs),
        "recent_successes": success_count,
        "recent_failures": fail_count,
        "is_healthy": (fail_count == 0 or success_count >= fail_count)
    }


@router.get("/executions/{execution_id}")
def get_execution_details(execution_id: str, db: Session = Depends(get_db)):
    """Retrieves execution record, processing duration, and payload for a specific run."""
    exec_rec = db.query(AgentExecutionModel).filter(AgentExecutionModel.execution_id == execution_id).first()
    if not exec_rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Execution '{execution_id}' not found.")
    return exec_rec


# ----------------------------------------------------------------------------
# 6. PROCUREMENT WORKFLOW (Pharmacist Dashboard Endpoints)
# ----------------------------------------------------------------------------
@router.get("/procurement/recommendations", response_model=List[ProcurementRecommendationSchema])
def list_procurement_recommendations(
    pharmacy_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Lists all active inventory shortage recommendations and draft purchase orders."""
    recs = db.query(ProcurementRecommendationModel).filter(
        ProcurementRecommendationModel.pharmacy_id == pharmacy_id
    ).order_by(ProcurementRecommendationModel.created_at.desc()).all()
    return recs


@router.post("/procurement/trigger", response_model=ProcurementDraftSummarySchema)
async def trigger_procurement_worker(
    pharmacy_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Manually triggers the autonomous Procurement Agent to evaluate low stock and draft a PO."""
    orchestrator = MultiAgentOrchestrator(db)
    summary = await orchestrator.run_procurement_worker(pharmacy_id=pharmacy_id)
    return summary


@router.get("/procurement/{purchase_order_id}/pdf")
def get_procurement_po_pdf(
    purchase_order_id: int,
    db: Session = Depends(get_db)
):
    """Serves the generated ReportLab Purchase Order PDF document."""
    po = db.query(SupplierPurchaseOrder).filter(SupplierPurchaseOrder.id == purchase_order_id).first()
    if not po:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase order not found.")

    rec = db.query(ProcurementRecommendationModel).filter(
        ProcurementRecommendationModel.purchase_order_id == purchase_order_id
    ).first()

    pdf_path = rec.pdf_reference if rec and rec.pdf_reference else None
    if not pdf_path or not os.path.exists(pdf_path):
        # Fallback path search
        expected = os.path.join(os.getcwd(), "backend", "uploads", "procurement", f"{po.po_number}.pdf")
        if os.path.exists(expected):
            pdf_path = expected

    if not pdf_path or not os.path.exists(pdf_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PO PDF file not found on disk.")

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"{po.po_number}.pdf"
    )


@router.post("/procurement/{purchase_order_id}/approve")
def approve_procurement_order(
    purchase_order_id: int,
    pharmacist_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Pharmacist approves a draft purchase order for distributor transmission."""
    agent = ProcurementAgent(db)
    try:
        po = agent.approve_purchase_order(purchase_order_id, pharmacist_id)
        return {"status": "SUCCESS", "message": f"PO {po.po_number} successfully APPROVED.", "po_id": po.id}
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))


@router.post("/procurement/{purchase_order_id}/send")
def send_procurement_order(
    purchase_order_id: int,
    db: Session = Depends(get_db)
):
    """Dispatches the approved purchase order to the pharmaceutical distributor."""
    agent = ProcurementAgent(db)
    try:
        po = agent.send_purchase_order(purchase_order_id)
        return {"status": "SUCCESS", "message": f"PO {po.po_number} dispatched to supplier.", "po_id": po.id}
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))


@router.post("/procurement/{purchase_order_id}/receive")
def receive_procurement_order(
    purchase_order_id: int,
    payload: Optional[Dict[str, Any]] = Body(None),
    db: Session = Depends(get_db)
):
    """
    Goods Receipt:
    When ordered stock physically arrives at the pharmacy, pharmacist records receipt,
    which updates inventory quantities in pharmacy_inventory.
    """
    agent = ProcurementAgent(db)
    items = payload.get("items") if payload else None
    try:
        po = agent.receive_goods(purchase_order_id, items)
        return {
            "status": "SUCCESS",
            "message": f"Goods received for PO {po.po_number}. Pharmacy inventory updated.",
            "po_id": po.id
        }
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))


# ----------------------------------------------------------------------------
# 7. REFILL REMINDER WORKFLOW
# ----------------------------------------------------------------------------
@router.get("/refill/predictions", response_model=List[RefillPredictionSchema])
def list_refill_predictions(
    patient_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Lists current medication refill predictions and adherence tracking."""
    query = db.query(RefillPredictionModel).filter(RefillPredictionModel.is_active == True)
    if patient_id:
        query = query.filter(RefillPredictionModel.patient_id == patient_id)
    records = query.order_by(RefillPredictionModel.expected_refill_date.asc()).all()

    results = []
    for r in records:
        results.append(RefillPredictionSchema(
            id=r.id,
            patient_id=r.patient_id,
            medicine_id=r.medicine_id,
            medicine_name=r.medicine_name,
            last_order_date=r.last_order_date,
            last_ordered_quantity=r.last_ordered_quantity,
            daily_usage_rate=r.daily_usage_rate,
            estimated_remaining_days=r.estimated_remaining_days,
            expected_refill_date=r.expected_refill_date,
            confidence=r.confidence,
            reason=r.reason,
            is_active=r.is_active,
            reminder_sent=len(r.reminders) > 0,
            reminder_type=r.reminders[0].reminder_type if r.reminders else None
        ))
    return results


@router.post("/refill/trigger", response_model=List[RefillPredictionSchema])
async def trigger_refill_worker(
    patient_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Manually triggers the autonomous Refill Reminder Agent."""
    orchestrator = MultiAgentOrchestrator(db)
    predictions = await orchestrator.run_refill_reminder_worker(patient_id=patient_id)
    return predictions

