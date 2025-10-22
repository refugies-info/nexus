"""Functional Carif-Oref CSV fetch scheduler using APScheduler.

Carif-Oref CSV Structure (from intercariforef.org DIAN export):
- ID formation: Unique formation identifier
- Intitule: Program title/name
- Debut: Start date (DD/MM/YYYY)
- Fin: End date (DD/MM/YYYY)
- Adressse de la formation: Training address
- Region: French region name
- Code Postal: Postal code
- Ville: City name
- Organisme responsable: Responsible organization
- Organisme formateur: Training organization
- Financeurs: Funding sources
- Tel: Contact phone number
"""

import csv
import io
import logging
from collections.abc import Callable
from datetime import datetime
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from db.repositories.reconciliation import ReconciliationRepository
from utils.errors import PipelineError


logger = logging.getLogger(__name__)


# Type aliases
SchedulerStatus = dict[str, Any]
FetchJob = Callable[[], Any]


async def create_scheduler(
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
            _fetch_csv_job,
            CronTrigger(minute=0),
            args=(reconciliation_repo,),
            id="carif_oref_hourly_fetch",
            name="Carif-Oref Hourly CSV Fetch",
            replace_existing=True,
        )

        scheduler.start()

        logger.info("Carif-Oref scheduler created and started successfully")
        return scheduler
    except Exception as e:
        logger.error(
            "Failed to create Carif-Oref scheduler",
            extra={"error": str(e)},
        )
        raise PipelineError(f"Failed to create Carif-Oref scheduler: {str(e)}") from e


async def shutdown_scheduler(scheduler: AsyncIOScheduler) -> None:
    """Stop the scheduler gracefully.

    Args:
        scheduler: AsyncIOScheduler instance to shutdown

    Raises:
        PipelineError: If scheduler fails to stop
    """
    try:
        logger.info("Stopping Carif-Oref scheduler")

        if scheduler:
            scheduler.shutdown(wait=True)

        logger.info("Carif-Oref scheduler stopped successfully")
    except Exception as e:
        logger.error(
            "Failed to stop Carif-Oref scheduler",
            extra={"error": str(e)},
        )
        raise PipelineError(f"Failed to stop Carif-Oref scheduler: {str(e)}") from e


def get_next_run_time(scheduler: AsyncIOScheduler) -> datetime | None:
    """Get the next scheduled run time.

    Args:
        scheduler: AsyncIOScheduler instance

    Returns:
        Next run time or None if scheduler not running
    """
    if not scheduler:
        return None

    job = scheduler.get_job("carif_oref_hourly_fetch")
    return job.next_run_time if job else None


def get_last_run_time(scheduler: AsyncIOScheduler) -> datetime | None:
    """Get the last run time.

    Args:
        scheduler: AsyncIOScheduler instance

    Returns:
        Last run time or None if never run
    """
    if not scheduler:
        return None

    job = scheduler.get_job("carif_oref_hourly_fetch")
    return job.last_run_time if job else None


async def trigger_immediate_fetch(
    repo: ReconciliationRepository,
) -> None:
    """Trigger an immediate CSV fetch (for testing/manual triggers).

    Args:
        repo: ReconciliationRepository instance

    Raises:
        PipelineError: If fetch fails
    """
    try:
        logger.info("Triggering immediate Carif-Oref CSV fetch")

        await _fetch_csv_job(repo)

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
        scheduler: AsyncIOScheduler instance

    Returns:
        Dictionary with scheduler status information
    """
    return {
        "is_running": scheduler.running if scheduler else False,
        "next_run_time": get_next_run_time(scheduler),
        "last_run_time": get_last_run_time(scheduler),
        "job_count": len(scheduler.get_jobs()) if scheduler else 0,
    }


# Pure helper functions


async def _fetch_csv_job(repo: ReconciliationRepository) -> None:
    """Fetch Carif-Oref CSV data (scheduled job).

    This function is called hourly by the scheduler.

    Args:
        repo: ReconciliationRepository instance
    """
    try:
        logger.info("Executing Carif-Oref CSV fetch job")

        # Fetch CSV data from Carif-Oref
        csv_data = await _fetch_carif_oref_csv()

        if not csv_data:
            logger.warning("No Carif-Oref CSV data fetched")
            return

        # Store fetched data
        await repo.store_csv_fetch(
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


async def _fetch_carif_oref_csv() -> list[dict[str, Any]]:
    """Fetch Carif-Oref CSV data from remote source.

    Returns:
        List of Carif-Oref records normalized to standard format

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


def parse_carif_oref_csv(csv_content: str) -> list[dict[str, Any]]:
    """Parse Carif-Oref CSV content into normalized records.

    Handles the DIAN export format from intercariforef.org with columns:
    ID formation, Intitule, Debut, Fin, Adressse de la formation,
    Region, Code Postal, Ville, Organisme responsable, Organisme formateur,
    Financeurs, Tel

    Args:
        csv_content: Raw CSV content as string

    Returns:
        List of normalized Carif-Oref records

    Raises:
        PipelineError: If parsing fails
    """
    try:
        records = []
        csv_file = io.StringIO(csv_content)
        reader = csv.DictReader(csv_file, delimiter=";")

        if not reader.fieldnames:
            logger.warning("Empty CSV file provided")
            return []

        for row in reader:
            # Normalize field names and values
            record = {
                "id_formation": row.get("ID formation", "").strip(),
                "name": row.get("Intitule", "").strip(),
                "start_date": row.get("Debut", "").strip(),
                "end_date": row.get("Fin", "").strip(),
                "address": row.get("Adressse de la formation", "").strip(),
                "region": row.get("Region", "").strip(),
                "postal_code": row.get("Code Postal", "").strip(),
                "city": row.get("Ville", "").strip(),
                "responsible_org": row.get("Organisme responsable", "").strip(),
                "training_org": row.get("Organisme formateur", "").strip(),
                "funders": row.get("Financeurs", "").strip(),
                "phone": row.get("Tel", "").strip(),
                "updated_at": datetime.utcnow().isoformat(),
            }

            # Only include records with essential fields
            if record["id_formation"] and record["name"]:
                records.append(record)

        logger.debug(
            "Carif-Oref CSV parsed successfully",
            extra={"record_count": len(records)},
        )

        return records
    except Exception as e:
        logger.error(
            "Failed to parse Carif-Oref CSV",
            extra={"error": str(e)},
        )
        raise PipelineError(f"Failed to parse Carif-Oref CSV: {str(e)}") from e
