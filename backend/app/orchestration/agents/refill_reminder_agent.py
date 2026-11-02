"""
MediLoop Multi-Agent Orchestration Layer - Agent 5: Refill Reminder Agent.
Independent background worker evaluating historical completed orders:
- Calculates days of medication supply: floor(quantity / daily_usage).
- Estimates exhaustion and expected refill dates.
- Detects medicines nearing depletion (e.g. <= 7 days, <= 3 days, due today).
- Enforces strict deduplication via refill_reminder_history table.
- Dispatches notification events to patient notifications table.
"""
import time
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.order import Order, OrderItem, OrderStatus
from app.models.medicine import Medicine
from app.models.notification import Notification
from app.models.orchestration import RefillPredictionModel, RefillReminderHistoryModel
from app.schemas.orchestration import RefillPredictionSchema

logger = logging.getLogger(__name__)


class RefillReminderAgent:
    """
    Agent 5: Refill Reminder Agent
    Autonomous background worker calculating patient refill schedules and dispatching reminders.
    """
    AGENT_ID = "refill_reminder_agent"
    VERSION = "2.0.0"

    def __init__(self, db: Session, reminder_threshold_days: int = 7):
        self.db = db
        self.reminder_threshold_days = reminder_threshold_days

    async def execute(self, patient_id: Optional[int] = None) -> List[RefillPredictionSchema]:
        """
        Evaluates completed patient orders, calculates refill dates,
        deduplicates, and sends reminders.
        If patient_id is provided, evaluates only that patient; otherwise evaluates all active patients.
        """
        start_time = time.perf_counter()
        now = datetime.now(timezone.utc)

        # Step 1: Query completed, delivered, or confirmed orders
        eligible_statuses = [
            OrderStatus.DELIVERED,
            OrderStatus.ACCEPTED,
            "DELIVERED",
            "CONFIRMED",
            "ACCEPTED"
        ]

        query = self.db.query(Order).filter(
            Order.order_status.in_(eligible_statuses)
        )
        if patient_id:
            query = query.filter(Order.customer_id == patient_id)

        orders = query.order_by(Order.placed_at.desc()).all()

        evaluated_predictions: List[RefillPredictionSchema] = []
        # Track most recent order per (customer_id, medicine_id)
        latest_orders_by_med: Dict[str, Dict[str, Any]] = {}

        for ord_obj in orders:
            order_date = ord_obj.placed_at or ord_obj.updated_at or now
            for item in ord_obj.items:
                if not item.medicine_id:
                    continue
                med_key = f"{ord_obj.customer_id}_{item.medicine_id}"
                if med_key not in latest_orders_by_med:
                    latest_orders_by_med[med_key] = {
                        "customer_id": ord_obj.customer_id,
                        "medicine_id": item.medicine_id,
                        "quantity": item.quantity,
                        "order_date": order_date,
                        "medicine": item.medicine
                    }

        # Step 2: Compute refill predictions for each active medication
        for key, record in latest_orders_by_med.items():
            cust_id = record["customer_id"]
            med_id = record["medicine_id"]
            ordered_qty = record["quantity"]
            order_dt = record["order_date"]
            med = record["medicine"]
            med_name = med.brand_name if med else f"Medicine #{med_id}"

            # Standard assumed daily usage rate: 2.0 (e.g. morning + evening) unless specified
            daily_usage = 2.0
            days_supply = max(1, int(ordered_qty / daily_usage))
            expected_refill_date = order_dt + timedelta(days=days_supply)

            remaining_days = (expected_refill_date.date() - now.date()).days

            # Only process if within reminder threshold window or overdue up to 14 days
            if remaining_days > self.reminder_threshold_days or remaining_days < -14:
                continue

            # Determine reminder type
            if remaining_days < 0:
                reminder_type = "OVERDUE"
                reminder_text = f"Your supply of {med_name} was estimated to end {abs(remaining_days)} days ago. Please reorder to stay on track."
            elif remaining_days == 0:
                reminder_type = "DUE_TODAY"
                reminder_text = f"Your supply of {med_name} is estimated to run out today. Place your refill order now."
            elif remaining_days <= 3:
                reminder_type = "3_DAYS_BEFORE"
                reminder_text = f"You have approximately 3 days of {med_name} remaining. Time to schedule your refill."
            else:
                reminder_type = "7_DAYS_BEFORE"
                reminder_text = f"Refill reminder: Your supply of {med_name} will run out in about {remaining_days} days."

            # Step 3: Check Deduplication in refill_reminder_history
            dedup_date_str = expected_refill_date.strftime("%Y%m%d")
            dedup_key = f"refill_{cust_id}_{med_id}_{reminder_type}_{dedup_date_str}"

            already_sent = self.db.query(RefillReminderHistoryModel).filter(
                RefillReminderHistoryModel.deduplication_key == dedup_key
            ).first()

            # Record or update RefillPredictionModel
            prediction_rec = self.db.query(RefillPredictionModel).filter(
                RefillPredictionModel.patient_id == cust_id,
                RefillPredictionModel.medicine_id == med_id,
                RefillPredictionModel.is_active == True
            ).first()

            if not prediction_rec:
                prediction_rec = RefillPredictionModel(
                    patient_id=cust_id,
                    medicine_id=med_id,
                    medicine_name=med_name,
                    last_order_date=order_dt,
                    last_ordered_quantity=ordered_qty,
                    daily_usage_rate=daily_usage,
                    estimated_remaining_days=remaining_days,
                    expected_refill_date=expected_refill_date,
                    confidence=0.92,
                    reason=f"Calculated supply: {ordered_qty} units at {daily_usage} doses/day.",
                    is_active=True
                )
                self.db.add(prediction_rec)
                self.db.commit()
                self.db.refresh(prediction_rec)
            else:
                prediction_rec.last_order_date = order_dt
                prediction_rec.last_ordered_quantity = ordered_qty
                prediction_rec.estimated_remaining_days = remaining_days
                prediction_rec.expected_refill_date = expected_refill_date
                self.db.commit()

            # Step 4: Dispatch Notification if not already sent
            notification_id = None
            if not already_sent:
                notif = Notification(
                    user_id=cust_id,
                    title="Medication Refill Reminder",
                    message=reminder_text,
                    notification_type="REFILL_REMINDER",
                    is_read=False,
                    action_url=f"/orders/refill/{med_id}"
                )
                self.db.add(notif)
                self.db.commit()
                self.db.refresh(notif)
                notification_id = notif.id

                # Save history record
                history_rec = RefillReminderHistoryModel(
                    prediction_id=prediction_rec.id,
                    patient_id=cust_id,
                    medicine_id=med_id,
                    reminder_type=reminder_type,
                    notification_id=notification_id,
                    deduplication_key=dedup_key
                )
                self.db.add(history_rec)
                self.db.commit()
                logger.info(f"Refill reminder dispatched to patient #{cust_id} for {med_name} ({reminder_type}).")

            evaluated_predictions.append(RefillPredictionSchema(
                id=prediction_rec.id,
                patient_id=cust_id,
                medicine_id=med_id,
                medicine_name=med_name,
                last_order_date=order_dt,
                last_ordered_quantity=ordered_qty,
                daily_usage_rate=daily_usage,
                estimated_remaining_days=remaining_days,
                expected_refill_date=expected_refill_date,
                confidence=0.92,
                reason=prediction_rec.reason,
                is_active=True,
                reminder_sent=bool(already_sent or notification_id),
                reminder_type=reminder_type
            ))

        return evaluated_predictions
