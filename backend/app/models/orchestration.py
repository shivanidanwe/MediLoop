"""
MediLoop Multi-Agent Orchestration Database Models.
Encapsulates Agent Registry, Workflows, Execution Traces, Events,
Prescription OCR Results, NER Extractions, Drug Safety Screenings,
Refill Predictions & History, and Procurement Recommendations.
"""
from datetime import datetime, timezone
import enum
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, DateTime,
    ForeignKey, Index, JSON, func, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class WorkflowStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    CANCELLED = "CANCELLED"


class ExecutionStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    BLOCKED = "BLOCKED"
    WAITING_FOR_USER = "WAITING_FOR_USER"
    CANCELLED = "CANCELLED"


class AgentRegistryModel(Base):
    __tablename__ = "agent_registry"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(128), nullable=False)
    version = Column(String(32), default="2.0.0", nullable=False)
    status = Column(String(32), default="ACTIVE", nullable=False)  # ACTIVE, INACTIVE, DEGRADED
    description = Column(Text, nullable=True)
    timeout_seconds = Column(Float, default=60.0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    dependencies_json = Column(JSON, default=list, nullable=False)
    input_schema_json = Column(JSON, default=dict, nullable=False)
    output_schema_json = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class AgentWorkflowModel(Base):
    __tablename__ = "agent_workflows"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(String(64), unique=True, index=True, nullable=False)
    workflow_type = Column(String(64), index=True, nullable=False)  # PRESCRIPTION_PROCESSING, REFILL_REMINDER, PROCUREMENT
    status = Column(String(32), default=WorkflowStatus.QUEUED.value, index=True, nullable=False)
    
    patient_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id", ondelete="CASCADE"), nullable=True, index=True)
    pharmacy_id = Column(Integer, ForeignKey("pharmacies.id", ondelete="SET NULL"), nullable=True, index=True)
    
    current_step = Column(String(64), default="", nullable=False)
    is_paused = Column(Boolean, default=False, nullable=False)
    pause_reason = Column(String(256), nullable=True)
    error_message = Column(Text, nullable=True)
    
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_ms = Column(Float, default=0.0, nullable=False)
    metadata_json = Column(JSON, default=dict, nullable=False)

    # Relationships
    executions = relationship("AgentExecutionModel", back_populates="workflow", cascade="all, delete-orphan")


class AgentExecutionModel(Base):
    __tablename__ = "agent_executions"

    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(String(64), unique=True, index=True, nullable=False)
    workflow_id = Column(String(64), ForeignKey("agent_workflows.workflow_id", ondelete="CASCADE"), index=True, nullable=False)
    agent_id = Column(String(64), index=True, nullable=False)
    agent_name = Column(String(128), nullable=False)
    agent_version = Column(String(32), default="2.0.0", nullable=False)
    status = Column(String(32), default=ExecutionStatus.QUEUED.value, index=True, nullable=False)
    retry_count = Column(Integer, default=0, nullable=False)
    
    input_payload = Column(JSON, default=dict, nullable=False)
    output_payload = Column(JSON, default=dict, nullable=False)
    error_details = Column(Text, nullable=True)
    
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_ms = Column(Float, default=0.0, nullable=False)

    workflow = relationship("AgentWorkflowModel", back_populates="executions")


class AgentExecutionEventModel(Base):
    __tablename__ = "agent_execution_events"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(String(64), index=True, nullable=False)
    event_name = Column(String(64), index=True, nullable=False)
    source_agent = Column(String(64), nullable=False)
    target_agent = Column(String(64), nullable=True)
    payload_json = Column(JSON, default=dict, nullable=False)
    emitted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class PrescriptionOCRResultModel(Base):
    __tablename__ = "prescription_ocr_results"

    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id", ondelete="CASCADE"), index=True, nullable=False)
    patient_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    workflow_id = Column(String(64), nullable=True, index=True)
    
    extracted_text = Column(Text, nullable=False)
    medicine_text_regions = Column(JSON, default=list, nullable=False)
    ocr_confidence = Column(Float, default=0.0, nullable=False)
    image_quality_status = Column(String(64), default="ACCEPTABLE", nullable=False)  # EXCELLENT, ACCEPTABLE, BLURRY, LOW_RES, UNREADABLE
    processing_status = Column(String(64), default="SUCCESS", nullable=False)      # SUCCESS, FAILED, REQUIRES_CLARIFICATION
    engine_used = Column(String(64), default="OllamaVision (llava)", nullable=False)
    raw_response = Column(JSON, default=dict, nullable=False)
    error_details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class PrescriptionExtractionModel(Base):
    __tablename__ = "prescription_extractions"

    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id", ondelete="CASCADE"), index=True, nullable=False)
    patient_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    workflow_id = Column(String(64), nullable=True, index=True)
    
    extraction_status = Column(String(64), default="SUCCESS", nullable=False)  # SUCCESS, PARTIAL, FAILED, AMBIGUOUS
    medicines_json = Column(JSON, default=list, nullable=False)
    unrecognized_entities = Column(JSON, default=list, nullable=False)
    missing_information = Column(JSON, default=list, nullable=False)
    warnings = Column(JSON, default=list, nullable=False)
    model_used = Column(String(64), default="llama3.2:3b", nullable=False)
    published_to_patient = Column(Boolean, default=False, nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class DrugSafetyAssessmentModel(Base):
    __tablename__ = "drug_safety_assessments"

    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id", ondelete="CASCADE"), index=True, nullable=False)
    patient_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    workflow_id = Column(String(64), nullable=True, index=True)
    
    safety_status = Column(String(64), default="CLEAR", index=True, nullable=False)  # CLEAR, WARNING, CRITICAL_RISK, INSUFFICIENT_DATA
    overall_risk = Column(String(32), default="LOW", nullable=False)                # LOW, MODERATE, HIGH, CRITICAL
    can_proceed = Column(Boolean, default=True, nullable=False)
    requires_review = Column(Boolean, default=False, nullable=False)
    checks_performed = Column(JSON, default=list, nullable=False)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    findings = relationship("SafetyFindingModel", back_populates="assessment", cascade="all, delete-orphan")


class SafetyFindingModel(Base):
    __tablename__ = "safety_findings"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("drug_safety_assessments.id", ondelete="CASCADE"), index=True, nullable=False)
    medicine_name = Column(String(128), nullable=False)
    issue_type = Column(String(64), nullable=False)  # ALLERGY, DRUG_INTERACTION, DUPLICATE_THERAPY, CONTRAINDICATION, DOSAGE_ANOMALY
    severity = Column(String(32), nullable=False)    # LOW, MODERATE, HIGH, CRITICAL
    description = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=False)
    evidence_source = Column(String(256), nullable=False)
    confidence = Column(Float, default=0.90, nullable=False)
    is_blocking = Column(Boolean, default=False, nullable=False)

    assessment = relationship("DrugSafetyAssessmentModel", back_populates="findings")


