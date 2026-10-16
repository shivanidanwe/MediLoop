import os
import uuid
import shutil
from fastapi import UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.prescription import Prescription, PrescriptionItem, VerificationStatus
from app.services.ocr_service import get_ocr_engine
from app.ai.prescription_agent import PrescriptionAgent
from app.core.database import SessionLocal
import logging

logger = logging.getLogger(__name__)

UPLOAD_DIR = "uploads/prescriptions"

def get_all_prescriptions(db: Session) -> List[Prescription]:
    return db.query(Prescription).order_by(Prescription.uploaded_at.desc()).all()

def get_prescription_by_id(db: Session, prescription_id: int) -> Optional[Prescription]:
    return db.query(Prescription).filter(Prescription.id == prescription_id).first()

def get_prescriptions_by_customer(db: Session, customer_id: int) -> List[Prescription]:
    return db.query(Prescription).filter(Prescription.customer_id == customer_id).order_by(Prescription.uploaded_at.desc()).all()

def get_prescriptions_by_pharmacy(db: Session, pharmacy_id: int) -> List[Prescription]:
    return db.query(Prescription).filter(Prescription.pharmacy_id == pharmacy_id).order_by(Prescription.uploaded_at.desc()).all()

def save_uploaded_file(file: UploadFile) -> str:
    """
    Saves an uploaded file to uploads/prescriptions with file size & extension validation.
    """
    from app.core.config import settings
    from fastapi import HTTPException, status

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # 1. Validate file extension
    original_name = os.path.basename(file.filename or "prescription")
    file_ext = os.path.splitext(original_name)[1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file extension '{file_ext}'. Allowed formats: JPG, JPEG, PNG, PDF."
        )

    # 2. Validate file size (10MB limit)
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0) # Reset stream pointer

    if file_size > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum limit of 10MB (Received: {round(file_size / (1024*1024), 2)}MB)."
        )
    
    # 3. Generate unique UUID filename to prevent path traversal & overwrites
    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
    dest_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return f"uploads/prescriptions/{unique_filename}"

def create_prescription_record(
    db: Session, 
    customer_id: int, 
    file_path: str, 
    original_filename: str, 
    pharmacy_id: Optional[int] = None
) -> Prescription:
    """
    Creates a new prescription record in database with UPLOADED status.
    """
    db_prescription = Prescription(
        customer_id=customer_id,
        pharmacy_id=pharmacy_id,
        uploaded_image_path=file_path,
        original_filename=original_filename,
        verification_status=VerificationStatus.PROCESSING, # Set directly to processing
    )
    db.add(db_prescription)
    db.commit()
    db.refresh(db_prescription)
    return db_prescription

