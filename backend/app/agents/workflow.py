"""
MediLoop Multi-Agent Workflow Manager.
"""
from typing import Dict, List
from app.agents.base_agent import BaseAgent
from app.agents.events import AgentEvent
from app.agents.registry import AgentRegistry


class WorkflowManager:
    """
    Manages workflow execution pipelines for domain events.
    """

    def __init__(self, registry: AgentRegistry):
        self.registry = registry
        self._custom_pipelines: Dict[AgentEvent, List[str]] = {}

    def set_custom_pipeline(self, event: AgentEvent, agent_names: List[str]) -> None:
        """Configures an explicit sequence of agent names for a specific event."""
        self._custom_pipelines[event] = agent_names

    async def get_candidate_agents(self, event: AgentEvent) -> List[BaseAgent]:
        """
        Returns candidate agents configured for an event in defined sequence.
        """
        if event in self._custom_pipelines:
            agent_names = self._custom_pipelines[event]
            return [self.registry.get_agent(name) for name in agent_names]

        return self.registry.get_agents_for_event(event)
