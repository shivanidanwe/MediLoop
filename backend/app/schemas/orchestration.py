"""
MediLoop Multi-Agent Orchestration Pydantic Data Contracts.
Strict schema validation for Inter-Agent Communication and APIs.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


# ==========================================
# Common / Execution Models
# ==========================================
class AgentMetadataSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    agent_id: str
    name: str
    version: str
    status: str
    description: Optional[str] = None
    timeout_seconds: float = 60.0
    max_retries: int = 3
    dependencies: List[str] = []


class AgentExecutionRecordSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    execution_id: str
    workflow_id: str
    agent_id: str
    agent_name: str
    agent_version: str
    status: str
    retry_count: int = 0
    duration_ms: float = 0.0
    input_payload: Dict[str, Any] = {}
    output_payload: Dict[str, Any] = {}
    error_details: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None


class WorkflowTimelineStepSchema(BaseModel):
    step_name: str
    agent_id: str
    status: str
    duration_ms: float
    started_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class WorkflowStateResponse(BaseModel):
    workflow_id: str
    workflow_type: str
    status: str
    current_step: str
    is_paused: bool = False
    pause_reason: Optional[str] = None
    error_message: Optional[str] = None
    patient_id: Optional[int] = None
    prescription_id: Optional[int] = None
    pharmacy_id: Optional[int] = None
    duration_ms: float = 0.0
    started_at: datetime
    completed_at: Optional[datetime] = None
    steps: List[WorkflowTimelineStepSchema] = []
    metadata: Dict[str, Any] = {}


# ==========================================
# Agent 1: OCR Agent Schemas
# ==========================================
class OCRAgentInput(BaseModel):
    prescription_id: int
    patient_id: int
    image_path: str
    file_type: str = "image/jpeg"
    metadata: Dict[str, Any] = {}


class OCRAgentOutput(BaseModel):
    prescription_id: int
    patient_id: int
    extracted_text: str
    medicine_text_regions: List[Dict[str, Any]] = []
    ocr_confidence: float
    image_quality_status: str  # EXCELLENT, ACCEPTABLE, BLURRY, LOW_RES, UNREADABLE
    processing_status: str     # SUCCESS, FAILED, REQUIRES_CLARIFICATION
    engine_used: str = "OllamaVision (llava)"
    error_details: Optional[str] = None


# ==========================================
# Agent 2: Prescription Intelligence Agent Schemas
# ==========================================
class PrescriptionIntelligenceInput(BaseModel):
    prescription_id: int
    patient_id: int
    ocr_text: str
    ocr_confidence: float = 0.90
    processing_metadata: Dict[str, Any] = {}


class ExtractedMedicineItem(BaseModel):
    medicine_name: str
    generic_name: Optional[str] = None
    brand_name: Optional[str] = None
    strength: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    quantity: Optional[int] = None
    route: Optional[str] = "Oral"
    instructions: Optional[str] = None
    confidence: float = 0.95
    verification_status: str = "recognized"  # recognized, unrecognized, ambiguous
    # Catalogue match
    matched_medicine_id: Optional[int] = None
    matched_brand_name: Optional[str] = None
    matched_manufacturer: Optional[str] = None
    match_confidence: float = 0.0
    match_status: str = "unmatched"  # exact, partial, unmatched


class PrescriptionIntelligenceOutput(BaseModel):
    prescription_id: int
    patient_id: int
    extraction_status: str  # SUCCESS, PARTIAL, FAILED
    medicines: List[ExtractedMedicineItem] = []
    unrecognized_entities: List[str] = []
    missing_information: List[str] = []
    warnings: List[str] = []
    model_used: str = "llama3.2:3b"
    published_to_patient: bool = False


# ==========================================
# Extraction Display Checkpoint Response
# ==========================================
class ExtractionDisplayCheckpointResponse(BaseModel):
    prescription_id: int
    patient_id: int
    extraction_status: str
    published: bool
    can_proceed_to_safety: bool
    medicines: List[ExtractedMedicineItem] = []
    unrecognized_entities: List[str] = []
    warnings: List[str] = []
    published_at: Optional[datetime] = None


# ==========================================
# Agent 3: Drug Safety Agent Schemas
# ==========================================
class SafetyFindingItem(BaseModel):
    medicine_name: str
    issue_type: str  # ALLERGY, DRUG_INTERACTION, DUPLICATE_THERAPY, CONTRAINDICATION, DOSAGE_ANOMALY
    severity: str    # LOW, MODERATE, HIGH, CRITICAL
    description: str
    recommendation: str
    source: str
    confidence: float = 0.95
    is_blocking: bool = False


class DrugSafetyInput(BaseModel):
    patient_id: int
    prescription_id: int
    extracted_medicines: List[ExtractedMedicineItem]
    allergies: Optional[str] = None
    medication_history: List[Dict[str, Any]] = []


class DrugSafetyOutput(BaseModel):
    patient_id: int
    prescription_id: int
    safety_status: str  # CLEAR, WARNING, CRITICAL_RISK, INSUFFICIENT_DATA
    overall_risk: str   # LOW, MODERATE, HIGH, CRITICAL
    checks_performed: List[str] = [
        "allergy_check",
        "medication_history",
        "interaction_check",
        "duplicate_therapy_check",
        "contraindications"
    ]
    findings: List[SafetyFindingItem] = []
    requires_review: bool = False
    can_proceed: bool = True
    summary: str = ""


# ==========================================
# Agent 4: Order Agent Schemas
# ==========================================
class OrderAgentInput(BaseModel):
    patient_id: int
    prescription_id: int
    selected_medicine_ids: Optional[List[int]] = None  # None = order all eligible
    requested_quantities: Optional[Dict[int, int]] = None  # medicine_id -> quantity
    pharmacy_id: Optional[int] = None
    idempotency_key: Optional[str] = None


class OrderAgentMedicineSummary(BaseModel):
    medicine_id: int
    medicine_name: str
    strength: Optional[str] = None
    quantity: int
    unit_price: float
    subtotal: float
    in_stock: bool
    available_stock: int


class OrderAgentOutput(BaseModel):
    draft_order_id: Optional[int] = None
    cart_id: Optional[int] = None
    prescription_id: int
    patient_id: int
    pharmacy_id: int
    selected_medicines: List[OrderAgentMedicineSummary] = []
    unavailable_medicines: List[Dict[str, Any]] = []
    subtotal: float
    delivery_charges: float = 0.0
    tax_amount: float = 0.0
    total_amount: float
    order_status: str = "READY_TO_PLACE"
    safety_status: str = "CLEAR"
    next_action: str = "PATIENT_CONFIRMATION_REQUIRED"
    idempotency_key: Optional[str] = None


# ==========================================
# Agent 5: Refill Reminder Agent Schemas
# ==========================================
class RefillPredictionItem(BaseModel):
    patient_id: int
    patient_name: Optional[str] = None
    patient_phone: Optional[str] = None
    medicine_id: Optional[int] = None
    medicine_name: str
    last_order_id: Optional[int] = None
    last_order_date: datetime
    last_ordered_quantity: int
    daily_usage_rate: float
    estimated_remaining_days: int
    expected_refill_date: datetime
    reminder_type: str  # 7_DAYS_BEFORE, 3_DAYS_BEFORE, DUE_TODAY, OVERDUE
    confidence: float
    reason: str


class RefillReminderTriggerResponse(BaseModel):
    total_evaluated_orders: int
    active_predictions: int
    new_reminders_dispatched: int
    predictions: List[RefillPredictionItem] = []


# ==========================================
# Agent 6: Procurement Agent Schemas
# ==========================================
class ProcurementRecommendationItem(BaseModel):
    procurement_id: int
    pharmacy_id: int
    medicine_id: int
    medicine_name: str
    current_stock: int
    reserved_stock: int = 0
    available_to_promise: int
    confirmed_incoming: int = 0
    projected_available: int
    reorder_level: int
    target_stock_level: int
    shortage_quantity: int
    suggested_procurement_quantity: int
    supplier_name: str
    unit_wholesale_price: float
    estimated_cost: float
    status: str
    purchase_order_id: Optional[int] = None
    pdf_reference: Optional[str] = None


class ProcurementCycleResponse(BaseModel):
    pharmacy_id: int
    total_skus_evaluated: int
    low_stock_detected_count: int
    recommendations_generated: int
    draft_purchase_orders_created: int
    recommendations: List[ProcurementRecommendationItem] = []


class ProcurementActionRequest(BaseModel):
    notes: Optional[str] = ""


class GoodsReceiptRequest(BaseModel):
    received_quantity: int
    batch_number: Optional[str] = "BAT-2026-REC"
    expiry_date: Optional[str] = "2027-12-31"
    notes: Optional[str] = "Goods received and verified by licensed pharmacist."


# ==========================================
# Orchestration V2 Schemas & Workflow Models
# ==========================================
class CatalogueMatchSchema(BaseModel):
    medicine_id: int
    brand_name: str
    generic_name: Optional[str] = None
    strength: Optional[str] = None
    dosage_form: Optional[str] = None
    unit_price: float = 0.0
    match_confidence: float = 0.90


class ExtractedMedicineSchema(BaseModel):
    medicine_name: str
    generic_name: Optional[str] = None
    brand_name: Optional[str] = None
    strength: Optional[str] = None
    dosage: Optional[str] = "1 tablet"
    frequency: Optional[str] = "1-0-1"
    duration: Optional[str] = "5 days"
    quantity: Optional[int] = 10
    route: Optional[str] = "Oral"
    instructions: Optional[str] = None
    confidence: float = 0.90
    is_ambiguous: bool = False
    catalogue_match: Optional[CatalogueMatchSchema] = None


class OCRResultSchema(BaseModel):
    id: Optional[int] = None
    prescription_id: int
    patient_id: int
    raw_text: str
    detected_medicine_regions: List[Dict[str, Any]] = []
    confidence_score: float = 0.90
    rotation_angle: float = 0.0
    contrast_enhanced: bool = False
    engine_used: str = "OllamaVision (llava)"
    status: str = "COMPLETED"
    processing_time_ms: float = 0.0
    created_at: Optional[datetime] = None


class PrescriptionExtractionSchema(BaseModel):
    id: Optional[int] = None
    prescription_id: int
    patient_id: int
    extracted_medicines: List[Any] = []
    unrecognized_medicines: List[str] = []
    ambiguous_medicines: List[str] = []
    missing_strength_medicines: List[str] = []
    doctor_name: Optional[str] = None
    clinic_name: Optional[str] = None
    prescription_date: Optional[str] = None
    general_instructions: Optional[str] = None
    total_medicines: int = 0
    matched_medicines_count: int = 0
    overall_confidence: float = 0.0
    extraction_notes: Optional[str] = None
    processing_time_ms: float = 0.0
    created_at: Optional[datetime] = None


class SafetyFindingSchema(BaseModel):
    medicine_name: str
    issue_type: str
    severity: str
    description: str
    recommendation: str
    clinical_evidence: Optional[str] = None
    requires_pharmacist_action: bool = False
    resolved: bool = False


class DrugSafetyAssessmentSchema(BaseModel):
    id: Optional[int] = None
    prescription_id: int
    patient_id: int
    safety_status: str
    overall_risk: str
    checks_performed: List[str] = []
    findings: List[Any] = []
    requires_review: bool = False
    can_proceed: bool = True
    pharmacist_cleared: bool = False
    clearance_notes: Optional[str] = None
    processing_time_ms: float = 0.0
    created_at: Optional[datetime] = None


class OrderItemPreparationSchema(BaseModel):
    medicine_id: int
    medicine_name: str
    generic_name: Optional[str] = None
    strength: Optional[str] = None
    prescribed_quantity: int
    ordered_quantity: int
    unit_price: float
    subtotal: float
    is_available: bool = True
    available_stock: int


class UnavailableItemSchema(BaseModel):
    medicine_id: int
    medicine_name: str
    requested_quantity: int
    available_quantity: int
    reason: str
    can_fulfill_partially: bool = False


class OrderPreparationSchema(BaseModel):
    draft_order_id: Optional[int] = None
    order_number: Optional[str] = None
    cart_id: Optional[int] = None
    prescription_id: int
    patient_id: int
    pharmacy_id: int = 1
    order_status: str = "READY_TO_PLACE"
    safety_status: str = "safe"
    items: List[OrderItemPreparationSchema] = []
    unavailable_items: List[UnavailableItemSchema] = []
    subtotal: float = 0.0
    delivery_charge: float = 0.0
    discount: float = 0.0
    total_amount: float = 0.0
    next_action: str = "PATIENT_CONFIRMATION_REQUIRED"
    processing_time_ms: float = 0.0
    created_at: Optional[datetime] = None


class WorkflowTimelineEventSchema(BaseModel):
    event_type: str
    agent_id: str
    payload: Dict[str, Any] = {}
    timestamp: datetime


class WorkflowSummarySchema(BaseModel):
    workflow_id: str
    workflow_type: str
    status: str
    current_step: str
    patient_id: Optional[int] = None
    prescription_id: Optional[int] = None
    pharmacy_id: Optional[int] = None
    events: List[WorkflowTimelineEventSchema] = []
    error_details: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None


class ProcurementRecommendationSchema(BaseModel):
    id: int
    pharmacy_id: int
    medicine_id: int
    medicine_name: str
    current_on_hand_stock: int
    reorder_threshold: int
    target_stock_level: int
    shortage_quantity: int
    suggested_procurement_quantity: int
    selected_supplier_name: str
    unit_wholesale_price: float
    estimated_cost: float
    status: str
    purchase_order_id: Optional[int] = None
    pdf_reference: Optional[str] = None
    created_at: datetime


class ProcurementDraftSummarySchema(BaseModel):
    purchase_order_id: Optional[int] = None
    po_number: str
    pharmacy_id: int
    pharmacy_name: str
    supplier_name: str
    status: str
    total_items: int
    total_quantity: int
    subtotal: float
    tax_amount: float
    total_amount: float
    pdf_reference: Optional[str] = None
    items: List[ProcurementRecommendationSchema] = []
    created_at: datetime


class RefillPredictionSchema(BaseModel):
    id: Optional[int] = None
    patient_id: int
    medicine_id: Optional[int] = None
    medicine_name: str
    last_order_date: datetime
    last_ordered_quantity: int
    daily_usage_rate: float
    estimated_remaining_days: int
    expected_refill_date: datetime
    confidence: float
    reason: Optional[str] = None
    is_active: bool = True
    reminder_sent: bool = False
    reminder_type: Optional[str] = None


class SafetyReevaluationRequestSchema(BaseModel):
    cleared_by_pharmacist: bool = True
    pharmacist_notes: Optional[str] = "Clinical warning reviewed and cleared by pharmacist."


class ProcurementApprovalRequestSchema(BaseModel):
    pharmacist_id: int = 1
    notes: Optional[str] = "Approved by pharmacist."


AgentRegistrySchema = AgentMetadataSchema
