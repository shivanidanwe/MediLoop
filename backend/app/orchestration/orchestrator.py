"""
MediLoop Multi-Agent Orchestration Layer - Central Multi-Agent Orchestrator.
Coordinates the execution sequence of all 6 specialized agents:
1. OCR Agent
2. Prescription Intelligence Agent
   [Checkpoint: Publish Consolidated Extraction Result]
3. Drug Safety Agent
4. Order Agent
Background Workers:
5. Refill Reminder Agent
6. Procurement Agent

Enforces execution sequence, guardrails, checkpoints, database transactionality,
event auditing, and state machine transitions.
"""
import uuid
import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models.orchestration import (
    AgentWorkflowModel,
    AgentExecutionModel,
    AgentExecutionEventModel,
    PrescriptionOCRResultModel,
    PrescriptionExtractionModel,
    DrugSafetyAssessmentModel
)
from app.models.prescription import Prescription
from app.schemas.orchestration import (
    WorkflowSummarySchema,
    WorkflowTimelineEventSchema,
    PrescriptionExtractionSchema,
    DrugSafetyAssessmentSchema,
    OrderPreparationSchema,
    RefillPredictionSchema,
    ProcurementDraftSummarySchema
)
from app.orchestration.registry import MultiAgentRegistry
from app.orchestration.execution_manager import ExecutionManager
from app.orchestration.agents.ocr_agent import OCRAgent
from app.orchestration.agents.prescription_intelligence_agent import PrescriptionIntelligenceAgent
from app.orchestration.agents.drug_safety_agent import DrugSafetyAgent
from app.orchestration.agents.order_agent import OrderAgent
from app.orchestration.agents.refill_reminder_agent import RefillReminderAgent
from app.orchestration.agents.procurement_agent import ProcurementAgent

logger = logging.getLogger(__name__)


