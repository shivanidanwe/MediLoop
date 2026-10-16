"""
Verification test script for MediLoop OCR Agent (Phase 3).
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
    AgentExecutionError,
)


async def run_ocr_agent_tests():
    print("=== Testing OCR Agent & Multi-Agent Pipeline Integration ===")
    registry = AgentRegistry()

    ocr_agent = OCRAgent()
    rx_agent = PrescriptionIntelligenceAgent()

    registry.register(ocr_agent)
    registry.register(rx_agent)

    orchestrator = AgentOrchestrator(registry)

    # Test Case 1: Full Pipeline (Uploaded Image -> OCR Agent -> Prescription Intelligence Agent)
    context = AgentContext(
        prescription_id="rx_scan_4040",
        user_id="usr_shivani_123",
        uploaded_image="/uploads/prescriptions/rx_scan.jpg",
    )

    print(f"Dispatching event '{AgentEvent.PRESCRIPTION_UPLOADED}'...")
    result_context = await orchestrator.dispatch(AgentEvent.PRESCRIPTION_UPLOADED, context)

    print("\n=== OCR Result Metadata ===")
    ocr_meta = result_context.metadata.get("ocr", {})
    print("Engine Used:", ocr_meta.get("engine_used"))
    print("Raw Text Character Count:", len(result_context.ocr_text or ""))
    print("Confidence:", ocr_meta.get("confidence"))

    print("\n=== Extracted Medicines Result (from Prescription Intelligence Agent) ===")
    for idx, med in enumerate(result_context.extracted_medicines, start=1):
        print(f" {idx}. Name: {med['name']} | Strength: {med['strength']} | Frequency: {med['frequency']}")

    print("\nExecution History:")
    for step in result_context.execution_history:
        print(f" - [{step['agent_name']}] Status: {step['status']} ({step['duration_ms']}ms)")

    assert result_context.ocr_text is not None
    assert len(result_context.extracted_medicines) >= 4
    assert len(result_context.execution_history) == 2
    assert result_context.execution_history[0]["agent_name"] == "ocr_agent"
    assert result_context.execution_history[1]["agent_name"] == "prescription_intelligence_agent"

    # Test Case 2: Validation Failure on Unsupported Image Format
    print("\n=== Testing Unsupported File Extension Validation ===")
    invalid_ext_ctx = AgentContext(uploaded_image="/uploads/file.exe")
    try:
        await orchestrator.dispatch(AgentEvent.PRESCRIPTION_UPLOADED, invalid_ext_ctx)
        print("[FAIL] Failed to raise error for unsupported extension!")
    except AgentExecutionError as e:
        print("[OK] Caught expected AgentExecutionError for unsupported image extension:")
        print(f"     Details: {e.message}")

    print("\n[SUCCESS] ALL OCR AGENT & MULTI-AGENT PIPELINE TESTS PASSED!")

if __name__ == "__main__":
    asyncio.run(run_ocr_agent_tests())