def process_prescription_background(prescription_id: int) -> None:
    """
    Background worker task executing full 7-step MultiAgentWorkflowEngine pipeline.
    """
    import asyncio
    from app.agents.context import AgentContext
    from app.agents.factory import get_workflow_engine
    from app.agents.workflow_engine import WorkflowState

    logger.info(f"Starting MultiAgent AI workflow for prescription ID: {prescription_id}")
    db = SessionLocal()
    try:
        prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
        if not prescription:
            logger.error(f"Prescription {prescription_id} not found in background task.")
            return

        # Prepare Shared AgentContext with DB session and absolute image path
        img_path = prescription.uploaded_image_path or ""
        if img_path and not os.path.isabs(img_path):
            img_path = os.path.abspath(img_path)

        context = AgentContext(
            prescription_id=str(prescription.id),
            uploaded_image=img_path
        )
        context.db = db
        context.metadata["prescription_id"] = prescription.id
        context.metadata["customer_id"] = prescription.customer_id
        context.metadata["image_path"] = img_path
        context.metadata["file_path"] = img_path

        # Run MultiAgent workflow with resilient loop handling
        engine = get_workflow_engine()
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                rec = pool.submit(asyncio.run, engine.execute_prescription_upload_workflow(context)).result()
        else:
            rec = loop.run_until_complete(engine.execute_prescription_upload_workflow(context))

        # Extract results from shared workflow context
        extracted_text = rec.context.metadata.get("ocr", {}).get("extracted_text") or rec.context.ocr_text or "Extracted prescription text"
        avg_confidence = rec.context.metadata.get("ocr", {}).get("confidence_score") or 0.95
        matched_items = rec.context.metadata.get("medicine_matching", {}).get("matched_medicines") or rec.context.matched_medicines or []

        # Add parsed items to database
        item_confidences = []
        for item in matched_items:
            qty_val = str(item.get("quantity") or item.get("calculated_quantity") or "10").strip()
            qty = int(qty_val) if qty_val.isdigit() else 10
            freq_raw = str(item.get("frequency") or "").lower()
            if "3" in freq_raw or "thrice" in freq_raw or "tid" in freq_raw:
                freq_int = 3
            elif "4" in freq_raw or "qid" in freq_raw:
                freq_int = 4
            elif "1" in freq_raw or "once" in freq_raw or "od" in freq_raw:
                freq_int = 1
            else:
                freq_int = 2

            db_item = PrescriptionItem(
                prescription_id=prescription.id,
                medicine_name=item.get("medicine_name") or item.get("name") or item.get("matched_brand_name") or "Medicine",
                strength=item.get("strength") or "500mg",
                dosage_pattern=item.get("dosage_pattern") or item.get("dosage") or "1-0-1",
                frequency=freq_int,
                duration_days=item.get("duration_days") or 5,
                calculated_quantity=qty,
                confidence_score=item.get("confidence") or avg_confidence,
                medicine_id=item.get("medicine_id") or item.get("id")
            )
            db.add(db_item)
            item_confidences.append(db_item.confidence_score)

        if item_confidences:
            avg_confidence = sum(item_confidences) / len(item_confidences)

        # Update prescription record
        prescription.extracted_text = extracted_text
        prescription.overall_confidence = avg_confidence
        if not prescription.pharmacy_id:
            prescription.pharmacy_id = rec.context.pharmacy_id or (rec.context.metadata.get("order_recommendation", {}).get("recommended_pharmacy", {}).get("id")) or 1

        # Determine verification status based on workflow pause state
        if rec.status == WorkflowState.WAITING:
            prescription.verification_status = VerificationStatus.PENDING_VERIFICATION
            prescription.pharmacist_comments = f"Paused for Pharmacist Review [Workflow ID: {rec.workflow_id}]"
        elif rec.status == WorkflowState.COMPLETED:
            prescription.verification_status = VerificationStatus.APPROVED
            prescription.pharmacist_comments = f"Verified and approved autonomously by MediLoop AI [Workflow ID: {rec.workflow_id}]"
            try:
                from app.services.cart_service import convert_approved_prescription_to_cart
                convert_approved_prescription_to_cart(db, prescription.id)
            except Exception as ex_c:
                logger.error(f"Failed to auto-convert to cart: {ex_c}")
        else:
            prescription.verification_status = VerificationStatus.PENDING_VERIFICATION

        db.commit()
        logger.info(f"Successfully processed AI workflow {rec.workflow_id} for prescription {prescription_id}")

    except Exception as e:
        logger.exception(f"Error in background AI workflow processing of prescription {prescription_id}: {str(e)}")
        try:
            prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
            if prescription:
                prescription.verification_status = VerificationStatus.UPLOADED
                prescription.pharmacist_comments = f"Automated AI processing failed: {str(e)}"
                db.commit()
        except Exception as db_ex:
            logger.error(f"Failed to update status in error handler: {str(db_ex)}")
    finally:
        db.close()

def approve_prescription(db: Session, prescription_id: int, comments: Optional[str] = None) -> Optional[Prescription]:
    """
    Approve prescription verification status, resume workflow, and convert items to cart.
    """
    import asyncio
    from app.agents.factory import get_workflow_engine

    db_prescription = get_prescription_by_id(db, prescription_id)
    if not db_prescription:
        return None

    db_prescription.verification_status = VerificationStatus.APPROVED
    if comments:
        db_prescription.pharmacist_comments = comments
    db.commit()
    db.refresh(db_prescription)

    # Resume any paused AI workflow associated with this prescription
    try:
        engine = get_workflow_engine()
        # Find waiting workflow for this prescription
        for wf_id, rec in engine._active_workflows.items():
            if rec.context and rec.context.metadata.get("prescription_id") == prescription_id:
                if rec.status.value == "waiting":
                    asyncio.run(engine.resume_workflow(wf_id, pharmacist_approved=True, reviewer_notes=comments or "Approved"))
                    break
    except Exception as ex:
        logger.warn(f"Workflow resume check note: {str(ex)}")

    # Automatically convert approved prescription items to customer's active cart
    try:
        from app.services.cart_service import convert_approved_prescription_to_cart
        convert_approved_prescription_to_cart(db, db_prescription.id)
    except Exception as e:
        logger.error(f"Failed to auto-convert approved prescription {prescription_id} to cart: {str(e)}")

    return db_prescription

def reject_prescription(db: Session, prescription_id: int, comments: Optional[str] = None) -> Optional[Prescription]:
    """
    Reject prescription verification status and cancel active workflow.
    """
    import asyncio
    from app.agents.factory import get_workflow_engine

    db_prescription = get_prescription_by_id(db, prescription_id)
    if not db_prescription:
        return None

    db_prescription.verification_status = VerificationStatus.REJECTED
    if comments:
        db_prescription.pharmacist_comments = comments
    db.commit()
    db.refresh(db_prescription)

    try:
        engine = get_workflow_engine()
        for wf_id, rec in engine._active_workflows.items():
            if rec.context and rec.context.metadata.get("prescription_id") == prescription_id:
                if rec.status.value == "waiting":
                    asyncio.run(engine.resume_workflow(wf_id, pharmacist_approved=False, reviewer_notes=comments or "Rejected"))
                    break
    except Exception as ex:
        logger.warn(f"Workflow cancellation check note: {str(ex)}")

    return db_prescription
