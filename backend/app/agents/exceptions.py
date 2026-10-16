"""
MediLoop Multi-Agent Exception Definitions.
"""


class AgentException(Exception):
    """Base exception for all agent-related errors."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class AgentExecutionError(AgentException):
    """Raised when an agent fails during execution."""
    pass


class AgentValidationError(AgentException):
    """Raised when pre-execution validation checks fail."""
    pass


class MissingContextError(AgentException):
    """Raised when required fields are missing from shared AgentContext."""
    pass


class WorkflowConfigurationError(AgentException):
    """Raised when workflow ordering or routing configuration is invalid."""
    pass


class DuplicateAgentRegistrationError(AgentException):
    """Raised when registering an agent with a name that already exists."""
    pass
