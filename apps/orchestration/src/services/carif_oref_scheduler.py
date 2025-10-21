"""Carif-Oref CSV fetch scheduler using APScheduler."""

import logging
from datetime import datetime
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from db.repositories.reconciliation import ReconciliationRepository
from utils.errors import PipelineError


logger = logging.getLogger(__name__)


class CarifOrefScheduler:
    """Scheduler for hourly Carif-Oref CSV fetches."""

    def __init__(self, reconciliation_repo: ReconciliationRepository):
        """Initialize Carif-Oref scheduler.

        Args:
            reconciliation_repo: ReconciliationRepository instance
        """
        self.reconciliation_repo = reconciliation_repo
        self.scheduler: AsyncIOScheduler | None = None
        self.is_running = False

    async def start(self) -> None:
        """Start the scheduler.

        Raises:
            PipelineError: If scheduler fails to start
        """
        try:
            logger.info("Starting Carif-Oref scheduler")

            self.scheduler = AsyncIOScheduler()

            # Schedule hourly CSV fetch at the top of every hour
            self.scheduler.add_job(
                self._fetch_csv_job,
                CronTrigger(minute=0),
                id="carif_oref_hourly_fetch",
                name="Carif-Oref Hourly CSV Fetch",
                replace_existing=True,
            )

            self.scheduler.start()
            self.is_running = True

            logger.info("Carif-Oref scheduler started successfully")
        except Exception as e:
            logger.error(
                "Failed to start Carif-Oref scheduler",
                extra={"error": str(e)},
            )
            raise PipelineError(f"Failed to start Carif-Oref scheduler: {str(e)}") from e

    async def stop(self) -> None:
        """Stop the scheduler.

        Raises:
            PipelineError: If scheduler fails to stop
        """
        try:
            logger.info("Stopping Carif-Oref scheduler")

            if self.scheduler and self.is_running:
                self.scheduler.shutdown(wait=True)
                self.is_running = False

            logger.info("Carif-Oref scheduler stopped successfully")
        except Exception as e:
            logger.error(
                "Failed to stop Carif-Oref scheduler",
                extra={"error": str(e)},
            )
            raise PipelineError(f"Failed to stop Carif-Oref scheduler: {str(e)}") from e

    async def _fetch_csv_job(self) -> None:
        """Fetch Carif-Oref CSV data (scheduled job).

        This method is called hourly by the scheduler.
        """
        try:
            logger.info("Executing Carif-Oref CSV fetch job")

            # Fetch CSV data from Carif-Oref
            csv_data = await self._fetch_carif_oref_csv()

            if not csv_data:
                logger.warning("No Carif-Oref CSV data fetched")
                return

            # Store fetched data
            await self.reconciliation_repo.store_csv_fetch(
                csv_data=csv_data,
                fetch_date=datetime.utcnow(),
            )

            logger.info(
                "Carif-Oref CSV fetch job completed",
                extra={"record_count": len(csv_data)},
            )
        except Exception as e:
            logger.error(
                "Carif-Oref CSV fetch job failed",
                extra={"error": str(e)},
            )
            # Don't raise - scheduler should continue running

    async def _fetch_carif_oref_csv(self) -> list[dict[str, Any]]:
        """Fetch Carif-Oref CSV data from remote source.

        Returns:
            List of Carif-Oref records

        Raises:
            PipelineError: If fetch fails
        """
        try:
            logger.debug("Fetching Carif-Oref CSV from remote source")

            # In production, this would fetch from:
            # https://www.intercariforef.org/dian/?...&excsv=1
            # For now, return empty list (would be implemented with httpx or requests)

            csv_data = []

            logger.debug(
                "Carif-Oref CSV fetched from remote",
                extra={"record_count": len(csv_data)},
            )

            return csv_data
        except Exception as e:
            logger.error(
                "Failed to fetch Carif-Oref CSV from remote",
                extra={"error": str(e)},
            )
            raise PipelineError(f"Failed to fetch Carif-Oref CSV: {str(e)}") from e

    def get_next_run_time(self) -> datetime | None:
        """Get the next scheduled run time.

        Returns:
            Next run time or None if scheduler not running
        """
        if not self.scheduler or not self.is_running:
            return None

        job = self.scheduler.get_job("carif_oref_hourly_fetch")
        if job:
            return job.next_run_time

        return None

    def get_last_run_time(self) -> datetime | None:
        """Get the last run time.

        Returns:
            Last run time or None if never run
        """
        if not self.scheduler or not self.is_running:
            return None

        job = self.scheduler.get_job("carif_oref_hourly_fetch")
        if job:
            return job.last_run_time

        return None

    async def trigger_immediate_fetch(self) -> None:
        """Trigger an immediate CSV fetch (for testing/manual triggers).

        Raises:
            PipelineError: If fetch fails
        """
        try:
            logger.info("Triggering immediate Carif-Oref CSV fetch")

            await self._fetch_csv_job()

            logger.info("Immediate Carif-Oref CSV fetch completed")
        except Exception as e:
            logger.error(
                "Failed to trigger immediate fetch",
                extra={"error": str(e)},
            )
            raise PipelineError(f"Failed to trigger immediate fetch: {str(e)}") from e

    def get_scheduler_status(self) -> dict[str, Any]:
        """Get current scheduler status.

        Returns:
            Dictionary with scheduler status information
        """
        return {
            "is_running": self.is_running,
            "next_run_time": self.get_next_run_time(),
            "last_run_time": self.get_last_run_time(),
            "job_count": len(self.scheduler.get_jobs()) if self.scheduler else 0,
        }
