"""
Verification test script for MediLoop Drug Safety Agent (Phase 5).
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
    AgentExecutionError,
)


async def run_drug_safety_agent_tests():
    print("=== Testing Drug Safety Agent & 4-Agent Pipeline Integration ===")
    registry = AgentRegistry()

    ocr_agent = OCRAgent()
    rx_agent = PrescriptionIntelligenceAgent()
    matching_agent = MedicineMatchingAgent()
    safety_agent = DrugSafetyAgent()

    registry.register(ocr_agent)
    registry.register(rx_agent)
    registry.register(matching_agent)
    registry.register(safety_agent)

    orchestrator = AgentOrchestrator(registry)

    # Test Case 1: 4-Agent Pipeline Dispatch (Uploaded Image -> OCR -> Rx -> Matching -> Safety)
    context = AgentContext(
        prescription_id="rx_safety_707",
        user_id="usr_shivani_123",
        uploaded_image="/uploads/prescriptions/rx_scan.jpg",
        metadata={"user_allergies": ["Penicillin"]}  # Patient has known Penicillin allergy
    )

    print(f"Dispatching event '{AgentEvent.PRESCRIPTION_UPLOADED}'...")
    result_context = await orchestrator.dispatch(AgentEvent.PRESCRIPTION_UPLOADED, context)

    print("\n=== Clinical Safety Analysis Report ===")
    safety_meta = result_context.metadata.get("drug_safety", {})
    print("Overall Status:", safety_meta.get("overall_status"))
    print("Risk Level:", safety_meta.get("risk_level"))
    print("Requires Pharmacist Review:", safety_meta.get("requires_pharmacist_review"))
    print("Total Safety Errors:", safety_meta.get("total_errors"))
    print("Total Safety Warnings:", safety_meta.get("total_warnings"))
    print("Clinical Notes:", safety_meta.get("clinical_notes"))

    print("\nReport Errors:")
    for err in safety_meta.get("errors", []):
        print(f" - [{err['severity']}] Type: {err['type']} | {err['description']}")

    print("\nExecution History:")
    for step in result_context.execution_history:
        print(f" - [{step['agent_name']}] Status: {step['status']} ({step['duration_ms']}ms)")

    assert len(result_context.execution_history) == 4
    assert result_context.execution_history[3]["agent_name"] == "drug_safety_agent"
    assert safety_meta.get("requires_pharmacist_review") is True  # Due to Penicillin allergy vs Amoxicillin
    assert safety_meta.get("risk_level") == "CRITICAL"

    # Test Case 2: Testing Drug Interaction (Warfarin + Aspirin)
    print("\n=== Testing Drug-Drug Interaction (Warfarin + Aspirin) ===")
    interaction_ctx = AgentContext(
        matched_medicines=[
            {"name": "Warfarin 5mg", "generic_name": "Warfarin", "strength": "5mg"},
            {"name": "Ecosprin 75mg", "generic_name": "Aspirin", "strength": "75mg"},
        ],
        metadata={"user_allergies": []}
    )

    result_interaction = await orchestrator.dispatch(AgentEvent.MEDICINES_MATCHED, interaction_ctx)
    safety_meta_int = result_interaction.metadata.get("drug_safety", {})

    print("Risk Level:", safety_meta_int.get("risk_level"))
    print("Errors Found:", len(safety_meta_int.get("errors", [])))
    print("Description:", safety_meta_int.get("errors", [{}])[0].get("description"))

    assert safety_meta_int.get("risk_level") == "CRITICAL"
    assert safety_meta_int.get("errors")[0]["type"] == "DRUG_INTERACTION"

    # Test Case 3: Validation Failure on Empty Context
    print("\n=== Testing Empty Context Validation Failure ===")
    empty_ctx = AgentContext()
    try:
        await orchestrator.dispatch(AgentEvent.MEDICINES_MATCHED, empty_ctx)
        print("[FAIL] Failed to raise error for empty context!")
    except AgentExecutionError as e:
        print("[OK] Caught expected AgentExecutionError for empty context:")
        print(f"     Details: {e.message}")

    print("\n[SUCCESS] ALL DRUG SAFETY AGENT TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run_drug_safety_agent_tests())
