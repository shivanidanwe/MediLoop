"""
Verification test script for MediLoop AI Agent Orchestrator Phase 1.
"""
import asyncio
import os
import sys

# Ensure backend directory is in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.agents import (
    BaseAgent,
    AgentContext,
    AgentEvent,
    AgentRegistry,
    WorkflowManager,
    AgentOrchestrator,
    AgentValidationError,
    DuplicateAgentRegistrationError,
)

# --- Sample Test Agents ---
class DummyOCRAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "ocr_agent"

    @property
    def description(self) -> str:
        return "Extracts raw text from uploaded prescription scan images."

    @property
    def handled_events(self):
        return [AgentEvent.PRESCRIPTION_UPLOADED]

    async def can_handle(self, event: AgentEvent, context: AgentContext) -> bool:
        return event == AgentEvent.PRESCRIPTION_UPLOADED and context.uploaded_image is not None

    async def validate(self, context: AgentContext) -> bool:
        if not context.uploaded_image:
            raise AgentValidationError("Prescription scan image path is required.")
        return True

    async def execute(self, context: AgentContext) -> AgentContext:
        context.ocr_text = "Rx: Paracetamol 500mg - 1 tab twice daily for 5 days. Amoxicillin 250mg - 1 capsule thrice daily."
        context.extracted_medicines = [
            {"raw_name": "Paracetamol 500mg", "dosage": "500mg", "frequency": "1 tab twice daily"},
            {"raw_name": "Amoxicillin 250mg", "dosage": "250mg", "frequency": "1 capsule thrice daily"}
        ]
        context.add_recommendation("Verify antibiotic course duration with pharmacist.")
        return context


class DummyMedicineMatchingAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "matching_agent"

    @property
    def description(self) -> str:
        return "Matches extracted raw medicine names with pharmacy catalog inventory."

    @property
    def handled_events(self):
        return [AgentEvent.PRESCRIPTION_UPLOADED, AgentEvent.MEDICINES_EXTRACTED]

    async def can_handle(self, event: AgentEvent, context: AgentContext) -> bool:
        return len(context.extracted_medicines) > 0

    async def validate(self, context: AgentContext) -> bool:
        return len(context.extracted_medicines) > 0

    async def execute(self, context: AgentContext) -> AgentContext:
        context.matched_medicines = [
            {"id": "med_101", "name": "Crocin 500mg (Paracetamol)", "price": 45.0, "stock": 120},
            {"id": "med_202", "name": "Mox 250mg (Amoxicillin)", "price": 110.0, "stock": 45}
        ]
        return context


async def run_tests():
    print("=== Testing Agent Registry & Injection ===")
    registry = AgentRegistry()
    ocr_agent = DummyOCRAgent()
    matching_agent = DummyMedicineMatchingAgent()

    registry.register(ocr_agent)
    registry.register(matching_agent)

    print("Registered Agents:", registry.list_registered_agents())
    assert len(registry.list_registered_agents()) == 2

    # Verify duplicate registration prevention
    try:
        registry.register(ocr_agent)
        print("[FAIL] Duplicate registration failed to raise error!")
    except DuplicateAgentRegistrationError:
        print("[OK] Duplicate registration caught successfully!")

    print("\n=== Testing Agent Orchestrator Dispatch ===")
    orchestrator = AgentOrchestrator(registry)

    # Initial context with uploaded prescription image
    ctx = AgentContext(
        user_id="usr_shivani_123",
        uploaded_image="/uploads/prescriptions/rx_99.jpg"
    )

    print(f"Dispatching event '{AgentEvent.PRESCRIPTION_UPLOADED}'...")
    final_ctx = await orchestrator.dispatch(AgentEvent.PRESCRIPTION_UPLOADED, ctx)

    print("\n=== Execution Results ===")
    print("Request ID:", final_ctx.request_id)
    print("OCR Text:", final_ctx.ocr_text)
    print("Extracted Medicines Count:", len(final_ctx.extracted_medicines))
    print("Matched Inventory Items:", [m['name'] for m in final_ctx.matched_medicines])
    print("Recommendations:", final_ctx.recommendations)
    print("\nExecution History:")
    for step in final_ctx.execution_history:
        print(f" - [{step['agent_name']}] Status: {step['status']} ({step['duration_ms']}ms)")

    assert final_ctx.ocr_text is not None
    assert len(final_ctx.matched_medicines) == 2
    assert len(final_ctx.execution_history) == 2
    print("\n[SUCCESS] ALL ORCHESTRATOR TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run_tests())
