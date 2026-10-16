"""
Verification test script for MediLoop Medicine Matching Agent (Phase 4).
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
    AgentExecutionError,
)


async def run_medicine_matching_agent_tests():
    print("=== Testing Medicine Matching Agent & 3-Agent Pipeline Integration ===")
    registry = AgentRegistry()

    ocr_agent = OCRAgent()
    rx_agent = PrescriptionIntelligenceAgent()
    matching_agent = MedicineMatchingAgent()

    registry.register(ocr_agent)
    registry.register(rx_agent)
    registry.register(matching_agent)

    orchestrator = AgentOrchestrator(registry)

    # Test Case 1: 3-Agent Pipeline Execution (Uploaded Image -> OCR -> Rx Agent -> Matching Agent)
    context = AgentContext(
        prescription_id="rx_scan_88",
        user_id="usr_shivani_123",
        uploaded_image="/uploads/prescriptions/rx_scan.jpg",
    )

    print(f"Dispatching event '{AgentEvent.PRESCRIPTION_UPLOADED}'...")
    result_context = await orchestrator.dispatch(AgentEvent.PRESCRIPTION_UPLOADED, context)

    print("\n=== Matched Medicines Results ===")
    for idx, med in enumerate(result_context.matched_medicines, start=1):
        print(f" {idx}. Brand Name: '{med['name']}' | Generic: '{med['generic_name']}'")
        print(f"    Strength: '{med['strength']}' | Price: Rs.{med['price']} | Confidence: {med['confidence']}")
        print(f"    Match Level: '{med['match_level']}'")
        if med.get("alternatives"):
            alt_names = [a["name"] for a in med["alternatives"]]
            print(f"    Suggested Alternatives: {alt_names}")

    print("\nMatching Summary Metadata:", result_context.metadata.get("medicine_matching"))

    print("\nExecution History:")
    for step in result_context.execution_history:
        print(f" - [{step['agent_name']}] Status: {step['status']} ({step['duration_ms']}ms)")

    assert len(result_context.matched_medicines) >= 4
    assert len(result_context.execution_history) == 3
    assert result_context.execution_history[0]["agent_name"] == "ocr_agent"
    assert result_context.execution_history[1]["agent_name"] == "prescription_intelligence_agent"
    assert result_context.execution_history[2]["agent_name"] == "medicine_matching_agent"

    # Test Case 2: Standalone Brand/Abbreviation/Fuzzy Match Testing
    print("\n=== Testing Standalone Multi-Level Matching ===")
    test_extracted = [
        {"name": "Crocin 650", "strength": "650mg", "dosage": "1 tab"},
        {"name": "PCM", "strength": "500mg", "dosage": "1 tab"},
        {"name": "Amoxycillin", "strength": "250mg", "dosage": "1 cap"},
        {"name": "Lipitor", "strength": "10mg", "dosage": "1 tab"},
        {"name": "UnknownXYZDrug", "strength": "100mg", "dosage": "1 tab"},
    ]

    direct_ctx = AgentContext(extracted_medicines=test_extracted)
    matched_ctx = await orchestrator.dispatch(AgentEvent.MEDICINES_EXTRACTED, direct_ctx)

    print("\nDirect Extraction Matching Results:")
    for idx, med in enumerate(matched_ctx.matched_medicines, start=1):
        print(f" {idx}. Raw: '{test_extracted[idx-1]['name']}' -> Matched: '{med['name']}' (Generic: {med['generic_name']}) | Level: {med['match_level']} | Conf: {med['confidence']}")

    assert matched_ctx.matched_medicines[0]["name"] == "Crocin 650"  # Exact
    assert matched_ctx.matched_medicines[1]["generic_name"] == "Paracetamol"  # Abbrev PCM -> Paracetamol
    assert matched_ctx.matched_medicines[2]["generic_name"] == "Amoxicillin"  # Fuzzy Amoxycillin -> Amoxicillin
    assert matched_ctx.matched_medicines[3]["generic_name"] == "Atorvastatin"  # Brand Lipitor -> Atorvastatin
    assert matched_ctx.matched_medicines[4]["match_level"] == "UNMATCHED"  # Unmatched

    # Test Case 3: Empty extracted_medicines validation
    print("\n=== Testing Empty extracted_medicines Validation Failure ===")
    empty_ctx = AgentContext(extracted_medicines=[])
    try:
        await orchestrator.dispatch(AgentEvent.MEDICINES_EXTRACTED, empty_ctx)
        print("[FAIL] Failed to raise error for empty extracted_medicines!")
    except AgentExecutionError as e:
        print("[OK] Caught expected AgentExecutionError for empty extracted_medicines:")
        print(f"     Details: {e.message}")

    print("\n[SUCCESS] ALL MEDICINE MATCHING AGENT TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run_medicine_matching_agent_tests())
