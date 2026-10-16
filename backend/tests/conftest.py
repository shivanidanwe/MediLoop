"""
Pytest configuration and test fixtures for MediLoop Backend & AI Test Suite.
"""
import os
import sys
import pytest
import asyncio

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
)


@pytest.fixture(scope="session")
def event_loop():
    """Provides asyncio event loop for async test cases."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_agent_registry():
    """Registers all 10 AI Agents into a clean test registry."""
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
    return registry


@pytest.fixture
def test_workflow_engine(mock_agent_registry):
    """Provides initialized MultiAgentWorkflowEngine for integration testing."""
    return MultiAgentWorkflowEngine(mock_agent_registry)


@pytest.fixture
def sample_prescription_context():
    """Provides a standard populated AgentContext for prescription workflows."""
    return AgentContext(
        prescription_id="rx_test_100",
        user_id="usr_test_shivani",
        uploaded_image="/uploads/prescriptions/rx_scan.jpg",
        metadata={"user_allergies": []}
    )
