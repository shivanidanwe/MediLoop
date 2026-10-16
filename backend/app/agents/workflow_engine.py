"""
MediLoop Multi-Agent Workflow Engine.
Coordinates all 10 specialized AI agents into fault-tolerant, state-tracked,
and parallelized production workflows with pause/resume controls and telemetry.
"""
import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

import time

import uuid

from typing import Any, Dict, List, Optional

from app.agents.context import AgentContext
from app.agents.events import AgentEvent
from app.agents.exceptions import AgentExecutionError, AgentValidationError
from app.agents.orchestrator import AgentOrchestrator
from app.agents.registry import AgentRegistry


class WorkflowState(str, Enum):
    """
    State machine categories for multi-agent workflow execution lifecycle.
    """

    STARTED = "started"

    RUNNING = "running"

    WAITING = "waiting"

    FAILED = "failed"

    COMPLETED = "completed"

    CANCELLED = "cancelled"


@dataclass
class WorkflowExecutionRecord:
    """

    Telemetry and execution record for a multi-agent workflow run.

    """

    workflow_id: str

    workflow_name: str

    status: WorkflowState

    start_time: str

    end_time: Optional[str] = None

    duration_ms: float = 0.0

    current_step: str = ""

    agent_metrics: List[Dict[str, Any]] = field(default_factory=list)

    retry_count: int = 0

    error_details: Optional[str] = None

    dlq_record: Optional[Dict[str, Any]] = None

    context: Optional[AgentContext] = None


