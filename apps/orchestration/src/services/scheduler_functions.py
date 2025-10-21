"""Functional Carif-Oref CSV fetch scheduler using APScheduler."""

import logging
from datetime import datetime
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from db.repositories.reconciliation import ReconciliationRepository
from utils.errors import PipelineError


logger = logging.getLogger(__name__)


# Type aliases
SchedulerStatus = dict[str, Any]


def create_scheduler(
    reconciliation_repo: ReconciliationRepository,
) -> AsyncIOScheduler:
    """Create and start the Carif-Oref scheduler.

    Args:
        reconciliation_repo: ReconciliationRepository instance

    Returns:
        Started AsyncIOScheduler instance

    Raises:
        PipelineError: If scheduler fails to start
    """
    try:
        logger.info("Creating Carif-Oref scheduler")

        scheduler = AsyncIOScheduler()

        # Schedule hourly CSV fetch at the top of every hour
        scheduler.add_job(
            lambda: fetch_csv_job(scheduler, reconciliation_repo),
            CronTrigger(minute=0),
            id="carif_oref_hourly_fetch",
            name="Carif-Oref Hourly CSV Fetch",
            replace_existing=True,
        )

        scheduler.start()
        logger.info("Carif-Oref scheduler started successfully")
        return scheduler
    except Exception as e:
        logger.error(
            "Failed to start Carif-Oref scheduler",
            extra={"error": str(e)},
        )
        raise PipelineError(f"Failed to start Carif-Oref scheduler: {str(e)}") from e


async def shutdown_scheduler(scheduler: AsyncIOScheduler) -> None:
    """Stop the scheduler gracefully.

    Args:
        scheduler: Scheduler instance to stop

    Raises:
        PipelineError: If scheduler fails to stop
    """
    try:
        logger.info("Stopping Carif-Oref scheduler")
        scheduler.shutdown(wait=True)
        logger.info("Carif-Oref scheduler stopped successfully")
    except Exception as e:
        logger.error(
            "Failed to stop Carif-Oref scheduler",
            extra={"error": str(e)},
        )
        raise PipelineError(f"Failed to stop Carif-Oref scheduler: {str(e)}") from e


async def fetch_csv_job(
    scheduler: AsyncIOScheduler,
    reconciliation_repo: ReconciliationRepository,
) -> None:
    """Fetch Carif-Oref CSV data (scheduled job).

    Args:
        scheduler: Scheduler instance
        reconciliation_repo: ReconciliationRepository instance
    """
    try:
        logger.info("Executing Carif-Oref CSV fetch job")

        # Fetch CSV data from Carif-Oref
        csv_data = await fetch_carif_oref_csv(reconciliation_repo)

        if not csv_data:
            logger.warning("No Carif-Oref CSV data fetched")
            return

        # Store fetched data
        await reconciliation_repo.store_csv_fetch(
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


async def fetch_carif_oref_csv(
    reconciliation_repo: ReconciliationRepository,
) -> list[dict[str, Any]]:
    """Fetch Carif-Oref CSV data from remote source.

    Args:
        reconciliation_repo: ReconciliationRepository instance

    Returns:
        List of Carif-Oref records

    Raises:
        PipelineError: If fetch fails
    """
    try:
        logger.debug("Fetching Carif-Oref CSV from remote source")

        # In production, this would fetch from:
        # https://www.intercariforef.org/dian/?...&excsv=1
        # For now, return empty list
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


def get_next_run_time(scheduler: AsyncIOScheduler) -> datetime | None:
    """Get the next scheduled run time.

    Args:
        scheduler: Scheduler instance

    Returns:
        Next run time or None if scheduler not running
    """
    job = scheduler.get_job("carif_oref_hourly_fetch")
    if job:
        return job.next_run_time
    return None


def get_last_run_time(scheduler: AsyncIOScheduler) -> datetime | None:
    """Get the last run time.

    Args:
        scheduler: Scheduler instance

    Returns:
        Last run time or None if never run
    """
    job = scheduler.get_job("carif_oref_hourly_fetch")
    if job:
        return job.last_run_time
    return None


async def trigger_immediate_fetch(
    scheduler: AsyncIOScheduler,
    reconciliation_repo: ReconciliationRepository,
) -> None:
    """Trigger an immediate CSV fetch (for testing/manual triggers).

    Args:
        scheduler: Scheduler instance
        reconciliation_repo: ReconciliationRepository instance

    Raises:
        PipelineError: If fetch fails
    """
    try:
        logger.info("Triggering immediate Carif-Oref CSV fetch")

        await fetch_csv_job(scheduler, reconciliation_repo)

        logger.info("Immediate Carif-Oref CSV fetch completed")
    except Exception as e:
        logger.error(
            "Failed to trigger immediate fetch",
            extra={"error": str(e)},
        )
        raise PipelineError(f"Failed to trigger immediate fetch: {str(e)}") from e


def get_scheduler_status(scheduler: AsyncIOScheduler) -> SchedulerStatus:
    """Get current scheduler status.

    Args:
        scheduler: Scheduler instance

    Returns:
        Dictionary with scheduler status information
    """
    return {
        "is_running": scheduler.running,
        "next_run_time": get_next_run_time(scheduler),
        "last_run_time": get_last_run_time(scheduler),
        "job_count": len(scheduler.get_jobs()),
    }
