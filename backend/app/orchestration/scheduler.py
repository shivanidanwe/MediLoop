"""
MediLoop Multi-Agent Orchestration Layer - Background Scheduler.
Runs background workers for independent agents:
- Refill Reminder Agent (evaluates patient order history and sends reminders).
- Procurement Agent (evaluates inventory depletion and drafts supplier POs).
Can run as an in-process asyncio task or standalone CLI background worker.
"""
import asyncio
import logging
from typing import Optional
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.orchestration.orchestrator import MultiAgentOrchestrator

logger = logging.getLogger(__name__)

# Configurable intervals in seconds
DEFAULT_REFILL_INTERVAL_SECONDS = 3600 * 12  # Run twice daily
DEFAULT_PROCUREMENT_INTERVAL_SECONDS = 3600 * 6  # Run every 6 hours


class OrchestrationBackgroundScheduler:
    """
    Background Task Scheduler for MediLoop Autonomous Workers.
    """
    def __init__(
        self,
        refill_interval: int = DEFAULT_REFILL_INTERVAL_SECONDS,
        procurement_interval: int = DEFAULT_PROCUREMENT_INTERVAL_SECONDS
    ):
        self.refill_interval = refill_interval
        self.procurement_interval = procurement_interval
        self._running = False
        self._tasks = []

    async def start(self):
        """Starts background loops."""
        self._running = True
        logger.info(
            f"Orchestration Scheduler started. "
            f"Refill interval: {self.refill_interval}s, "
            f"Procurement interval: {self.procurement_interval}s."
        )
        self._tasks.append(asyncio.create_task(self._refill_loop()))
        self._tasks.append(asyncio.create_task(self._procurement_loop()))

    async def stop(self):
        """Stops background loops gracefully."""
        self._running = False
        for task in self._tasks:
            task.cancel()
        logger.info("Orchestration Scheduler stopped.")

    async def _refill_loop(self):
        """Periodic runner for Refill Reminder Agent."""
        while self._running:
            try:
                db: Session = SessionLocal()
                try:
                    logger.info("[Scheduler] Triggering periodic Refill Reminder Agent...")
                    orchestrator = MultiAgentOrchestrator(db)
                    predictions = await orchestrator.run_refill_reminder_worker()
                    logger.info(f"[Scheduler] Refill Reminder Agent evaluated {len(predictions)} medication schedules.")
                finally:
                    db.close()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[Scheduler] Refill Reminder loop error: {e}")

            await asyncio.sleep(self.refill_interval)

    async def _procurement_loop(self):
        """Periodic runner for Procurement Agent."""
        while self._running:
            try:
                db: Session = SessionLocal()
                try:
                    logger.info("[Scheduler] Triggering periodic Procurement Agent...")
                    orchestrator = MultiAgentOrchestrator(db)
                    # Run for default pharmacy #1
                    proc_summary = await orchestrator.run_procurement_worker(pharmacy_id=1)
                    logger.info(
                        f"[Scheduler] Procurement Agent status: {proc_summary.status}, "
                        f"Items below threshold: {proc_summary.total_items}."
                    )
                finally:
                    db.close()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[Scheduler] Procurement loop error: {e}")

            await asyncio.sleep(self.procurement_interval)


scheduler_instance = OrchestrationBackgroundScheduler()


def get_orchestration_scheduler() -> OrchestrationBackgroundScheduler:
    return scheduler_instance

