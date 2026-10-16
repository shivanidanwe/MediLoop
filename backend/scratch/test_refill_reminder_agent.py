"""
Verification test script for MediLoop Refill Reminder Agent (Phase 8).
"""
import asyncio
import os
import sys

# Ensure backend directory is in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.agents import (
    AgentContext,
    AgentEvent,
    AgentRegistry,
    AgentOrchestrator,
    OCRAgent,
    PrescriptionIntelligenceAgent,
    MedicineMatchingAgent,
    DrugSafetyAgent,
    InventoryAvailabilityAgent,
    OrderRecommendationAgent,
    RefillReminderAgent,
    AgentExecutionError,
)


async def run_refill_reminder_agent_tests():
    print("=== Testing Refill Reminder Agent & 7-Agent Pipeline Integration ===")
    registry = AgentRegistry()

    ocr_agent = OCRAgent()
    rx_agent = PrescriptionIntelligenceAgent()
    matching_agent = MedicineMatchingAgent()
    safety_agent = DrugSafetyAgent()
    inventory_agent = InventoryAvailabilityAgent()
    recommendation_agent = OrderRecommendationAgent()
    refill_agent = RefillReminderAgent(reminder_window_days=5)

    registry.register(ocr_agent)
    registry.register(rx_agent)
    registry.register(matching_agent)
    registry.register(safety_agent)
    registry.register(inventory_agent)
    registry.register(recommendation_agent)
    registry.register(refill_agent)

    orchestrator = AgentOrchestrator(registry)

    # Test Case 1: 7-Agent Pipeline Dispatch (Uploaded Image -> OCR -> Rx -> Matching -> Safety -> Inventory -> Recommendation -> Refill)
    context = AgentContext(
        prescription_id="rx_refill_3030",
        user_id="usr_shivani_123",
        uploaded_image="/uploads/prescriptions/rx_scan.jpg",
        metadata={"user_allergies": []}
    )

    print(f"Dispatching event '{AgentEvent.PRESCRIPTION_UPLOADED}'...")
    result_context = await orchestrator.dispatch(AgentEvent.PRESCRIPTION_UPLOADED, context)

    print("\n=== Refill Adherence Report ===")
    refill_meta = result_context.metadata.get("refill_report", {})
    print("Status:", refill_meta.get("status"))
    print("Risk Level:", refill_meta.get("risk_level"))
    print("Days Remaining:", refill_meta.get("days_remaining"))
    print("Expected Completion Date:", refill_meta.get("expected_completion_date"))
    print("Recommended Reminder Date:", refill_meta.get("recommended_reminder_date"))
    print("Requires Notification:", refill_meta.get("requires_notification"))

    print("\nEvaluated Medicines Detail:")
    for med in refill_meta.get("evaluated_medicines", []):
        print(f" - [{med['status']}] '{med['medicine_name']}' ({med['generic_name']}) | Supply: {med['supply_days']}d | Chronic: {med['is_chronic']} | Risk: {med['risk_level']}")

    print("\nExecution History:")
    for step in result_context.execution_history:
        print(f" - [{step['agent_name']}] Status: {step['status']} ({step['duration_ms']}ms)")

    assert len(result_context.execution_history) == 7
    assert result_context.execution_history[6]["agent_name"] == "refill_reminder_agent"
    assert refill_meta.get("status") in ("READY_FOR_REORDER", "MONITORING")
    assert len(refill_meta.get("evaluated_medicines", [])) >= 4

    # Test Case 2: Validation Failure on Empty Context
    print("\n=== Testing Empty Context Validation Failure ===")
    empty_ctx = AgentContext()
    try:
        await orchestrator.dispatch(AgentEvent.REFILL_REMINDER, empty_ctx)
        print("[FAIL] Failed to raise error for empty context!")
    except AgentExecutionError as e:
        print("[OK] Caught expected AgentExecutionError for empty context:")
        print(f"     Details: {e.message}")

    print("\n[SUCCESS] ALL REFILL REMINDER AGENT TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run_refill_reminder_agent_tests())
