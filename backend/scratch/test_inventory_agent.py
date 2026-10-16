"""
Verification test script for MediLoop Inventory Availability Agent (Phase 6).
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
    AgentExecutionError,
)


async def run_inventory_agent_tests():
    print("=== Testing Inventory Availability Agent & 5-Agent Pipeline Integration ===")
    registry = AgentRegistry()

    ocr_agent = OCRAgent()
    rx_agent = PrescriptionIntelligenceAgent()
    matching_agent = MedicineMatchingAgent()
    safety_agent = DrugSafetyAgent()
    inventory_agent = InventoryAvailabilityAgent()

    registry.register(ocr_agent)
    registry.register(rx_agent)
    registry.register(matching_agent)
    registry.register(safety_agent)
    registry.register(inventory_agent)

    orchestrator = AgentOrchestrator(registry)

    # Test Case 1: 5-Agent Pipeline Execution (Uploaded Image -> OCR -> Rx -> Matching -> Safety -> Inventory)
    context = AgentContext(
        prescription_id="rx_inv_9090",
        user_id="usr_shivani_123",
        pharmacy_id=1,  # MediLoop Central Pharmacy (has 1 out of stock item: Glucophage 500)
        uploaded_image="/uploads/prescriptions/rx_scan.jpg",
    )

    print(f"Dispatching event '{AgentEvent.PRESCRIPTION_UPLOADED}'...")
    result_context = await orchestrator.dispatch(AgentEvent.PRESCRIPTION_UPLOADED, context)

    print("\n=== Inventory Analysis Report ===")
    inv_meta = result_context.metadata.get("inventory", {})
    print("Overall Status:", inv_meta.get("overall_status"))
    print("Complete Order:", inv_meta.get("complete_order"))
    print("Selected Pharmacy:", inv_meta.get("selected_pharmacy", {}).get("name"))
    print("Unavailable Items Count:", len(inv_meta.get("unavailable_items", [])))

    print("\nItem Status Breakdown:")
    for item in inv_meta.get("items", []):
        print(f" - Item: {item['name']} | Status: {item['status']} | Available: {item['available_quantity']}/{item['requested_quantity']}")

    print("\nRanked Alternative Pharmacies:")
    for alt in inv_meta.get("alternative_pharmacies", []):
        print(f" - Pharmacy: {alt['pharmacy_name']} | Fulfillment: {alt['fulfillment_percentage']}% | Rating: {alt['rating']}")

    print("\nExecution History:")
    for step in result_context.execution_history:
        print(f" - [{step['agent_name']}] Status: {step['status']} ({step['duration_ms']}ms)")

    assert len(result_context.execution_history) == 5
    assert result_context.execution_history[4]["agent_name"] == "inventory_availability_agent"
    assert inv_meta.get("overall_status") == "PARTIAL_FULFILLMENT"
    assert len(inv_meta.get("alternative_pharmacies", [])) > 0
    # Top alternative pharmacy (Apollo Pharmacy) should offer 100% fulfillment
    assert inv_meta.get("alternative_pharmacies")[0]["fulfillment_percentage"] == 100.0

    # Test Case 2: Validation Failure on Empty Context
    print("\n=== Testing Empty Context Validation Failure ===")
    empty_ctx = AgentContext()
    try:
        await orchestrator.dispatch(AgentEvent.SAFETY_VALIDATION_COMPLETED, empty_ctx)
        print("[FAIL] Failed to raise error for empty context!")
    except AgentExecutionError as e:
        print("[OK] Caught expected AgentExecutionError for empty context:")
        print(f"     Details: {e.message}")

    print("\n[SUCCESS] ALL INVENTORY AVAILABILITY AGENT TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run_inventory_agent_tests())
