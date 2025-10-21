"""Reconciliation API endpoints."""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from db.repositories.reconciliation import ReconciliationRepository
from services.reconciliation import (
    detect_conflicts,
    fetch_carif_oref_csv,
    match_programs,
    resolve_conflicts,
)
from utils.errors import PipelineError


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reconciliation", tags=["reconciliation"])


# Dependencies
def get_reconciliation_repository() -> ReconciliationRepository:
    """Get reconciliation repository instance."""
    return ReconciliationRepository()


@router.post("/process", status_code=status.HTTP_200_OK)
async def reconcile_program(
    program_id: str,
    program_data: dict[str, Any],
    reconciliation_repo: ReconciliationRepository = Depends(  # noqa: B008
        get_reconciliation_repository
    ),
) -> dict[str, Any]:
    """Reconcile a program with Carif-Oref data.

    Args:
        program_id: Unique program identifier
        program_data: Program data from Data Inclusion
        reconciliation_repo: Reconciliation repository instance

    Returns:
        Reconciliation result with merged data and conflicts

    Raises:
        HTTPException: If reconciliation fails
    """
    try:
        logger.info(
            "Starting program reconciliation",
            extra={"program_id": program_id},
        )

        # Fetch Carif-Oref CSV data
        csv_data = await fetch_carif_oref_csv(reconciliation_repo)

        # Match program with Carif-Oref data
        carif_oref_data = await match_programs(
            reconciliation_repo=reconciliation_repo,
            program_data=program_data,
            csv_data=csv_data,
        )

        # Detect conflicts
        conflicts = await detect_conflicts(
            program_data=program_data,
            carif_oref_data=carif_oref_data,
        )

        # Resolve conflicts
        resolved_data = await resolve_conflicts(
            program_data=program_data,
            carif_oref_data=carif_oref_data,
            conflicts=conflicts,
        )

        # Determine reconciliation status
        if carif_oref_data and not conflicts:
            status_value = "fully_reconciled"
        elif carif_oref_data and conflicts:
            status_value = "data_conflict"
        elif carif_oref_data:
            status_value = "partially_reconciled"
        else:
            status_value = "no_match"

        # Store reconciliation status
        status_record = await reconciliation_repo.create_reconciliation_status(
            program_id=program_id,
            status=status_value,
            carif_oref_data=carif_oref_data,
            conflicts=conflicts,
        )

        logger.info(
            "Program reconciliation completed",
            extra={
                "program_id": program_id,
                "status": status_value,
                "conflict_count": len(conflicts),
            },
        )

        return {
            "program_id": program_id,
            "status_id": status_record.get("id"),
            "reconciliation_status": status_value,
            "merged_data": resolved_data,
            "conflicts": conflicts,
            "carif_oref_matched": carif_oref_data is not None,
        }

    except PipelineError as e:
        logger.error(
            "Reconciliation failed",
            extra={"program_id": program_id, "error": str(e)},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Reconciliation failed: {str(e)}",
        ) from e
    except Exception as e:
        logger.error(
            "Unexpected error during reconciliation",
            extra={"program_id": program_id, "error": str(e)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during reconciliation",
        ) from e


@router.get("/status/{program_id}", status_code=status.HTTP_200_OK)
async def get_reconciliation_status(
    program_id: str,
    reconciliation_repo: ReconciliationRepository = Depends(  # noqa: B008
        get_reconciliation_repository
    ),
) -> dict[str, Any]:
    """Get the reconciliation status for a program.

    Args:
        program_id: Unique program identifier
        reconciliation_repo: Reconciliation repository instance

    Returns:
        Reconciliation status record

    Raises:
        HTTPException: If status not found or retrieval fails
    """
    try:
        logger.debug(
            "Retrieving reconciliation status",
            extra={"program_id": program_id},
        )

        status_record = await reconciliation_repo.get_reconciliation_status(program_id)

        if not status_record:
            logger.warning(
                "Reconciliation status not found",
                extra={"program_id": program_id},
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No reconciliation status found for program {program_id}",
            )

        logger.debug(
            "Reconciliation status retrieved",
            extra={"program_id": program_id},
        )

        return status_record

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to retrieve reconciliation status",
            extra={"program_id": program_id, "error": str(e)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error retrieving reconciliation status",
        ) from e
