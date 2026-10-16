from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_pharmacist
from app.models.user import User
from app.models.pharmacist import Pharmacist
from app.agents.context import AgentContext
from app.agents.factory import get_workflow_engine

router = APIRouter(prefix="/ai", tags=["AI Integration"])

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    workflow_id: str
    warnings: List[str] = []
    recommendations: List[str] = []

class PharmacistResumeRequest(BaseModel):
    approved: bool
    notes: Optional[str] = ""

@router.post("/chat", response_model=ChatResponse)
async def ai_health_companion_chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    AI Health Companion Endpoint.
    Executes AIHealthCompanionAgent via MultiAgentWorkflowEngine.
    """
    engine = get_workflow_engine()
    context = AgentContext()
    context.metadata["customer_id"] = current_user.id
    context.metadata["user_name"] = current_user.full_name

    rec = await engine.execute_health_companion_workflow(
        user_prompt=request.message,
        context=context
    )

    reply_text = rec.context.metadata.get("health_companion", {}).get("response_text") or (
        f"Hello {current_user.full_name}, I am MediLoop AI Health Companion. "
        f"I received your query: '{request.message}'. How else can I assist with your medications?"
    )

    return {
        "reply": reply_text,
        "workflow_id": rec.workflow_id,
        "warnings": rec.context.warnings,
        "recommendations": rec.context.recommendations,
    }

@router.get("/telemetry")
def get_ai_telemetry_metrics(
    current_pharmacist: Pharmacist = Depends(get_current_pharmacist)
):
    """
    Retrieve performance telemetry metrics and dead-letter queue records for all multi-agent workflows.
    """
    engine = get_workflow_engine()
    return {
        "metrics": engine.get_telemetry_metrics(),
        "dead_letter_queue": engine.get_dead_letter_queue()
    }

@router.get("/workflows/{workflow_id}")
def get_workflow_status(
    workflow_id: str,
    current_pharmacist: Pharmacist = Depends(get_current_pharmacist)
):
    """
    Retrieve detailed status, step telemetry, and execution state for a specific workflow ID.
    """
    engine = get_workflow_engine()
    rec = engine.get_workflow_status(workflow_id)
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow '{workflow_id}' not found."
        )

    return {
        "workflow_id": rec.workflow_id,
        "name": rec.workflow_name,
        "status": rec.status.value,
        "start_time": rec.start_time,
        "end_time": rec.end_time,
        "duration_ms": rec.duration_ms,
        "current_step": rec.current_step,
        "agent_metrics": rec.agent_metrics,
        "error_details": rec.error_details,
    }

@router.post("/workflows/{workflow_id}/resume")
async def resume_paused_workflow(
    workflow_id: str,
    request: PharmacistResumeRequest,
    current_pharmacist: Pharmacist = Depends(get_current_pharmacist)
):
    """
    Endpoint for Pharmacists to approve or reject a paused workflow (manual review task).
    Resumes or cancels the workflow engine state.
    """
    engine = get_workflow_engine()
    try:
        rec = await engine.resume_workflow(
            workflow_id=workflow_id,
            pharmacist_approved=request.approved,
            reviewer_notes=request.notes or ""
        )
        return {
            "workflow_id": rec.workflow_id,
            "status": rec.status.value,
            "message": "Workflow successfully resumed" if request.approved else "Workflow cancelled by pharmacist review."
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
