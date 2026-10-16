"""
MediLoop Shared Agent Context Object.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid


@dataclass
class AgentContext:
    """
    Mutable shared context object passed across sequential AI agents.
    """
    request_id: str = field(default_factory=lambda: f"req_{uuid.uuid4().hex[:12]}")
    user_id: Optional[str] = None
    pharmacy_id: Optional[str] = None
    prescription_id: Optional[str] = None
    uploaded_image: Optional[str] = None
    ocr_text: Optional[str] = None
    extracted_medicines: List[Dict[str, Any]] = field(default_factory=list)
    matched_medicines: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    order_id: Optional[str] = None
    execution_history: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamps: Dict[str, str] = field(default_factory=lambda: {
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    db: Optional[Any] = None

    def add_warning(self, message: str) -> None:
        """Appends a safety or processing warning."""
        if message not in self.warnings:
            self.warnings.append(message)

    def add_recommendation(self, note: str) -> None:
        """Appends a clinical or pharmacy recommendation."""
        if note not in self.recommendations:
            self.recommendations.append(note)

    def record_step(self, agent_name: str, status: str, duration_ms: float, error: Optional[str] = None) -> None:
        """Appends an execution step record to history."""
        self.execution_history.append({
            "agent_name": agent_name,
            "status": status,
            "duration_ms": round(duration_ms, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": error,
        })
        self.timestamps["updated_at"] = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Serializes context into a plain dictionary representation."""
        return {
            "request_id": self.request_id,
            "user_id": self.user_id,
            "pharmacy_id": self.pharmacy_id,
            "prescription_id": self.prescription_id,
            "uploaded_image": self.uploaded_image,
            "ocr_text": self.ocr_text,
            "extracted_medicines": self.extracted_medicines,
            "matched_medicines": self.matched_medicines,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
            "order_id": self.order_id,
            "execution_history": self.execution_history,
            "metadata": self.metadata,
            "timestamps": self.timestamps,
        }
