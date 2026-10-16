"""
MediLoop Multi-Agent Domain Event Enum definitions.
"""
from enum import Enum


class AgentEvent(str, Enum):
    """
    Standard domain events dispatched across the MediLoop multi-agent ecosystem.
    """
    USER_REGISTERED = "user_registered"
    PRESCRIPTION_UPLOADED = "prescription_uploaded"
    OCR_COMPLETED = "ocr_completed"
    MEDICINES_EXTRACTED = "medicines_extracted"
    MEDICINES_MATCHED = "medicines_matched"
    SAFETY_VALIDATION_COMPLETED = "safety_validation_completed"
    INVENTORY_CHECKED = "inventory_checked"
    ORDER_RECOMMENDED = "order_recommended"
    ORDER_CREATED = "order_created"
    ORDER_CONFIRMED = "order_confirmed"
    REFILL_REMINDER = "refill_reminder"
    AI_QUERY = "ai_query"
    AI_CHAT_REQUEST = "ai_chat_request"