class MultiAgentWorkflowEngine:
    """

    Enterprise Multi-Agent Workflow Engine coordinating end-to-end AI pipelines.

    Manages state transitions, parallel agent execution, pharmacist review pauses,

    retries, and dead letter queue recording.

    """

    def __init__(
        self,
        registry: AgentRegistry,
        orchestrator: Optional[AgentOrchestrator] = None,
        max_retries: int = 2,
    ):

        self.registry = registry

        self.orchestrator = orchestrator or AgentOrchestrator(registry)

        self.max_retries = max_retries

        self._active_workflows: Dict[str, WorkflowExecutionRecord] = {}

        self._dead_letter_queue: List[Dict[str, Any]] = []

    # --- Workflow 1: Prescription Upload & Checkout Pipeline ---

    async def execute_prescription_upload_workflow(
        self, context: Optional[AgentContext] = None
    ) -> WorkflowExecutionRecord:

        """

        Executes end-to-end Prescription Upload workflow:

        OCR -> Rx Intelligence -> Medicine Matching -> Parallel (Drug Safety + Inventory) -> Recommendation -> Notification.

        """

        if context is None:

            context = AgentContext()

        wf_id = f"wf_rx_{uuid.uuid4().hex[:8]}"

        rec = WorkflowExecutionRecord(
            workflow_id=wf_id,
            workflow_name="PRESCRIPTION_UPLOAD_WORKFLOW",
            status=WorkflowState.STARTED,
            start_time=datetime.now().isoformat(),
            context=context,
        )

        self._active_workflows[wf_id] = rec

        start_ts = time.perf_counter()

        try:

            rec.status = WorkflowState.RUNNING

            # Step 1: OCR Agent

            rec.current_step = "ocr_agent"

            context = await self._execute_agent_with_retry("ocr_agent", AgentEvent.PRESCRIPTION_UPLOADED, context, rec)

            # Step 2: Prescription Intelligence Agent

            rec.current_step = "prescription_intelligence_agent"

            context = await self._execute_agent_with_retry(
                "prescription_intelligence_agent",
                AgentEvent.OCR_COMPLETED,
                context,
                rec,
            )

            # Step 3: Medicine Matching Agent

            rec.current_step = "medicine_matching_agent"

            context = await self._execute_agent_with_retry(
                "medicine_matching_agent",
                AgentEvent.MEDICINES_EXTRACTED,
                context,
                rec,
            )

            # Step 4: Parallel Execution (Drug Safety Agent + Inventory Availability Agent)

            rec.current_step = "parallel_safety_and_inventory"

            context = await self._execute_parallel_safety_and_inventory(
                context, rec
            )

            # Step 5: Order Recommendation Agent

            rec.current_step = "order_recommendation_agent"

            context = await self._execute_agent_with_retry(
                "order_recommendation_agent",
                AgentEvent.INVENTORY_CHECKED,
                context,
                rec,
            )

            # Check if Clinical Safety or Order Recommendation requires manual Pharmacist Review

            safety_meta = context.metadata.get("drug_safety", {})

            order_rec = context.metadata.get("order_recommendation", {})

            if safety_meta.get("requires_pharmacist_review") or order_rec.get(
                "requires_pharmacist_review"
            ):

                # Step 6a: Dispatch Notification Agent for Pharmacist Alert

                rec.current_step = "notification_agent_pause_alert"

                context = await self._execute_agent_with_retry(
                    "notification_agent", AgentEvent.ORDER_RECOMMENDED, context, rec
                )

                rec.status = WorkflowState.WAITING

                rec.duration_ms = round(
                    (time.perf_counter() - start_ts) * 1000.0, 2
                )

                rec.context = context

                return rec

            # Step 6b: Dispatch Notification Agent & Complete Workflow

            rec.current_step = "notification_agent"

            context = await self._execute_agent_with_retry(
                "notification_agent", AgentEvent.ORDER_RECOMMENDED, context, rec
            )

            rec.status = WorkflowState.COMPLETED

            rec.end_time = datetime.now().isoformat()

            rec.duration_ms = round(
                (time.perf_counter() - start_ts) * 1000.0, 2
            )

            rec.context = context

            return rec

        except Exception as e:

            return await self._handle_workflow_failure(wf_id, rec, e, start_ts)

    # --- Workflow 2: Order Completion & Refill Adherence ---

    async def execute_order_completed_workflow(
        self, context: Optional[AgentContext] = None
    ) -> WorkflowExecutionRecord:

        """

        Executes Order Completion workflow:

        Order Confirmed -> Refill Reminder Agent -> Notification Agent.

        """

        if context is None:

            context = AgentContext()

        wf_id = f"wf_order_{uuid.uuid4().hex[:8]}"

        rec = WorkflowExecutionRecord(
            workflow_id=wf_id,
            workflow_name="ORDER_COMPLETED_WORKFLOW",
            status=WorkflowState.STARTED,
            start_time=datetime.now().isoformat(),
            context=context,
        )

        self._active_workflows[wf_id] = rec

        start_ts = time.perf_counter()

        try:

            rec.status = WorkflowState.RUNNING

            rec.current_step = "refill_reminder_agent"

            context = await self._execute_agent_with_retry(
                "refill_reminder_agent", AgentEvent.ORDER_CONFIRMED, context, rec
            )

            rec.current_step = "notification_agent"

            context = await self._execute_agent_with_retry(
                "notification_agent", AgentEvent.REFILL_REMINDER, context, rec
            )

            rec.status = WorkflowState.COMPLETED

            rec.end_time = datetime.now().isoformat()

            rec.duration_ms = round(
                (time.perf_counter() - start_ts) * 1000.0, 2
            )

            rec.context = context

            return rec

        except Exception as e:

            return await self._handle_workflow_failure(wf_id, rec, e, start_ts)

    # --- Workflow 3: AI Health Companion Chat Workflow ---

    async def execute_health_companion_workflow(
        self, user_prompt: str, context: Optional[AgentContext] = None
    ) -> WorkflowExecutionRecord:

        """

        Executes Conversational Assistant workflow:

        User Chat -> AI Health Companion -> Sub-Agent Invocation -> Notification Agent.

        """

        if context is None:

            context = AgentContext()

        context.metadata["user_message"] = user_prompt

        wf_id = f"wf_chat_{uuid.uuid4().hex[:8]}"

        rec = WorkflowExecutionRecord(
            workflow_id=wf_id,
            workflow_name="HEALTH_COMPANION_WORKFLOW",
            status=WorkflowState.STARTED,
            start_time=datetime.now().isoformat(),
            context=context,
        )

        self._active_workflows[wf_id] = rec

        start_ts = time.perf_counter()

        try:

            rec.status = WorkflowState.RUNNING

            rec.current_step = "health_companion_agent"

            context = await self._execute_agent_with_retry(
                "health_companion_agent", AgentEvent.AI_CHAT_REQUEST, context, rec
            )

            rec.current_step = "notification_agent"

            context = await self._execute_agent_with_retry(
                "notification_agent", AgentEvent.AI_QUERY, context, rec
            )

            rec.status = WorkflowState.COMPLETED

            rec.end_time = datetime.now().isoformat()

            rec.duration_ms = round(
                (time.perf_counter() - start_ts) * 1000.0, 2
            )

            rec.context = context

            return rec

        except Exception as e:

            return await self._handle_workflow_failure(wf_id, rec, e, start_ts)

    # --- Manual Intervention Pause & Resume Controls ---

    async def resume_workflow(
        self, workflow_id: str, pharmacist_approved: bool, reviewer_notes: str = ""
    ) -> WorkflowExecutionRecord:

        """

        Resumes a paused (WAITING) workflow after manual pharmacist clinical review.

        """

        rec = self._active_workflows.get(workflow_id)

        if not rec:

            raise AgentValidationError(
                f"Workflow '{workflow_id}' not found in active state registry."
            )

        if rec.status != WorkflowState.WAITING:

            raise AgentValidationError(
                f"Workflow '{workflow_id}' is not in WAITING state (Current status: {rec.status.value})."
            )

        start_ts = time.perf_counter()

        ctx = rec.context or AgentContext()

        if not pharmacist_approved:

            rec.status = WorkflowState.CANCELLED

            rec.end_time = datetime.now().isoformat()

            rec.error_details = (
                f"Pharmacist rejected prescription review. Notes: {reviewer_notes}"
            )

            ctx.add_warning(
                f"Workflow cancelled by Pharmacist: {reviewer_notes}"
            )

            rec.context = ctx

            return rec

        # Approved by Pharmacist -> Clear clinical error blocks & resume

        ctx.metadata["pharmacist_approval"] = {
            "approved": True,
            "notes": reviewer_notes,
            "approved_at": datetime.now().isoformat(),
        }

        rec.status = WorkflowState.RUNNING

        rec.current_step = "notification_agent_resumed"

        ctx = await self._execute_agent_with_retry(
            "notification_agent", AgentEvent.ORDER_RECOMMENDED, ctx, rec
        )

        rec.status = WorkflowState.COMPLETED

        rec.end_time = datetime.now().isoformat()

        rec.duration_ms += round((time.perf_counter() - start_ts) * 1000.0, 2)

        rec.context = ctx

        return rec

    async def cancel_workflow(
        self, workflow_id: str, reason: str = ""
    ) -> WorkflowExecutionRecord:

        """Cancels an active or waiting workflow."""

        rec = self._active_workflows.get(workflow_id)

        if not rec:

            raise AgentValidationError(
                f"Workflow '{workflow_id}' not found in active registry."
            )

        rec.status = WorkflowState.CANCELLED

        rec.end_time = datetime.now().isoformat()

        rec.error_details = (
            f"Workflow cancelled by user/admin. Reason: {reason}"
        )

        return rec

    # --- Internal Parallel Execution & Fault Tolerance Helpers ---

    async def _execute_parallel_safety_and_inventory(
        self, context: AgentContext, rec: WorkflowExecutionRecord
    ) -> AgentContext:

        """

        Executes DrugSafetyAgent and InventoryAvailabilityAgent concurrently using asyncio.gather.

        """

        safety_agent = self.registry.get_agent("drug_safety_agent")

        inventory_agent = self.registry.get_agent(
            "inventory_availability_agent"
        )

        step_start = time.perf_counter()

        results = await asyncio.gather(
            safety_agent.execute(context),
            inventory_agent.execute(context),
            return_exceptions=True,
        )

        step_duration = (time.perf_counter() - step_start) * 1000.0

        for idx, res in enumerate(results):

            agent_name = (
                "drug_safety_agent"
                if idx == 0
                else "inventory_availability_agent"
            )

            if isinstance(res, Exception):

                rec.agent_metrics.append(
                    {
                        "agent": agent_name,
                        "status": "FAILED",
                        "duration_ms": step_duration,
                        "error": str(res),
                    }
                )

                raise res

            rec.agent_metrics.append(
                {
                    "agent": agent_name,
                    "status": "SUCCESS",
                    "duration_ms": step_duration,
                }
            )

        # Merge results into final context

        safety_ctx, inv_ctx = results[0], results[1]  # type: ignore

        context.metadata.update(safety_ctx.metadata)

        context.metadata.update(inv_ctx.metadata)

        context.warnings = list(
            set(context.warnings + safety_ctx.warnings + inv_ctx.warnings)
        )

        context.recommendations = list(
            set(
                context.recommendations
                + safety_ctx.recommendations
                + inv_ctx.recommendations
            )
        )

        return context

    async def _execute_agent_with_retry(
        self,
        agent_name: str,
        event: AgentEvent,
        context: AgentContext,
        rec: WorkflowExecutionRecord,
    ) -> AgentContext:

        """

        Executes a single agent with retry attempts and telemetry logging.

        """

        agent = self.registry.get_agent(agent_name)

        attempts = 0

        while attempts <= self.max_retries:

            step_start = time.perf_counter()

            try:

                if not await agent.can_handle(event, context):

                    return context

                await agent.validate(context)

                context = await agent.execute(context)

                step_duration = (time.perf_counter() - step_start) * 1000.0

                rec.agent_metrics.append(
                    {
                        "agent": agent_name,
                        "status": "SUCCESS",
                        "duration_ms": round(step_duration, 2),
                        "attempt": attempts + 1,
                    }
                )

                return context

            except Exception as e:

                attempts += 1

                step_duration = (time.perf_counter() - step_start) * 1000.0

                rec.agent_metrics.append(
                    {
                        "agent": agent_name,
                        "status": "RETRY"
                        if attempts <= self.max_retries
                        else "FAILED",
                        "duration_ms": round(step_duration, 2),
                        "attempt": attempts,
                        "error": str(e),
                    }
                )

                if attempts > self.max_retries:

                    raise e

                await asyncio.sleep(0.01 * attempts)

        return context

    async def _handle_workflow_failure(
        self,
        wf_id: str,
        rec: WorkflowExecutionRecord,
        error: Exception,
        start_ts: float,
    ) -> WorkflowExecutionRecord:

        """Pushes unrecoverable workflow failures to Dead Letter Queue (DLQ)."""

        rec.status = WorkflowState.FAILED

        rec.end_time = datetime.now().isoformat()

        rec.duration_ms = round((time.perf_counter() - start_ts) * 1000.0, 2)

        rec.error_details = str(error)

        dlq_entry = {
            "dlq_id": f"dlq_{uuid.uuid4().hex[:8]}",
            "workflow_id": wf_id,
            "workflow_name": rec.workflow_name,
            "failed_step": rec.current_step,
            "error_message": str(error),
            "timestamp": datetime.now().isoformat(),
        }

        rec.dlq_record = dlq_entry

        self._dead_letter_queue.append(dlq_entry)

        return rec

    # --- Telemetry & Status API Queries ---

    def get_workflow_status(
        self, workflow_id: str
    ) -> Optional[WorkflowExecutionRecord]:

        """Retrieves execution status record for a workflow ID."""

        return self._active_workflows.get(workflow_id)

    def get_dead_letter_queue(self) -> List[Dict[str, Any]]:

        """Returns all unrecoverable Dead Letter Queue entries."""

        return self._dead_letter_queue

    def get_telemetry_metrics(self) -> Dict[str, Any]:

        """Returns performance telemetry and execution statistics."""

        total = len(self._active_workflows)

        completed = sum(
            1
            for r in self._active_workflows.values()
            if r.status == WorkflowState.COMPLETED
        )

        failed = sum(
            1
            for r in self._active_workflows.values()
            if r.status == WorkflowState.FAILED
        )

        waiting = sum(
            1
            for r in self._active_workflows.values()
            if r.status == WorkflowState.WAITING
        )

        cancelled = sum(
            1
            for r in self._active_workflows.values()
            if r.status == WorkflowState.CANCELLED
        )

        avg_duration = (
            sum(r.duration_ms for r in self._active_workflows.values()) / total
            if total > 0
            else 0.0
        )

        return {
            "total_workflows_executed": total,
            "completed_workflows": completed,
            "failed_workflows": failed,
            "waiting_workflows": waiting,
            "cancelled_workflows": cancelled,
            "dlq_count": len(self._dead_letter_queue),
            "average_duration_ms": round(avg_duration, 2),
        }
