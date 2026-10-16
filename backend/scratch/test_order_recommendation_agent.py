"""
Verification test script for MediLoop Order Recommendation Agent (Phase 7).
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
    AgentExecutionError,
)


async def run_order_recommendation_agent_tests():
    print("=== Testing Order Recommendation Agent & 6-Agent End-to-End Pipeline Integration ===")
    registry = AgentRegistry()

    ocr_agent = OCRAgent()
    rx_agent = PrescriptionIntelligenceAgent()
    matching_agent = MedicineMatchingAgent()
    safety_agent = DrugSafetyAgent()
    inventory_agent = InventoryAvailabilityAgent()
    recommendation_agent = OrderRecommendationAgent()

    registry.register(ocr_agent)
    registry.register(rx_agent)
    registry.register(matching_agent)
    registry.register(safety_agent)
    registry.register(inventory_agent)
    registry.register(recommendation_agent)

    orchestrator = AgentOrchestrator(registry)

    # Test Case 1: 6-Agent Pipeline Dispatch (Uploaded Image -> OCR -> Rx -> Matching -> Safety -> Inventory -> Recommendation)
    context = AgentContext(
        prescription_id="rx_order_1010",
        user_id="usr_shivani_123",
        pharmacy_id=1,  # MediLoop Central Pharmacy (has 1 out of stock item: Glucophage 500)
        uploaded_image="/uploads/prescriptions/rx_scan.jpg",
        metadata={"user_allergies": ["Penicillin"]}  # Patient has known Penicillin allergy
    )

    print(f"Dispatching event '{AgentEvent.PRESCRIPTION_UPLOADED}'...")
    result_context = await orchestrator.dispatch(AgentEvent.PRESCRIPTION_UPLOADED, context)

    print("\n=== AI Order Recommendation Strategy Report ===")
    rec_meta = result_context.metadata.get("order_recommendation", {})
    print("Order Status:", rec_meta.get("order_status"))
    print("Recommended Pharmacy:", rec_meta.get("recommended_pharmacy", {}).get("name"))
    print("Recommendation Confidence:", rec_meta.get("recommendation_confidence"))
    print("Requires Pharmacist Review:", rec_meta.get("requires_pharmacist_review"))

    print("\nDecision Reasoning Points:")
    for point in rec_meta.get("reasoning", []):
        print(f" - {point}")

    print("\nExecution History:")
    for step in result_context.execution_history:
        print(f" - [{step['agent_name']}] Status: {step['status']} ({step['duration_ms']}ms)")

    assert len(result_context.execution_history) == 6
    assert result_context.execution_history[5]["agent_name"] == "order_recommendation_agent"
    assert rec_meta.get("recommended_pharmacy", {}).get("name") == "Apollo Pharmacy - Express Branch"
    assert rec_meta.get("requires_pharmacist_review") is True
    assert rec_meta.get("order_status") == "REQUIRES_PHARMACIST_REVIEW"

    # Test Case 2: Clean Prescription Execution (No Allergies -> READY_FOR_CHECKOUT)
    print("\n=== Testing Clean Prescription Execution (READY_FOR_CHECKOUT) ===")
    clean_ctx = AgentContext(
        prescription_id="rx_clean_2020",
        uploaded_image="/uploads/prescriptions/rx_scan.jpg",
        metadata={"user_allergies": []}  # No allergies
    )
    clean_res = await orchestrator.dispatch(AgentEvent.PRESCRIPTION_UPLOADED, clean_ctx)
    clean_rec = clean_res.metadata.get("order_recommendation", {})

    print("Order Status:", clean_rec.get("order_status"))
    print("Recommended Pharmacy:", clean_rec.get("recommended_pharmacy", {}).get("name"))
    print("Confidence:", clean_rec.get("recommendation_confidence"))

    assert clean_rec.get("order_status") == "READY_FOR_CHECKOUT"
    assert clean_rec.get("requires_pharmacist_review") is False

    # Test Case 3: Validation Failure on Empty Context
    print("\n=== Testing Empty Context Validation Failure ===")
    empty_ctx = AgentContext()
    try:
        await orchestrator.dispatch(AgentEvent.INVENTORY_CHECKED, empty_ctx)
        print("[FAIL] Failed to raise error for empty context!")
    except AgentExecutionError as e:
        print("[OK] Caught expected AgentExecutionError for empty context:")
        print(f"     Details: {e.message}")

    print("\n[SUCCESS] ALL ORDER RECOMMENDATION AGENT TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run_order_recommendation_agent_tests())
