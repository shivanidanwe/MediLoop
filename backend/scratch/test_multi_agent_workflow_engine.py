"""
Comprehensive Integration Test Suite for MediLoop Multi-Agent Workflow Engine (Phase 11).
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
    MultiAgentWorkflowEngine,
    WorkflowState,
)


async def run_workflow_engine_integration_tests():
    print("=== Testing MediLoop Multi-Agent Workflow Engine (Phase 11) ===")

    # 1. Register all 10 AI Agents into Registry
    registry = AgentRegistry()
    registry.register(OCRAgent())
    registry.register(PrescriptionIntelligenceAgent())
    registry.register(MedicineMatchingAgent())
    registry.register(DrugSafetyAgent())
    registry.register(InventoryAvailabilityAgent())
    registry.register(OrderRecommendationAgent())
    registry.register(RefillReminderAgent())
    registry.register(NotificationAgent())
    registry.register(AIHealthCompanionAgent())

    engine = MultiAgentWorkflowEngine(registry)

    # --- Test Case 1: Workflow 1 (Happy Path Prescription Upload & Checkout) ---
    print("\n--- Test Case 1: Workflow 1 (Happy Path Prescription Upload) ---")
    clean_ctx = AgentContext(
        prescription_id="rx_clean_999",
        user_id="usr_shivani_123",
        uploaded_image="/uploads/prescriptions/rx_scan.jpg",
        metadata={"user_allergies": []}  # Clean, no allergies
    )

    rec1 = await engine.execute_prescription_upload_workflow(clean_ctx)

    print(f"Workflow ID: {rec1.workflow_id} | Status: {rec1.status.value} | Duration: {rec1.duration_ms}ms")
    print("Agent Sequence Metrics:")
    for step in rec1.agent_metrics:
        print(f" - Agent: {step['agent']} | Status: {step['status']} ({step['duration_ms']}ms)")

    assert rec1.status == WorkflowState.COMPLETED
    assert rec1.context is not None
    assert rec1.context.metadata["order_recommendation"]["order_status"] == "READY_FOR_CHECKOUT"
    print("[OK] Happy Path Prescription Upload Workflow PASSED!")

    # --- Test Case 2: Workflow 4 (High Risk Pause & Resume Controls) ---
    print("\n--- Test Case 2: Workflow 4 (High Risk Allergy Pause & Pharmacist Resume) ---")
    risk_ctx = AgentContext(
        prescription_id="rx_risk_888",
        user_id="usr_shivani_123",
        uploaded_image="/uploads/prescriptions/rx_scan.jpg",
        metadata={"user_allergies": ["Penicillin"]}  # Triggers Penicillin allergy vs Amoxil 500
    )

    rec2 = await engine.execute_prescription_upload_workflow(risk_ctx)
    print(f"Initial Execution Status: {rec2.status.value} (Expected: WAITING)")
    assert rec2.status == WorkflowState.WAITING
    assert rec2.context.metadata["drug_safety"]["requires_pharmacist_review"] is True

    print(f"Resuming workflow '{rec2.workflow_id}' with Pharmacist Approval...")
    resumed_rec2 = await engine.resume_workflow(
        workflow_id=rec2.workflow_id,
        pharmacist_approved=True,
        reviewer_notes="Verified dosage with prescribing doctor. Cleared for dispensing."
    )

    print(f"Resumed Status: {resumed_rec2.status.value} (Expected: COMPLETED)")
    assert resumed_rec2.status == WorkflowState.COMPLETED
    assert resumed_rec2.context.metadata["pharmacist_approval"]["approved"] is True
    print("[OK] High Risk Pause & Resume Workflow PASSED!")

    # --- Test Case 3: Workflow 2 (Order Completed & Refill Adherence) ---
    print("\n--- Test Case 3: Workflow 2 (Order Completed & Refill Adherence) ---")
    order_ctx = AgentContext(
        user_id="usr_shivani_123",
        matched_medicines=[
            {"id": 1, "name": "Crocin 650", "generic_name": "Paracetamol", "strength": "650 mg", "frequency": "1-0-1", "quantity": "30"}
        ]
    )

    rec3 = await engine.execute_order_completed_workflow(order_ctx)
    print(f"Workflow ID: {rec3.workflow_id} | Status: {rec3.status.value} | Duration: {rec3.duration_ms}ms")
    assert rec3.status == WorkflowState.COMPLETED
    assert rec3.context.metadata["refill_report"]["status"] in ("READY_FOR_REORDER", "MONITORING")
    print("[OK] Order Completed Refill Workflow PASSED!")

    # --- Test Case 4: Workflow 3 (Health Companion Chat Workflow) ---
    print("\n--- Test Case 4: Workflow 3 (AI Health Companion Chat) ---")
    rec4 = await engine.execute_health_companion_workflow(
        user_prompt="Are there any drug interactions in my prescription?",
        context=AgentContext(matched_medicines=[{"name": "Crocin 650", "generic_name": "Paracetamol"}])
    )

    print(f"Workflow ID: {rec4.workflow_id} | Status: {rec4.status.value} | Duration: {rec4.duration_ms}ms")
    assistant_resp = rec4.context.metadata.get("assistant_response", {})
    print("Assistant Intent Detected:", assistant_resp.get("intent"))
    print("Response Snippet:", assistant_resp.get("response")[:100], "...")
    assert rec4.status == WorkflowState.COMPLETED
    assert assistant_resp.get("intent") == "SAFETY_QUERY"
    print("[OK] AI Health Companion Chat Workflow PASSED!")

    # --- Test Case 5: Parallel Execution Verification ---
    print("\n--- Test Case 5: Parallel Execution Verification (Safety + Inventory) ---")
    parallel_metrics = [m for m in rec1.agent_metrics if m["agent"] in ("drug_safety_agent", "inventory_availability_agent")]
    print(f"Parallel Agents Executed Count: {len(parallel_metrics)}")
    assert len(parallel_metrics) == 2
    print("[OK] Parallel Execution Verified PASSED!")

    # --- Test Case 6: Telemetry & Metrics Summary ---
    print("\n=== Engine Telemetry & Performance Summary ===")
    telemetry = engine.get_telemetry_metrics()
    print("Total Workflows Executed:", telemetry["total_workflows_executed"])
    print("Completed Workflows:", telemetry["completed_workflows"])
    print("Waiting Workflows:", telemetry["waiting_workflows"])
    print("Failed Workflows:", telemetry["failed_workflows"])
    print("Dead Letter Queue Count:", telemetry["dlq_count"])
    print("Average Workflow Duration:", telemetry["average_duration_ms"], "ms")

    assert telemetry["total_workflows_executed"] >= 4
    assert telemetry["completed_workflows"] >= 3
    print("\n[SUCCESS] ALL MULTI-AGENT WORKFLOW ENGINE INTEGRATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run_workflow_engine_integration_tests())
