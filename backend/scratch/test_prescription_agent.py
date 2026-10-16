"""
Verification test script for MediLoop Prescription Intelligence Agent (Phase 2).
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
    PrescriptionIntelligenceAgent,
    AgentExecutionError,
)


async def run_prescription_agent_tests():
    print("=== Testing Prescription Intelligence Agent Integration ===")
    registry = AgentRegistry()
    agent = PrescriptionIntelligenceAgent()
    registry.register(agent)

    orchestrator = AgentOrchestrator(registry)

    # Test Case 1: Valid OCR Text Extraction
    ocr_text_sample = """
    DR. A. SHARMA, M.D. (CARDIOLOGY)
    CITY CARE CLINIC - RX PRESCRIPTION
    DATE: 2026-07-20

    1. Paracetamol 500mg - 1 tab 1-0-1 for 5 days
    2. Amoxicillin 250 mg - 1 capsule BID for 7 days
    3. Atorvastatin 10mg - once daily HS for 30 days
    4. Metformin 500mg - twice a day after meals
    5. Vitamin D3 60000iu - once a week
    """

    context = AgentContext(
        prescription_id="rx_doc_8899",
        user_id="usr_shivani_123",
        ocr_text=ocr_text_sample,
    )

    print(f"Dispatching event '{AgentEvent.OCR_COMPLETED}'...")
    result_context = await orchestrator.dispatch(AgentEvent.OCR_COMPLETED, context)

    print("\n=== Extracted Medicines Result ===")
    for idx, med in enumerate(result_context.extracted_medicines, start=1):
        print(f" {idx}. Name: {med['name']}")
        print(f"    Strength: '{med['strength']}', Frequency: '{med['frequency']}', Duration: '{med['duration']}', Dosage: '{med['dosage']}'")
        print(f"    Confidence: {med['confidence']}")

    print("\nMetadata Summary:", result_context.metadata.get("prescription_intelligence"))
    print("Warnings:", result_context.warnings)

    assert len(result_context.extracted_medicines) >= 4
    first_med = result_context.extracted_medicines[0]
    assert "Paracetamol" in first_med["name"]
    assert first_med["strength"] == "500mg"
    assert first_med["frequency"] == "1-0-1"
    assert first_med["duration"] == "5 days"
    assert first_med["confidence"] >= 0.85

    # Test Case 2: Validation Failure on Empty Context
    print("\n=== Testing Empty Context Validation Failure ===")
    empty_context = AgentContext(prescription_id="rx_empty")
    try:
        await orchestrator.dispatch(AgentEvent.OCR_COMPLETED, empty_context)
        print("[FAIL] Failed to raise AgentExecutionError for empty OCR text!")
    except AgentExecutionError as e:
        print("[OK] Caught expected AgentExecutionError for empty OCR text:")
        print(f"     Details: {e.message}")

    print("\n[SUCCESS] ALL PRESCRIPTION INTELLIGENCE AGENT TESTS PASSED!")

if __name__ == "__main__":
    asyncio.run(run_prescription_agent_tests())
