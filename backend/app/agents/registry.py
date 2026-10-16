"""
MediLoop Agent Registry for Dependency Injection.
"""
from typing import Dict, List
from app.agents.base_agent import BaseAgent
from app.agents.events import AgentEvent
from app.agents.exceptions import DuplicateAgentRegistrationError


class AgentRegistry:
    """
    Registry for registering, retrieving, and querying available AI agents.
    """

    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        """
        Registers an agent instance into the registry.
        Raises DuplicateAgentRegistrationError if an agent with the same name exists.
        """
        if agent.name in self._agents:
            raise DuplicateAgentRegistrationError(
                f"Agent with name '{agent.name}' is already registered."
            )
        self._agents[agent.name] = agent

    def unregister(self, agent_name: str) -> None:
        """Removes an agent from the registry by name."""
        if agent_name in self._agents:
            del self._agents[agent_name]

    def get_agent(self, agent_name: str) -> BaseAgent:
        """Retrieves a registered agent by name."""
        if agent_name not in self._agents:
            raise KeyError(f"No agent registered with name '{agent_name}'.")
        return self._agents[agent_name]

    def get_agents_for_event(self, event: AgentEvent) -> List[BaseAgent]:
        """Returns all registered agents configured to handle the specified event."""
        return [
            agent for agent in self._agents.values()
            if event in agent.handled_events
        ]

    def list_registered_agents(self) -> List[str]:
        """Returns names of all registered agents."""
        return list(self._agents.keys())

    def clear(self) -> None:
        """Clears all registered agents (primarily for testing)."""
        self._agents.clear()
