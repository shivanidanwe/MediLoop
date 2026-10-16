"""
MediLoop Refill Reminder Agent.
Proactively calculates medication completion dates, monitors chronic refills,
and generates structured adherence risk reports without auto-placing orders or triggering push alerts.
"""
from datetime import datetime, timedelta
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from app.agents.base_agent import BaseAgent
from app.agents.context import AgentContext
from app.agents.events import AgentEvent
from app.agents.exceptions import AgentValidationError


# Known Chronic Medication Generic Categories
CHRONIC_GENERIC_CATEGORIES: Set[str] = {
    "atorvastatin", "metformin", "amlodipine", "telmisartan", "losartan",
    "levothyroxine", "thyronorm", "glimepiride", "atenolol", "metoprolol",
    "rosuvastatin", "calcium + vitamin d3", "clopidogrel", "pantoprazole"
}


class RefillReminderAgent(BaseAgent):
    """
    Agent responsible for analyzing active medication supplies, dosage frequencies,
    and prescription durations to compute completion dates, detect chronic refill patterns,
    and calculate adherence risk levels.
    """

    def __init__(self, reminder_window_days: int = 5):
        self.reminder_window_days = reminder_window_days

    @property
    def name(self) -> str:
        return "refill_reminder_agent"

    @property
    def description(self) -> str:
        return (
            "Analyzes active medication supplies, dosage frequencies, and prescription durations "
            "to compute completion dates, detect chronic refill patterns, and calculate adherence risk levels."
        )

    @property
    def handled_events(self) -> List[AgentEvent]:
        return [
            AgentEvent.ORDER_CONFIRMED,
            AgentEvent.ORDER_CREATED,
            AgentEvent.REFILL_REMINDER,
            AgentEvent.INVENTORY_CHECKED,
            AgentEvent.SAFETY_VALIDATION_COMPLETED,
            AgentEvent.MEDICINES_MATCHED,
            AgentEvent.MEDICINES_EXTRACTED,
            AgentEvent.OCR_COMPLETED,
            AgentEvent.PRESCRIPTION_UPLOADED,
        ]

    async def can_handle(self, event: AgentEvent, context: AgentContext) -> bool:
        """
        Handles event if matched_medicines or extracted_medicines exists.
        """
        has_matched = len(context.matched_medicines) > 0
        has_extracted = len(context.extracted_medicines) > 0
        return event in self.handled_events and (has_matched or has_extracted)

    async def validate(self, context: AgentContext) -> bool:
        """
        Validates presence of medicine records in context.
        """
        if not context.matched_medicines and not context.extracted_medicines:
            raise AgentValidationError(
                "RefillReminderAgent validation failed: No medicines available in context to calculate refill schedule."
            )
        return True

    async def execute(self, context: AgentContext) -> AgentContext:
        """
        Calculates refill schedules and updates context.metadata['refill_report'].
        """
        target_medicines = list(context.matched_medicines) if context.matched_medicines else list(context.extracted_medicines)

        # Pull past delivered order items from DB if available
        if getattr(context, "db", None):
            try:
                from app.models.order import Order, OrderStatus
                c_id = context.metadata.get("customer_id") or getattr(context, "user_id", None)
                if c_id:
                    past_orders = context.db.query(Order).filter(
                        Order.customer_id == int(c_id),
                        Order.order_status == OrderStatus.DELIVERED
                    ).all()
                    for po in past_orders:
                        for p_item in po.items:
                            target_medicines.append({
                                "name": getattr(p_item.medicine, "brand_name", "Medicine"),
                                "generic_name": getattr(p_item.medicine, "generic_name", ""),
                                "quantity": str(p_item.quantity),
                                "frequency": "Once daily",
                                "duration": f"{p_item.quantity} days"
                            })
            except Exception:
                pass

        now = datetime.now()

        evaluated_items: List[Dict[str, Any]] = []
        completion_dates: List[datetime] = []
        statuses: List[str] = []
        risks: List[str] = []

        for med in target_medicines:
            raw_name = med.get("name", "Unknown")
            generic_name = (med.get("generic_name") or "").lower()
            frequency = med.get("frequency") or ""
            quantity_str = med.get("quantity") or ""
            duration_str = med.get("duration") or ""

            daily_intake = self._parse_daily_intake(frequency)
            supply_days = self._calculate_supply_days(quantity_str, duration_str, daily_intake)

            exp_completion = now + timedelta(days=supply_days)
            rem_date = exp_completion - timedelta(days=self.reminder_window_days)
            days_remaining = (exp_completion - now).days

            is_chronic = (supply_days >= 14) or (generic_name in CHRONIC_GENERIC_CATEGORIES)

            if days_remaining <= 0:
                item_status = "OVERDUE"
                item_risk = "HIGH" if is_chronic else "MEDIUM"
                context.add_warning(
                    f"Refill OVERDUE for medication '{raw_name}'. Immediate reorder recommended for adherence continuity."
                )
            elif days_remaining <= self.reminder_window_days:
                item_status = "READY_FOR_REORDER"
                item_risk = "HIGH" if (is_chronic and days_remaining <= 2) else "MEDIUM"
                context.add_warning(
                    f"Refill due in {days_remaining} days for '{raw_name}'. Reorder window is active."
                )
            else:
                item_status = "MONITORING"
                item_risk = "LOW"

            completion_dates.append(exp_completion)
            statuses.append(item_status)
            risks.append(item_risk)

            evaluated_items.append({
                "medicine_name": raw_name,
                "generic_name": med.get("generic_name", "Unknown"),
                "daily_intake": daily_intake,
                "supply_days": supply_days,
                "days_remaining": days_remaining,
                "is_chronic": is_chronic,
                "status": item_status,
                "risk_level": item_risk,
                "expected_completion_date": exp_completion.strftime("%Y-%m-%d"),
                "recommended_reminder_date": rem_date.strftime("%Y-%m-%d"),
            })

        overall_status = "OVERDUE" if "OVERDUE" in statuses else ("READY_FOR_REORDER" if "READY_FOR_REORDER" in statuses else "MONITORING")
        overall_risk = "HIGH" if "HIGH" in risks else ("MEDIUM" if "MEDIUM" in risks else "LOW")
        earliest_completion = min(completion_dates) if completion_dates else now
        earliest_reminder = earliest_completion - timedelta(days=self.reminder_window_days)

        refill_report = {
            "status": overall_status,
            "risk_level": overall_risk,
            "days_remaining": max(0, (earliest_completion - now).days),
            "expected_completion_date": earliest_completion.strftime("%Y-%m-%d"),
            "recommended_reminder_date": earliest_reminder.strftime("%Y-%m-%d"),
            "requires_notification": (overall_status in ("READY_FOR_REORDER", "OVERDUE")),
            "total_evaluated": len(evaluated_items),
            "evaluated_medicines": evaluated_items,
        }

        context.metadata["refill_report"] = refill_report

        if refill_report["requires_notification"]:
            context.add_recommendation(
                f"Proactive Refill Recommendation: Medication supply completes on {refill_report['expected_completion_date']}. Status: {overall_status}."
            )

        return context

    def _parse_daily_intake(self, frequency: str) -> float:
        """Parses frequency string into daily tablet/dose count."""
        f_norm = frequency.lower().strip()
        if "1-0-1" in f_norm or "bid" in f_norm or "twice" in f_norm or "bd" in f_norm:
            return 2.0
        if "1-1-1" in f_norm or "tid" in f_norm or "thrice" in f_norm or "three times" in f_norm:
            return 3.0
        if "qid" in f_norm or "four times" in f_norm or "1-1-1-1" in f_norm:
            return 4.0
        if "once" in f_norm or "od" in f_norm or "hs" in f_norm or "1-0-0" in f_norm or "0-0-1" in f_norm:
            return 1.0
        if "every 12" in f_norm:
            return 2.0
        if "every 8" in f_norm:
            return 3.0
        return 1.0

    def _calculate_supply_days(self, qty_str: str, duration_str: str, daily_intake: float) -> int:
        """Calculates total supply duration in days."""
        qty_match = re.search(r'(\d+)', qty_str)
        if qty_match and int(qty_match.group(1)) > 0:
            qty = int(qty_match.group(1))
            return max(1, int(qty / daily_intake))

        dur_match = re.search(r'(\d+)\s*(days?|weeks?|months?|d|w|m)', duration_str, re.IGNORECASE)
        if dur_match:
            num = int(dur_match.group(1))
            unit = dur_match.group(2).lower()
            if 'w' in unit:
                return num * 7
            if 'm' in unit:
                return num * 30
            return num

        return 10  # Default standard pack duration