class RefillPredictionModel(Base):
    __tablename__ = "refill_predictions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.id", ondelete="SET NULL"), nullable=True)
    medicine_name = Column(String(128), nullable=False)
    last_order_id = Column(Integer, ForeignKey("orders.id", ondelete="SET NULL"), nullable=True)
    last_order_date = Column(DateTime(timezone=True), nullable=False)
    last_ordered_quantity = Column(Integer, nullable=False)
    daily_usage_rate = Column(Float, default=1.0, nullable=False)
    estimated_remaining_days = Column(Integer, nullable=False)
    expected_refill_date = Column(DateTime(timezone=True), nullable=False)
    confidence = Column(Float, default=0.90, nullable=False)
    reason = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    reminders = relationship("RefillReminderHistoryModel", back_populates="prediction", cascade="all, delete-orphan")


class RefillReminderHistoryModel(Base):
    __tablename__ = "refill_reminder_history"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("refill_predictions.id", ondelete="CASCADE"), index=True, nullable=False)
    patient_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    medicine_id = Column(Integer, nullable=True)
    reminder_type = Column(String(32), nullable=False)  # 7_DAYS_BEFORE, 3_DAYS_BEFORE, DUE_TODAY, OVERDUE
    notification_id = Column(Integer, ForeignKey("notifications.id", ondelete="SET NULL"), nullable=True)
    sent_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    deduplication_key = Column(String(128), unique=True, index=True, nullable=False)

    prediction = relationship("RefillPredictionModel", back_populates="reminders")


class ProcurementRecommendationModel(Base):
    __tablename__ = "procurement_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    pharmacy_id = Column(Integer, ForeignKey("pharmacies.id", ondelete="CASCADE"), index=True, nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.id", ondelete="CASCADE"), index=True, nullable=False)
    medicine_name = Column(String(128), nullable=False)
    
    current_on_hand_stock = Column(Integer, nullable=False)
    reserved_stock = Column(Integer, default=0, nullable=False)
    available_to_promise = Column(Integer, nullable=False)
    confirmed_incoming_stock = Column(Integer, default=0, nullable=False)
    projected_available_stock = Column(Integer, nullable=False)
    reorder_threshold = Column(Integer, nullable=False)
    target_stock_level = Column(Integer, nullable=False)
    shortage_quantity = Column(Integer, nullable=False)
    suggested_procurement_quantity = Column(Integer, nullable=False)
    
    selected_supplier_id = Column(Integer, nullable=True)
    selected_supplier_name = Column(String(128), default="Apex Healthcare & Pharma Distributors Pvt Ltd", nullable=False)
    unit_wholesale_price = Column(Float, nullable=False)
    estimated_cost = Column(Float, nullable=False)
    
    # Status: MONITORING, LOW_STOCK_DETECTED, PROCUREMENT_DRAFT_CREATED, AWAITING_PHARMACIST_APPROVAL, APPROVED, SENT_TO_SUPPLIER, RECEIVED, CANCELLED
    status = Column(String(64), default="LOW_STOCK_DETECTED", index=True, nullable=False)
    purchase_order_id = Column(Integer, ForeignKey("supplier_purchase_orders.id", ondelete="SET NULL"), nullable=True)
    pdf_reference = Column(String(256), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class ProcurementOrderItemModel(Base):
    __tablename__ = "procurement_order_items"

    id = Column(Integer, primary_key=True, index=True)
    purchase_order_id = Column(Integer, ForeignKey("supplier_purchase_orders.id", ondelete="CASCADE"), index=True, nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.id", ondelete="SET NULL"), nullable=True)
    medicine_name = Column(String(128), nullable=False)
    generic_name = Column(String(128), nullable=True)
    manufacturer = Column(String(128), nullable=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    line_total = Column(Float, nullable=False)

