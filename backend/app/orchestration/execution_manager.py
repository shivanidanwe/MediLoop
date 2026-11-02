"""
MediLoop Agent Execution Manager.
Handles lifecycle state machines, tracing, telemetry, timeouts, retries,
and database persistence for all agent workflow runs.
"""
import asyncio
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional, Tuple
from sqlalchemy.orm import Session

from app.models.orchestration import (
    AgentWorkflowModel,
    AgentExecutionModel,
    AgentExecutionEventModel,
    WorkflowStatus,
    ExecutionStatus
)
from app.orchestration.registry import agent_registry

logger = logging.getLogger(__name__)


class ExecutionManager:
    """Manages transactional database logging and lifecycle of multi-agent runs."""

    def __init__(self, db: Optional[Session] = None):
        self.db = db

    def create_workflow(
        self,
        db: Optional[Session] = None,
        workflow_type: str = "PRESCRIPTION_PROCESSING",
        patient_id: Optional[int] = None,
        prescription_id: Optional[int] = None,
        pharmacy_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentWorkflowModel:
        target_db = db or self.db
        workflow_id = f"WF-{uuid.uuid4().hex[:12].upper()}"
        workflow = AgentWorkflowModel(
            workflow_id=workflow_id,
            workflow_type=workflow_type,
            status=WorkflowStatus.RUNNING.value,
            patient_id=patient_id,
            prescription_id=prescription_id,
            pharmacy_id=pharmacy_id,
            current_step="INITIALIZING",
            metadata_json=metadata or {}
        )
        target_db.add(workflow)
        target_db.commit()
        target_db.refresh(workflow)
        logger.info(f"[ExecutionManager] Created workflow {workflow_id} ({workflow_type})")
        return workflow

    def update_workflow(
        self,
        db: Optional[Session] = None,
        workflow_id: str = "",
        current_step: Optional[str] = None,
        status: Optional[str] = None,
        is_paused: Optional[bool] = None,
        pause_reason: Optional[str] = None,
        error_message: Optional[str] = None,
        metadata_update: Optional[Dict[str, Any]] = None
    ) -> Optional[AgentWorkflowModel]:
        target_db = db or self.db
        wf = target_db.query(AgentWorkflowModel).filter(
            AgentWorkflowModel.workflow_id == workflow_id
        ).first()
        if not wf:
            return None

        if current_step is not None:
            wf.current_step = current_step
        if status is not None:
            wf.status = status
            if status in [WorkflowStatus.COMPLETED.value, WorkflowStatus.FAILED.value, WorkflowStatus.CANCELLED.value, "COMPLETED", "FAILED", "CANCELLED"]:
                wf.completed_at = datetime.now(timezone.utc)
                if wf.started_at:
                    wf.duration_ms = (wf.completed_at - wf.started_at).total_seconds() * 1000.0
        if is_paused is not None:
            wf.is_paused = is_paused
        if pause_reason is not None:
            wf.pause_reason = pause_reason
        if error_message is not None:
            wf.error_message = error_message
        if metadata_update:
            current_meta = dict(wf.metadata_json or {})
            current_meta.update(metadata_update)
            wf.metadata_json = current_meta

        target_db.commit()
        target_db.refresh(wf)
        return wf

    async def run_agent_with_monitoring(
        self,
        workflow_id: str,
        agent_id: str,
        execute_fn: Callable,
        patient_id: Optional[int] = None,
        prescription_id: Optional[int] = None,
        pharmacy_id: Optional[int] = None,
        input_payload: Optional[Dict[str, Any]] = None
    ) -> Tuple[AgentExecutionModel, Any]:
        """Runs an agent with lifecycle auditing, execution tracking, and DB logging."""
        target_db = self.db
        agent = agent_registry.get_agent(agent_id)
        execution_id = f"EXEC-{uuid.uuid4().hex[:12].upper()}"

        exec_record = AgentExecutionModel(
            execution_id=execution_id,
            workflow_id=workflow_id,
            agent_id=agent.agent_id,
            agent_name=agent.name,
            agent_version=agent.version,
            status=ExecutionStatus.RUNNING.value,
            input_payload=input_payload or {},
            retry_count=0
        )
        target_db.add(exec_record)
        target_db.commit()

        self.record_event(
            workflow_id=workflow_id,
            agent_id=agent_id,
            event_type=f"{agent_id}_started",
            payload={"execution_id": execution_id}
        )

        start_time = time.perf_counter()
        try:
            # Execute agent callable (coroutine or regular function)
            res = execute_fn()
            if asyncio.iscoroutine(res):
                result_output = await res
            else:
                result_output = res

            duration_ms = (time.perf_counter() - start_time) * 1000.0
            from fastapi.encoders import jsonable_encoder
            if hasattr(result_output, "model_dump"):
                output_payload = result_output.model_dump(mode="json")
            else:
                output_payload = jsonable_encoder(result_output)

            exec_record.status = ExecutionStatus.COMPLETED.value
            exec_record.output_payload = output_payload
            exec_record.duration_ms = duration_ms
            exec_record.completed_at = datetime.now(timezone.utc)
            target_db.commit()

            self.record_event(
                workflow_id=workflow_id,
                agent_id=agent_id,
                event_type=f"{agent_id}_completed",
                payload={"execution_id": execution_id, "duration_ms": duration_ms}
            )
            return exec_record, result_output
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            exec_record.status = ExecutionStatus.FAILED.value
            exec_record.error_details = str(e)
            exec_record.duration_ms = duration_ms
            exec_record.completed_at = datetime.now(timezone.utc)
            target_db.commit()

            self.record_event(
                workflow_id=workflow_id,
                agent_id=agent_id,
                event_type=f"{agent_id}_failed",
                payload={"execution_id": execution_id, "error": str(e)}
            )
            raise

    def record_event(
        self,
        workflow_id: str,
        agent_id: str,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None
    ) -> AgentExecutionEventModel:
        """Records an execution event in agent_execution_events table."""
        event = AgentExecutionEventModel(
            workflow_id=workflow_id,
            event_name=event_type,
            source_agent=agent_id,
            target_agent=None,
            payload_json=payload or {}
        )
        self.db.add(event)
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
        return event

    def emit_event(
        self,
        db: Session,
        workflow_id: str,
        event_name: str,
        source_agent: str,
        target_agent: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None
    ) -> AgentExecutionEventModel:
        event = AgentExecutionEventModel(
            workflow_id=workflow_id,
            event_name=event_name,
            source_agent=source_agent,
            target_agent=target_agent,
            payload_json=payload or {}
        )
        db.add(event)
        try:
            db.commit()
        except Exception:
            db.rollback()
        return event


# Singleton ExecutionManager
execution_manager = ExecutionManager()
