"""
MediLoop Audit Logger & Sensitive Data Redaction Module.
Logs security events, authentication attempts, workflow executions, and manual reviews
while redacting PII, passwords, and JWT tokens.
"""
import logging
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

# Setup dedicated Audit Logger
logger = logging.getLogger("mediloop.audit")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[AUDIT] %(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

SENSITIVE_KEYS = {"password", "plain_password", "access_token", "token", "secret", "cvv", "card_number"}

def redact_sensitive_data(data: Any) -> Any:
    """
    Recursively redacts sensitive fields from dictionaries and lists.
    """
    if isinstance(data, dict):
        cleaned = {}
        for k, v in data.items():
            if k.lower() in SENSITIVE_KEYS:
                cleaned[k] = "[REDACTED]"
            else:
                cleaned[k] = redact_sensitive_data(v)
        return cleaned
    elif isinstance(data, list):
        return [redact_sensitive_data(item) for item in data]
    return data

def log_audit_event(
    event_type: str,
    actor_id: Optional[str] = None,
    action: str = "",
    status: str = "SUCCESS",
    details: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Structured security audit logging helper.
    """
    safe_details = redact_sensitive_data(details or {})
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "actor_id": actor_id or "anonymous",
        "action": action,
        "status": status,
        "details": safe_details
    }
    logger.info(json.dumps(record))
