"""
Negative & Security Edge Case Tests for MediLoop Backend & AI Ecosystem.
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
    AgentExecutionError,
    AgentValidationError,
)


@pytest.mark.asyncio
async def test_ocr_agent_invalid_file_extension():
    agent = OCRAgent()
    invalid_ctx = AgentContext(uploaded_image="/uploads/malicious_payload.exe")
    
    with pytest.raises(AgentValidationError) as exc_info:
        await agent.validate(invalid_ctx)
    assert "Unsupported image extension" in str(exc_info.value)


@pytest.mark.asyncio
async def test_prescription_intelligence_empty_ocr_text():
    agent = PrescriptionIntelligenceAgent()
    empty_ctx = AgentContext(ocr_text="   ")
    
    with pytest.raises(AgentValidationError) as exc_info:
        await agent.validate(empty_ctx)
    assert "missing or empty" in str(exc_info.value)


@pytest.mark.asyncio
async def test_medicine_matching_unmatched_drug():
    agent = MedicineMatchingAgent()
    unmatched_ctx = AgentContext(extracted_medicines=[{"name": "UnknownNonExistentDrug123"}])
    
    result_ctx = await agent.execute(unmatched_ctx)
    matched = result_ctx.matched_medicines[0]
    assert matched["match_level"] == "UNMATCHED"
    assert matched["confidence"] == 0.0
    assert len(result_ctx.warnings) > 0


@pytest.mark.asyncio
async def test_drug_safety_penicillin_allergy_conflict():
    agent = DrugSafetyAgent()
    allergy_ctx = AgentContext(
        matched_medicines=[{"name": "Amoxil 500", "generic_name": "Amoxicillin"}],
        metadata={"user_allergies": ["Penicillin"]}
    )
    
    result_ctx = await agent.execute(allergy_ctx)
    safety_meta = result_ctx.metadata["drug_safety"]
    assert safety_meta["risk_level"] == "CRITICAL"
    assert safety_meta["requires_pharmacist_review"] is True
    assert safety_meta["errors"][0]["type"] == "ALLERGY_CONFLICT"


@pytest.mark.asyncio
async def test_inventory_agent_out_of_stock_item():
    agent = InventoryAvailabilityAgent()
    # Pharmacy ID 1 has 0 stock for Glucophage 500 (medicine_id 10)
    ctx = AgentContext(
        matched_medicines=[{"id": 10, "name": "Glucophage 500", "quantity": "10"}],
        pharmacy_id=1
    )
    
    result_ctx = await agent.execute(ctx)
    inv_meta = result_ctx.metadata["inventory"]
    assert inv_meta["overall_status"] == "UNAVAILABLE"
    assert inv_meta["complete_order"] is False
    assert len(inv_meta["unavailable_items"]) == 1
