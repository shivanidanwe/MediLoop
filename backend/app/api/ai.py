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

from app.schemas.order import OrderDraftConfirmRequest, OrderResponse
from app.services import ai_medicine_agent_service

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    workflow_id: str
    warnings: List[str] = []
    recommendations: List[str] = []
    order_draft: Optional[Dict[str, Any]] = None
    in_scope: bool = True

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
    AI Medicine Assistant Chat & Transcribed Voice Input Endpoint.
    Strictly restricted to medicine information, allergies, uploaded prescriptions,
    and verified ordering workflows. Rejects unrelated topics with prescribed notice.
    """
    res = ai_medicine_agent_service.process_ai_patient_message(
        db=db,
        current_user=current_user,
        user_message=request.message
    )
    return res

@router.post("/orders/confirm", response_model=OrderResponse)
def confirm_order_draft(
    request: OrderDraftConfirmRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Explicit patient confirmation of an AI-prepared order draft.
    Prevents duplicate submissions via idempotency key and records audit trail.
    """
    order = ai_medicine_agent_service.submit_confirmed_order(
        db=db,
        customer_id=current_user.id,
        draft_id=request.draft_id,
        idempotency_key=request.idempotency_key,
        address_id=request.address_id,
        payment_method=request.payment_method or "COD"
    )
    return order

@router.get("/prescriptions")
def get_patient_prescriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deterministic tool: Retrieve patient's authorized prescriptions."""
    return ai_medicine_agent_service.get_my_prescriptions(db, current_user.id)

@router.get("/allergies")
def get_patient_allergies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deterministic tool: Retrieve patient's recorded allergies."""
    return ai_medicine_agent_service.get_my_recorded_allergies(db, current_user.id)

@router.get("/orders/status")
def get_patient_order_status(
    order_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deterministic tool: Retrieve patient's order status."""
    return ai_medicine_agent_service.get_my_order_status(db, current_user.id, order_id)

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