class MultiAgentOrchestrator:
    """
    Central Controller for MediLoop Multi-Agent Architecture.
    Controls sequential dependencies, background agents, and execution state.
    """
    def __init__(self, db: Session):
        self.db = db
        self.registry = MultiAgentRegistry(db)
        self.execution_manager = ExecutionManager(db)
        # Ensure agents are registered in DB
        self.registry.sync_to_db()

    async def process_prescription_workflow(
        self,
        prescription_id: int,
        patient_id: Optional[int] = None,
        pharmacy_id: int = 1,
        patient_selection: Optional[Dict[str, Any]] = None,
        auto_order: bool = True
    ) -> WorkflowSummarySchema:
        """
        Executes the primary sequential pipeline:
        Prescription -> OCR Agent -> Prescription Intelligence Agent -> Checkpoint -> Drug Safety Agent -> Order Agent
        """
        start_time = time.perf_counter()
        workflow_id = f"wf_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"

        # Resolve prescription and patient
        rx = self.db.query(Prescription).filter(Prescription.id == prescription_id).first()
        if not rx:
            raise ValueError(f"Prescription with id {prescription_id} does not exist.")

        resolved_patient_id = patient_id or rx.customer_id
        resolved_pharmacy_id = pharmacy_id or rx.pharmacy_id or 1

        # 1. Initialize Workflow Record in DB
        workflow = AgentWorkflowModel(
            workflow_id=workflow_id,
            workflow_type="PRESCRIPTION_PROCESSING",
            status="RUNNING",
            current_step="OCR_EXTRACTION",
            patient_id=resolved_patient_id,
            prescription_id=prescription_id,
            pharmacy_id=resolved_pharmacy_id,
            started_at=datetime.now(timezone.utc)
        )
        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)

        ocr_agent = OCRAgent(self.db)
        intel_agent = PrescriptionIntelligenceAgent(self.db)
        safety_agent = DrugSafetyAgent(self.db)
        order_agent = OrderAgent(self.db)

        # ---------------------------------------------------------------------
        # STEP 1: OCR Agent
        # ---------------------------------------------------------------------
        logger.info(f"[{workflow_id}] Running Step 1: OCR Agent for Prescription #{prescription_id}")
        ocr_result_schema = None
        try:
            ocr_exec, ocr_result_schema = await self.execution_manager.run_agent_with_monitoring(
                workflow_id=workflow_id,
                agent_id="ocr_agent",
                execute_fn=lambda: ocr_agent.execute(
                    prescription_id=prescription_id,
                    patient_id=resolved_patient_id
                ),
                patient_id=resolved_patient_id,
                prescription_id=prescription_id,
                pharmacy_id=resolved_pharmacy_id,
                input_payload={"prescription_id": prescription_id}
            )
        except Exception as e:
            logger.error(f"[{workflow_id}] OCR Agent execution failed: {e}")
            workflow.status = "FAILED"
            workflow.error_message = f"OCR Agent failed: {str(e)}"
            self.db.commit()
            return self._build_workflow_summary(workflow)

        if not ocr_result_schema or ocr_result_schema.status == "UNREADABLE":
            workflow.status = "FAILED"
            workflow.error_message = "Prescription image is unreadable, blank, or corrupted. Please upload a clear document."
            self.db.commit()
            return self._build_workflow_summary(workflow)

        # ---------------------------------------------------------------------
        # STEP 2: Prescription Intelligence Agent (Medical NER & Catalogue Match)
        # ---------------------------------------------------------------------
        logger.info(f"[{workflow_id}] Running Step 2: Prescription Intelligence Agent")
        workflow.current_step = "PRESCRIPTION_INTELLIGENCE"
        self.db.commit()

        intel_result_schema = None
        try:
            intel_exec, intel_result_schema = await self.execution_manager.run_agent_with_monitoring(
                workflow_id=workflow_id,
                agent_id="prescription_intelligence_agent",
                execute_fn=lambda: intel_agent.execute(
                    prescription_id=prescription_id,
                    patient_id=resolved_patient_id,
                    raw_text=ocr_result_schema.raw_text,
                    ocr_confidence=ocr_result_schema.confidence_score
                ),
                patient_id=resolved_patient_id,
                prescription_id=prescription_id,
                pharmacy_id=resolved_pharmacy_id,
                input_payload={"raw_text_length": len(ocr_result_schema.raw_text)}
            )
        except Exception as e:
            logger.error(f"[{workflow_id}] Prescription Intelligence Agent failed: {e}")
            workflow.status = "FAILED"
            workflow.error_message = f"Prescription Intelligence failed: {str(e)}"
            self.db.commit()
            return self._build_workflow_summary(workflow)

        # ---------------------------------------------------------------------
        # STEP 3: Checkpoint: Publish Consolidated Extraction Result
        # ---------------------------------------------------------------------
        logger.info(f"[{workflow_id}] Checkpoint: Extracted {intel_result_schema.total_medicines} medicines. Publishing extraction.")
        self.execution_manager.record_event(
            workflow_id=workflow_id,
            agent_id="prescription_intelligence_agent",
            event_type="EXTRACTION_CHECKPOINT_PUBLISHED",
            payload={
                "total_medicines": intel_result_schema.total_medicines,
                "matched_count": intel_result_schema.matched_medicines_count,
                "extraction_id": intel_result_schema.id
            }
        )

        if intel_result_schema.total_medicines == 0:
            workflow.status = "FAILED"
            workflow.error_message = "No valid prescribed medicines could be identified in the prescription."
            self.db.commit()
            return self._build_workflow_summary(workflow)

        # ---------------------------------------------------------------------
        # STEP 4: Drug Safety Agent
        # ---------------------------------------------------------------------
        logger.info(f"[{workflow_id}] Running Step 4: Drug Safety Agent")
        workflow.current_step = "DRUG_SAFETY_SCREENING"
        self.db.commit()

        safety_result_schema = None
        try:
            safety_exec, safety_result_schema = await self.execution_manager.run_agent_with_monitoring(
                workflow_id=workflow_id,
                agent_id="drug_safety_agent",
                execute_fn=lambda: safety_agent.execute(
                    prescription_id=prescription_id,
                    patient_id=resolved_patient_id,
                    extracted_medicines=intel_result_schema.extracted_medicines
                ),
                patient_id=resolved_patient_id,
                prescription_id=prescription_id,
                pharmacy_id=resolved_pharmacy_id,
                input_payload={"medicines_count": len(intel_result_schema.extracted_medicines)}
            )
        except Exception as e:
            logger.error(f"[{workflow_id}] Drug Safety Agent failed: {e}")
            workflow.status = "FAILED"
            workflow.error_message = f"Drug Safety screening failed: {str(e)}"
            self.db.commit()
            return self._build_workflow_summary(workflow)

        # Safety Gate Check: If critical risk or severe allergy conflict, halt ordering
        if not safety_result_schema.can_proceed:
            logger.warning(f"[{workflow_id}] Safety findings block automated order. Workflow paused for clinical review.")
            workflow.status = "SAFETY_BLOCKED"
            workflow.current_step = "AWAITING_SAFETY_CLEARANCE"
            self.execution_manager.record_event(
                workflow_id=workflow_id,
                agent_id="drug_safety_agent",
                event_type="SAFETY_REVIEW_REQUIRED",
                payload={
                    "safety_status": safety_result_schema.safety_status,
                    "findings_count": len(safety_result_schema.findings)
                }
            )
            self.db.commit()
            return self._build_workflow_summary(workflow)

        # ---------------------------------------------------------------------
        # STEP 5: Order Agent (Cart & Draft Order Preparation)
        # ---------------------------------------------------------------------
        if auto_order:
            logger.info(f"[{workflow_id}] Running Step 5: Order Agent")
            workflow.current_step = "ORDER_PREPARATION"
            self.db.commit()

            order_result_schema = None
            try:
                order_exec, order_result_schema = await self.execution_manager.run_agent_with_monitoring(
                    workflow_id=workflow_id,
                    agent_id="order_agent",
                    execute_fn=lambda: order_agent.execute(
                        prescription_id=prescription_id,
                        patient_id=resolved_patient_id,
                        extracted_medicines=intel_result_schema.extracted_medicines,
                        safety_assessment=safety_result_schema,
                        pharmacy_id=resolved_pharmacy_id,
                        patient_selection=patient_selection
                    ),
                    patient_id=resolved_patient_id,
                    prescription_id=prescription_id,
                    pharmacy_id=resolved_pharmacy_id,
                    input_payload={"pharmacy_id": resolved_pharmacy_id}
                )
            except Exception as e:
                logger.error(f"[{workflow_id}] Order Agent failed: {e}")
                workflow.status = "FAILED"
                workflow.error_message = f"Order preparation failed: {str(e)}"
                self.db.commit()
                return self._build_workflow_summary(workflow)

            workflow.status = "COMPLETED"
            workflow.current_step = "READY_TO_PLACE"
            workflow.completed_at = datetime.now(timezone.utc)
            self.db.commit()

        return self._build_workflow_summary(workflow)

    def get_prescription_extraction(self, prescription_id: int) -> Optional[PrescriptionExtractionSchema]:
        """
        Retrieves the immutable extracted medicine details for patient app display.
        """
        ext = self.db.query(PrescriptionExtractionModel).filter(
            PrescriptionExtractionModel.prescription_id == prescription_id
        ).order_by(PrescriptionExtractionModel.created_at.desc()).first()

        if not ext:
            return None

        meds = ext.medicines_json or []
        return PrescriptionExtractionSchema(
            id=ext.id,
            prescription_id=ext.prescription_id,
            patient_id=ext.patient_id,
            extracted_medicines=meds,
            unrecognized_medicines=ext.unrecognized_entities or [],
            ambiguous_medicines=ext.warnings or [],
            missing_strength_medicines=ext.missing_information or [],
            doctor_name=None,
            clinic_name=None,
            prescription_date=None,
            general_instructions=None,
            total_medicines=len(meds),
            matched_medicines_count=sum(1 for m in meds if isinstance(m, dict) and m.get("catalogue_match") or m.get("matched_medicine_id")),
            overall_confidence=0.92,
            extraction_notes=f"Extraction status: {ext.extraction_status}",
            created_at=ext.created_at
        )

    def get_prescription_safety(self, prescription_id: int) -> Optional[DrugSafetyAssessmentSchema]:
        """
        Retrieves the latest safety screening report for a prescription.
        """
        assessment = self.db.query(DrugSafetyAssessmentModel).filter(
            DrugSafetyAssessmentModel.prescription_id == prescription_id
        ).order_by(DrugSafetyAssessmentModel.created_at.desc()).first()

        if not assessment:
            return None

        findings = []
        for f in assessment.findings:
            findings.append({
                "medicine_name": f.medicine_name,
                "issue_type": f.issue_type,
                "severity": f.severity,
                "description": f.description,
                "recommendation": f.recommendation,
                "clinical_evidence": f.evidence_source,
                "requires_pharmacist_action": f.is_blocking,
                "resolved": not f.is_blocking
            })

        return DrugSafetyAssessmentSchema(
            id=assessment.id,
            prescription_id=assessment.prescription_id,
            patient_id=assessment.patient_id,
            safety_status=assessment.safety_status,
            overall_risk=assessment.overall_risk,
            checks_performed=assessment.checks_performed or [],
            findings=findings,
            requires_review=assessment.requires_review,
            can_proceed=assessment.can_proceed,
            pharmacist_cleared=assessment.can_proceed,
            clearance_notes=assessment.summary,
            processing_time_ms=0.0,
            created_at=assessment.created_at
        )

    async def re_evaluate_safety(
        self,
        prescription_id: int,
        cleared_by_pharmacist: bool = False,
        pharmacist_notes: Optional[str] = None
    ) -> DrugSafetyAssessmentSchema:
        """
        Allows controlled clinical re-evaluation after pharmacist review or clarification.
        """
        assessment = self.db.query(DrugSafetyAssessmentModel).filter(
            DrugSafetyAssessmentModel.prescription_id == prescription_id
        ).order_by(DrugSafetyAssessmentModel.created_at.desc()).first()

        if not assessment:
            raise ValueError(f"No safety assessment exists for prescription #{prescription_id}")

        if cleared_by_pharmacist:
            assessment.pharmacist_cleared = True
            assessment.can_proceed = True
            assessment.clearance_notes = pharmacist_notes or "Cleared by registered pharmacist."
            for f in assessment.findings:
                f.resolved = True
            self.db.commit()
            self.db.refresh(assessment)

            # Update any blocked workflow
            wf = self.db.query(AgentWorkflowModel).filter(
                AgentWorkflowModel.prescription_id == prescription_id,
                AgentWorkflowModel.status == "SAFETY_BLOCKED"
            ).first()
            if wf:
                wf.status = "RUNNING"
                wf.current_step = "ORDER_PREPARATION"
                self.db.commit()

        return self.get_prescription_safety(prescription_id)

    async def run_refill_reminder_worker(self, patient_id: Optional[int] = None) -> List[RefillPredictionSchema]:
        """Triggers the background Refill Reminder Agent."""
        agent = RefillReminderAgent(self.db)
        return await agent.execute(patient_id=patient_id)

    async def run_procurement_worker(self, pharmacy_id: int = 1) -> ProcurementDraftSummarySchema:
        """Triggers the background Procurement Agent."""
        agent = ProcurementAgent(self.db)
        return await agent.execute(pharmacy_id=pharmacy_id)

    def get_workflow_details(self, workflow_id: str) -> Optional[WorkflowSummarySchema]:
        """Retrieves full workflow summary with timeline events."""
        wf = self.db.query(AgentWorkflowModel).filter(AgentWorkflowModel.workflow_id == workflow_id).first()
        if not wf:
            return None
        return self._build_workflow_summary(wf)

    def _build_workflow_summary(self, wf: AgentWorkflowModel) -> WorkflowSummarySchema:
        """Constructs WorkflowSummarySchema including timeline events."""
        events = self.db.query(AgentExecutionEventModel).filter(
            AgentExecutionEventModel.workflow_id == wf.workflow_id
        ).order_by(AgentExecutionEventModel.emitted_at.asc()).all()

        timeline = [
            WorkflowTimelineEventSchema(
                event_type=e.event_name,
                agent_id=e.source_agent or "orchestrator",
                payload=e.payload_json or {},
                timestamp=e.emitted_at
            )
            for e in events
        ]

        return WorkflowSummarySchema(
            workflow_id=wf.workflow_id,
            workflow_type=wf.workflow_type,
            status=wf.status,
            current_step=wf.current_step,
            patient_id=wf.patient_id,
            prescription_id=wf.prescription_id,
            pharmacy_id=wf.pharmacy_id,
            events=timeline,
            error_details=wf.error_message,
            started_at=wf.started_at,
            completed_at=wf.completed_at
        )
