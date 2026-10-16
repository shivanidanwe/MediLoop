"""
Abstract Base Class for MediLoop AI Agents.
"""
from abc import ABC, abstractmethod
from typing import List
from app.agents.context import AgentContext
from app.agents.events import AgentEvent


class BaseAgent(ABC):
    """
    Abstract Base Class for all MediLoop specialized agents.
    Every agent must implement name, handled_events, can_handle, validate, and execute.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier name for the agent."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable summary of what the agent does."""
        pass

    @property
    @abstractmethod
    def handled_events(self) -> List[AgentEvent]:
        """List of AgentEvent types this agent is built to handle."""
        pass

    @abstractmethod
    async def can_handle(self, event: AgentEvent, context: AgentContext) -> bool:
        """
        Determines whether this agent can process the given event and context state.
        """
        pass

    @abstractmethod
    async def validate(self, context: AgentContext) -> bool:
        """
        Validates whether required context fields exist before execution begins.
        Raises AgentValidationError or returns False if prerequisites are missing.
        """
        pass

    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentContext:
        """
        Executes agent specific processing logic and returns the updated AgentContext.
        """
        pass
