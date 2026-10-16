"""
MediLoop Agent Factory.
Instantiates and registers all 10 specialized AI agents into the MultiAgentWorkflowEngine.
"""
from typing import Optional
from app.agents.registry import AgentRegistry
from app.agents.workflow_engine import MultiAgentWorkflowEngine

from app.agents.ocr_agent import OCRAgent
from app.agents.prescription_agent import PrescriptionIntelligenceAgent
from app.agents.medicine_matching_agent import MedicineMatchingAgent
from app.agents.drug_safety_agent import DrugSafetyAgent
from app.agents.inventory_agent import InventoryAvailabilityAgent
from app.agents.order_recommendation_agent import OrderRecommendationAgent
from app.agents.refill_reminder_agent import RefillReminderAgent
from app.agents.notification_agent import NotificationAgent
from app.agents.health_companion_agent import AIHealthCompanionAgent

_engine_instance: Optional[MultiAgentWorkflowEngine] = None

def get_workflow_engine() -> MultiAgentWorkflowEngine:
    """
    Returns singleton instance of MultiAgentWorkflowEngine populated with all 10 registered agents.
    """
    global _engine_instance
    if _engine_instance is None:
        registry = AgentRegistry()
        
        # Register all 10 specialized AI agents
        registry.register(OCRAgent())
        registry.register(PrescriptionIntelligenceAgent())
        registry.register(MedicineMatchingAgent())
        registry.register(DrugSafetyAgent())
        registry.register(InventoryAvailabilityAgent())
        registry.register(OrderRecommendationAgent())
        registry.register(RefillReminderAgent())
        registry.register(NotificationAgent())
        registry.register(AIHealthCompanionAgent())
        
        _engine_instance = MultiAgentWorkflowEngine(registry=registry)
    return _engine_instance
