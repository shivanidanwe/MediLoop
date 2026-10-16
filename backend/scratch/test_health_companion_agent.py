"""
Verification test script for MediLoop AI Health Companion Agent (Phase 10).
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
    AIHealthCompanionAgent,
)


async def run_health_companion_agent_tests():
    print("=== Testing AI Health Companion Agent & Full 9-Agent Pipeline Integration ===")
    registry = AgentRegistry()

    ocr_agent = OCRAgent()
    rx_agent = PrescriptionIntelligenceAgent()
    matching_agent = MedicineMatchingAgent()
    safety_agent = DrugSafetyAgent()
    inventory_agent = InventoryAvailabilityAgent()
    recommendation_agent = OrderRecommendationAgent()
    refill_agent = RefillReminderAgent()
    notification_agent = NotificationAgent()
    companion_agent = AIHealthCompanionAgent()

    registry.register(ocr_agent)
    registry.register(rx_agent)
    registry.register(matching_agent)
    registry.register(safety_agent)
    registry.register(inventory_agent)
    registry.register(recommendation_agent)
    registry.register(refill_agent)
    registry.register(notification_agent)
    registry.register(companion_agent)

    orchestrator = AgentOrchestrator(registry)

    # Test Case 1: Full 9-Agent Orchestration Pipeline on Prescription Upload
    context = AgentContext(
        prescription_id="rx_companion_5050",
        user_id="usr_shivani_123",
        uploaded_image="/uploads/prescriptions/rx_scan.jpg",
        metadata={"user_message": "Can you analyze my prescription scan and recommend an order?"}
    )

    print(f"Dispatching event '{AgentEvent.PRESCRIPTION_UPLOADED}'...")
    result_context = await orchestrator.dispatch(AgentEvent.PRESCRIPTION_UPLOADED, context)

    print("\n=== Conversational Assistant Response ===")
    resp_meta = result_context.metadata.get("assistant_response", {})
    print("Detected Intent:", resp_meta.get("intent"))
    print("Agents Used:", resp_meta.get("agents_used"))
    print("Suggested Actions:", resp_meta.get("suggested_actions"))
    print("\nNatural Language Response:")
    print(resp_meta.get("response"))

    print("\nConversation History Memory Length:", len(result_context.metadata.get("conversation_history", [])))

    print("\nExecution History:")
    for step in result_context.execution_history:
        print(f" - [{step['agent_name']}] Status: {step['status']} ({step['duration_ms']}ms)")

    assert len(result_context.execution_history) == 9
    assert result_context.execution_history[8]["agent_name"] == "health_companion_agent"
    assert resp_meta.get("intent") == "PRESCRIPTION_ASSISTANCE"
    assert len(resp_meta.get("agents_used", [])) >= 3
    assert "Disclaimer" in resp_meta.get("disclaimer", "")

    # Test Case 2: Standalone Conversational Safety Query
    print("\n=== Testing Conversational Safety Query Intent ===")
    safety_chat_ctx = AgentContext(
        user_id="usr_shivani_123",
        metadata={
            "user_message": "Is Paracetamol safe to take with Aspirin?",
            "drug_safety": {"risk_level": "MEDIUM", "errors": [], "requires_pharmacist_review": False}
        }
    )
    result_safety_chat = await orchestrator.dispatch(AgentEvent.AI_CHAT_REQUEST, safety_chat_ctx)
    safety_resp = result_safety_chat.metadata.get("assistant_response", {})

    print("Detected Intent:", safety_resp.get("intent"))
    print("Response Snippet:", safety_resp.get("response")[:120], "...")
    assert safety_resp.get("intent") == "SAFETY_QUERY"

    print("\n[SUCCESS] ALL AI HEALTH COMPANION AGENT TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run_health_companion_agent_tests())
