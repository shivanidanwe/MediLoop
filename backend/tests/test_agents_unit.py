"""
Unit Tests for all 10 MediLoop AI Agents.
Tests each agent independently with isolated inputs and mocked dependencies.
"""
import pytest
from app.agents import (
    AgentContext,
    AgentEvent,
    OCRAgent,
    PrescriptionIntelligenceAgent,
    MedicineMatchingAgent,
    DrugSafetyAgent,
    InventoryAvailabilityAgent,
    OrderRecommendationAgent,
    RefillReminderAgent,
    NotificationAgent,
    AIHealthCompanionAgent,
    AgentValidationError,
)


@pytest.mark.asyncio
async def test_ocr_agent_unit():
    agent = OCRAgent()
    ctx = AgentContext(uploaded_image="/uploads/prescriptions/rx_scan.jpg")
    
    assert await agent.can_handle(AgentEvent.PRESCRIPTION_UPLOADED, ctx) is True
    assert await agent.validate(ctx) is True
    
    result_ctx = await agent.execute(ctx)
    assert result_ctx.ocr_text is not None
    assert "ocr" in result_ctx.metadata
    assert result_ctx.metadata["ocr"]["confidence"] >= 0.90


@pytest.mark.asyncio
async def test_prescription_intelligence_agent_unit():
    agent = PrescriptionIntelligenceAgent()
    ocr_sample = "Rx: Paracetamol 500mg - 1 tab 1-0-1 for 5 days.\nAmoxicillin 250mg - 1 capsule BID for 7 days."
    ctx = AgentContext(ocr_text=ocr_sample)

    assert await agent.can_handle(AgentEvent.OCR_COMPLETED, ctx) is True
    assert await agent.validate(ctx) is True

    result_ctx = await agent.execute(ctx)
    assert len(result_ctx.extracted_medicines) == 2
    assert result_ctx.extracted_medicines[0]["name"] == "Paracetamol"
    assert result_ctx.extracted_medicines[0]["strength"] == "500mg"


@pytest.mark.asyncio
async def test_medicine_matching_agent_unit():
    agent = MedicineMatchingAgent()
    extracted = [
        {"name": "Crocin 650", "strength": "650mg"},
        {"name": "PCM", "strength": "500mg"},
        {"name": "Amoxycillin", "strength": "250mg"},
    ]
    ctx = AgentContext(extracted_medicines=extracted)

    assert await agent.can_handle(AgentEvent.MEDICINES_EXTRACTED, ctx) is True
    assert await agent.validate(ctx) is True

    result_ctx = await agent.execute(ctx)
    assert len(result_ctx.matched_medicines) == 3
    assert result_ctx.matched_medicines[0]["name"] == "Crocin 650"
    assert result_ctx.matched_medicines[1]["generic_name"] == "Paracetamol"
    assert result_ctx.matched_medicines[2]["generic_name"] == "Amoxicillin"


@pytest.mark.asyncio
async def test_drug_safety_agent_unit():
    agent = DrugSafetyAgent()
    matched = [
        {"name": "Warfarin 5mg", "generic_name": "Warfarin"},
        {"name": "Ecosprin 75mg", "generic_name": "Aspirin"},
    ]
    ctx = AgentContext(matched_medicines=matched, metadata={"user_allergies": []})

    assert await agent.can_handle(AgentEvent.MEDICINES_MATCHED, ctx) is True
    assert await agent.validate(ctx) is True

    result_ctx = await agent.execute(ctx)
    safety_meta = result_ctx.metadata["drug_safety"]
    assert safety_meta["risk_level"] == "CRITICAL"
    assert safety_meta["requires_pharmacist_review"] is True


@pytest.mark.asyncio
async def test_inventory_availability_agent_unit():
    agent = InventoryAvailabilityAgent()
    matched = [{"id": 1, "name": "Crocin 650", "quantity": "10"}]
    ctx = AgentContext(matched_medicines=matched, pharmacy_id=1)

    assert await agent.can_handle(AgentEvent.SAFETY_VALIDATION_COMPLETED, ctx) is True
    assert await agent.validate(ctx) is True

    result_ctx = await agent.execute(ctx)
    inv_meta = result_ctx.metadata["inventory"]
    assert inv_meta["overall_status"] == "AVAILABLE"
    assert inv_meta["complete_order"] is True


@pytest.mark.asyncio
async def test_order_recommendation_agent_unit():
    agent = OrderRecommendationAgent()
    ctx = AgentContext(
        matched_medicines=[{"name": "Crocin 650"}],
        metadata={
            "drug_safety": {"risk_level": "LOW", "requires_pharmacist_review": False},
            "inventory": {"complete_order": True, "selected_pharmacy": {"id": 1, "name": "MediLoop Central"}}
        }
    )

    assert await agent.can_handle(AgentEvent.INVENTORY_CHECKED, ctx) is True
    assert await agent.validate(ctx) is True

    result_ctx = await agent.execute(ctx)
    rec_meta = result_ctx.metadata["order_recommendation"]
    assert rec_meta["order_status"] == "READY_FOR_CHECKOUT"
    assert rec_meta["requires_pharmacist_review"] is False


@pytest.mark.asyncio
async def test_refill_reminder_agent_unit():
    agent = RefillReminderAgent(reminder_window_days=5)
    matched = [{"name": "Atorvastatin 10mg", "generic_name": "Atorvastatin", "quantity": "10", "frequency": "once daily"}]
    ctx = AgentContext(matched_medicines=matched)

    assert await agent.can_handle(AgentEvent.ORDER_CONFIRMED, ctx) is True
    assert await agent.validate(ctx) is True

    result_ctx = await agent.execute(ctx)
    refill_meta = result_ctx.metadata["refill_report"]
    assert refill_meta["status"] in ("READY_FOR_REORDER", "MONITORING")
    assert refill_meta["evaluated_medicines"][0]["is_chronic"] is True


@pytest.mark.asyncio
async def test_notification_agent_unit():
    agent = NotificationAgent()
    ctx = AgentContext(
        metadata={
            "drug_safety": {"risk_level": "HIGH", "requires_pharmacist_review": True},
            "refill_report": {"requires_notification": True, "status": "READY_FOR_REORDER", "days_remaining": 3}
        }
    )

    assert await agent.can_handle(AgentEvent.ORDER_RECOMMENDED, ctx) is True
    assert await agent.validate(ctx) is True

    result_ctx = await agent.execute(ctx)
    notifications = result_ctx.metadata["notifications"]
    assert len(notifications) >= 2
    assert any(n["recipient"] == "pharmacist" and n["priority"] == "CRITICAL" for n in notifications)


@pytest.mark.asyncio
async def test_health_companion_agent_unit():
    agent = AIHealthCompanionAgent()
    ctx = AgentContext(
        metadata={"user_message": "Are there any interactions in my prescription?"}
    )

    assert await agent.can_handle(AgentEvent.AI_CHAT_REQUEST, ctx) is True
    assert await agent.validate(ctx) is True

    result_ctx = await agent.execute(ctx)
    resp = result_ctx.metadata["assistant_response"]
    assert resp["intent"] == "SAFETY_QUERY"
    assert "Disclaimer" in resp["disclaimer"]
