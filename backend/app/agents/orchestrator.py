"""
MediLoop Core AI Agent Orchestrator.
"""
import time
from typing import Optional
from app.agents.context import AgentContext
from app.agents.events import AgentEvent
from app.agents.exceptions import AgentExecutionError, AgentValidationError
from app.agents.execution_log import AgentExecutionLogger
from app.agents.registry import AgentRegistry
from app.agents.workflow import WorkflowManager


class AgentOrchestrator:
    """
    Core Orchestrator coordinating multi-agent pipeline execution.
    Contains zero business logic; delegates execution to registered agents.
    """

    def __init__(self, registry: AgentRegistry, workflow_manager: Optional[WorkflowManager] = None):
        self.registry = registry
        self.workflow_manager = workflow_manager or WorkflowManager(registry)
        self.logger = AgentExecutionLogger()

    async def dispatch(self, event: AgentEvent, context: Optional[AgentContext] = None) -> AgentContext:
        """
        Dispatches an event through the agent pipeline, updating and returning shared context.
        """
        if context is None:
            context = AgentContext()

        candidate_agents = await self.workflow_manager.get_candidate_agents(event)
        if not candidate_agents:
            self.logger.log.info(f"[ORCHESTRATOR] No registered agents for event '{event.value}'.")
            return context

        for agent in candidate_agents:
            # Dynamically check if agent can handle event with current context state
            if not await agent.can_handle(event, context):
                continue

            log_record = self.logger.log_start(
                request_id=context.request_id,
                event=event,
                agent_name=agent.name,
            )
            step_start = time.perf_counter()
            try:
                # 1. Validate context
                is_valid = await agent.validate(context)
                if not is_valid:
                    raise AgentValidationError(
                        f"Agent '{agent.name}' pre-execution validation failed."
                    )

                # 2. Execute agent
                context = await agent.execute(context)
                step_duration = (time.perf_counter() - step_start) * 1000.0

                # 3. Log success
                context.record_step(
                    agent_name=agent.name,
                    status="SUCCESS",
                    duration_ms=step_duration,
                )
                self.logger.log_success(log_record)

            except Exception as e:
                step_duration = (time.perf_counter() - step_start) * 1000.0
                error_msg = str(e)
                context.record_step(
                    agent_name=agent.name,
                    status="FAILED",
                    duration_ms=step_duration,
                    error=error_msg,
                )
                self.logger.log_failure(log_record, error_msg=error_msg)
                raise AgentExecutionError(
                    f"Orchestration halted: Agent '{agent.name}' failed: {error_msg}",
                    details={"agent": agent.name, "event": str(event), "request_id": context.request_id}
                ) from e

        return context
