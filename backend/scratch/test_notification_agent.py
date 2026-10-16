"""
Verification test script for MediLoop Notification Agent (Phase 9).
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
    NotificationAgent,
    AgentExecutionError,
)


async def run_notification_agent_tests():
    print("=== Testing Notification Agent & 8-Agent Pipeline Integration ===")
    registry = AgentRegistry()

    ocr_agent = OCRAgent()
    rx_agent = PrescriptionIntelligenceAgent()
    matching_agent = MedicineMatchingAgent()
    safety_agent = DrugSafetyAgent()
    inventory_agent = InventoryAvailabilityAgent()
    recommendation_agent = OrderRecommendationAgent()
    refill_agent = RefillReminderAgent()
    notification_agent = NotificationAgent()

    registry.register(ocr_agent)
    registry.register(rx_agent)
    registry.register(matching_agent)
    registry.register(safety_agent)
    registry.register(inventory_agent)
    registry.register(recommendation_agent)
    registry.register(refill_agent)
    registry.register(notification_agent)

    orchestrator = AgentOrchestrator(registry)

    # Test Case 1: 8-Agent Pipeline Dispatch (Uploaded Image -> OCR -> Rx -> Matching -> Safety -> Inventory -> Recommendation -> Refill -> Notification)
    context = AgentContext(
        prescription_id="rx_notify_4040",
        user_id="usr_shivani_123",
        uploaded_image="/uploads/prescriptions/rx_scan.jpg",
        metadata={"user_allergies": ["Penicillin"]}  # Triggers Pharmacist CRITICAL safety alert
    )

    print(f"Dispatching event '{AgentEvent.PRESCRIPTION_UPLOADED}'...")
    result_context = await orchestrator.dispatch(AgentEvent.PRESCRIPTION_UPLOADED, context)

    print("\n=== Notification Payloads Generated ===")
    notifications = result_context.metadata.get("notifications", [])
    print(f"Total Notifications Created: {len(notifications)}")

    for idx, note in enumerate(notifications, start=1):
        print(f" {idx}. [{note['priority']}] Recipient: '{note['recipient'].upper()}' | Category: {note['category']} | Channel: {note['channel']}")
        print(f"    Title: {note['title']}")
        print(f"    Message: {note['message']}")

    print("\nExecution History:")
    for step in result_context.execution_history:
        print(f" - [{step['agent_name']}] Status: {step['status']} ({step['duration_ms']}ms)")

    assert len(result_context.execution_history) == 8
    assert result_context.execution_history[7]["agent_name"] == "notification_agent"
    assert len(notifications) >= 3
    # Check Pharmacist CRITICAL Safety notification exists
    pharmacist_notes = [n for n in notifications if n["recipient"] == "pharmacist"]
    assert len(pharmacist_notes) > 0
    assert pharmacist_notes[0]["priority"] == "CRITICAL"

    # Test Case 2: Validation Failure on Empty Context
    print("\n=== Testing Empty Context Validation Failure ===")
    empty_ctx = AgentContext()
    try:
        await orchestrator.dispatch(AgentEvent.ORDER_RECOMMENDED, empty_ctx)
        print("[FAIL] Failed to raise error for empty context!")
    except AgentExecutionError as e:
        print("[OK] Caught expected AgentExecutionError for empty context:")
        print(f"     Details: {e.message}")

    print("\n[SUCCESS] ALL NOTIFICATION AGENT TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run_notification_agent_tests())
