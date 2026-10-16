"""
MediLoop Agent Execution Logger.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
import logging
from typing import Any, Dict, Optional
from app.agents.events import AgentEvent

logger = logging.getLogger("mediloop.agents")


@dataclass
class ExecutionRecord:
    """Dataclass holding structured execution metrics for a single agent step."""
    request_id: str
    event: AgentEvent
    agent_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: float = 0.0
    status: str = "PENDING"
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def mark_complete(self, status: str = "SUCCESS", error: Optional[str] = None) -> None:
        self.end_time = datetime.now(timezone.utc)
        self.duration_ms = (self.end_time - self.start_time).total_seconds() * 1000.0
        self.status = status
        self.error = error


class AgentExecutionLogger:
    """Logger component for recording agent step lifecycle events."""

    def __init__(self, name: str = "mediloop.agents"):
        self.log = logging.getLogger(name)

    def log_start(self, request_id: str, event: AgentEvent, agent_name: str) -> ExecutionRecord:
        record = ExecutionRecord(
            request_id=request_id,
            event=event,
            agent_name=agent_name,
            start_time=datetime.now(timezone.utc),
        )
        self.log.info(
            f"[AGENT_START] req={request_id} event={event.value} agent={agent_name}"
        )
        return record

    def log_success(self, record: ExecutionRecord, details: Optional[str] = None) -> None:
        record.mark_complete(status="SUCCESS")
        self.log.info(
            f"[AGENT_SUCCESS] req={record.request_id} event={record.event.value} "
            f"agent={record.agent_name} duration={record.duration_ms:.2f}ms"
            f"{f' details={details}' if details else ''}"
        )

    def log_failure(self, record: ExecutionRecord, error_msg: str) -> None:
        record.mark_complete(status="FAILED", error=error_msg)
        self.log.error(
            f"[AGENT_FAILURE] req={record.request_id} event={record.event.value} "
            f"agent={record.agent_name} duration={record.duration_ms:.2f}ms error={error_msg}"
        )
