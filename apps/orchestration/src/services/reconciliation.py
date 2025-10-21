"""Functional Carif-Oref reconciliation service for data merging and conflict detection."""

import logging
from typing import Any

from db.repositories.reconciliation import ReconciliationRepository
from utils.errors import PipelineError


logger = logging.getLogger(__name__)


# Type aliases
CarifOrefRecord = dict[str, Any]
ProgramData = dict[str, Any]
ReconciliationResult = dict[str, Any]
ConflictRecord = dict[str, Any]


async def fetch_carif_oref_csv() -> list[CarifOrefRecord]:
    """Fetch latest Carif-Oref CSV data.

    Returns:
        List of Carif-Oref program records

    Raises:
        PipelineError: If fetch fails
    """
    try:
        logger.info("Fetching Carif-Oref CSV data")

        # In production, this would fetch from:
        # https://www.intercariforef.org/dian/?...&excsv=1
        csv_data = []

        logger.info(
            "Carif-Oref CSV fetched",
            extra={"record_count": len(csv_data)},
        )

        return csv_data
    except Exception as e:
        logger.error(
            "Failed to fetch Carif-Oref CSV",
            extra={"error": str(e)},
        )
        raise PipelineError(f"Failed to fetch Carif-Oref CSV: {str(e)}") from e


def match_programs(
    program_data: ProgramData,
    csv_data: list[CarifOrefRecord],
) -> CarifOrefRecord | None:
    """Match a program with Carif-Oref data.

    Args:
        program_data: Program data from Data Inclusion
        csv_data: Carif-Oref CSV records

    Returns:
        Matching Carif-Oref record or None if no match
    """
    logger.debug(
        "Matching program with Carif-Oref data",
        extra={"program_id": program_data.get("id")},
    )

    structure_id = program_data.get("structure_id")
    service_id = program_data.get("service_id")

    if not structure_id or not service_id:
        logger.debug(
            "Missing structure_id or service_id for matching",
            extra={"program_id": program_data.get("id")},
        )
        return None

    for record in csv_data:
        if record.get("structure_id") == structure_id and record.get("service_id") == service_id:
            logger.debug(
                "Carif-Oref match found",
                extra={"program_id": program_data.get("id")},
            )
            return record

    logger.debug(
        "No Carif-Oref match found",
        extra={"program_id": program_data.get("id")},
    )
    return None


def merge_data(
    program_data: ProgramData,
    carif_oref_data: CarifOrefRecord | None,
) -> ProgramData:
    """Merge program data with Carif-Oref data.

    Args:
        program_data: Program data from Data Inclusion
        carif_oref_data: Matching Carif-Oref data (optional)

    Returns:
        Merged program data
    """
    logger.info(
        "Merging program data with Carif-Oref",
        extra={"program_id": program_data.get("id")},
    )

    merged_data = dict(program_data)

    if not carif_oref_data:
        logger.debug(
            "No Carif-Oref data to merge",
            extra={"program_id": program_data.get("id")},
        )
        return merged_data

    # Merge Carif-Oref data (takes precedence for overlapping fields)
    carif_oref_fields = [
        "name",
        "description",
        "address",
        "phone",
        "email",
        "website",
        "opening_hours",
    ]

    for field in carif_oref_fields:
        if field in carif_oref_data and carif_oref_data[field]:
            merged_data[f"carif_oref_{field}"] = carif_oref_data[field]

    merged_data["carif_oref_url"] = _build_carif_oref_url(carif_oref_data)

    logger.info(
        "Data merged successfully",
        extra={"program_id": program_data.get("id")},
    )

    return merged_data


def detect_conflicts(
    program_data: ProgramData,
    carif_oref_data: CarifOrefRecord | None,
) -> list[ConflictRecord]:
    """Detect conflicts between program data and Carif-Oref data.

    Args:
        program_data: Program data from Data Inclusion
        carif_oref_data: Matching Carif-Oref data (optional)

    Returns:
        List of detected conflicts
    """
    logger.info(
        "Detecting conflicts",
        extra={"program_id": program_data.get("id")},
    )

    conflicts = []

    if not carif_oref_data:
        logger.debug(
            "No Carif-Oref data for conflict detection",
            extra={"program_id": program_data.get("id")},
        )
        return conflicts

    conflict_fields = [
        "name",
        "description",
        "address",
        "phone",
        "email",
    ]

    for field in conflict_fields:
        data_inclusion_value = program_data.get(field, "").strip().lower()
        carif_oref_value = carif_oref_data.get(field, "").strip().lower()

        if data_inclusion_value and carif_oref_value and data_inclusion_value != carif_oref_value:
            conflicts.append(
                {
                    "field": field,
                    "data_inclusion_value": program_data.get(field),
                    "carif_oref_value": carif_oref_data.get(field),
                    "severity": _calculate_conflict_severity(field),
                }
            )

    logger.info(
        "Conflict detection completed",
        extra={
            "program_id": program_data.get("id"),
            "conflict_count": len(conflicts),
        },
    )

    return conflicts


def resolve_conflicts(
    program_data: ProgramData,
    carif_oref_data: CarifOrefRecord | None,
    conflicts: list[ConflictRecord],
) -> ProgramData:
    """Resolve conflicts using deterministic rules.

    Args:
        program_data: Program data from Data Inclusion
        carif_oref_data: Matching Carif-Oref data (optional)
        conflicts: List of detected conflicts

    Returns:
        Resolved program data
    """
    logger.info(
        "Resolving conflicts",
        extra={
            "program_id": program_data.get("id"),
            "conflict_count": len(conflicts),
        },
    )

    resolved_data = dict(program_data)

    if not carif_oref_data or not conflicts:
        return resolved_data

    for conflict in conflicts:
        field = conflict["field"]

        # Rule 1: Prefer Carif-Oref if more recent
        carif_oref_updated = carif_oref_data.get("updated_at")
        data_inclusion_updated = program_data.get("updated_at")

        if carif_oref_updated and data_inclusion_updated:
            if carif_oref_updated > data_inclusion_updated:
                resolved_data[field] = carif_oref_data[field]
                logger.debug(
                    "Conflict resolved: Carif-Oref is more recent",
                    extra={"field": field},
                )
                continue

        # Rule 2: Prefer Data Inclusion if more complete
        data_inclusion_completeness = _calculate_completeness(program_data)
        carif_oref_completeness = _calculate_completeness(carif_oref_data)

        if data_inclusion_completeness > carif_oref_completeness:
            logger.debug(
                "Conflict resolved: Data Inclusion is more complete",
                extra={"field": field},
            )
            continue

        # Default: Prefer Carif-Oref
        resolved_data[field] = carif_oref_data[field]
        logger.debug(
            "Conflict resolved: Using Carif-Oref (default)",
            extra={"field": field},
        )

    logger.info(
        "Conflicts resolved",
        extra={"program_id": program_data.get("id")},
    )

    return resolved_data


async def create_reconciliation_status(
    program_id: str,
    status: str,
    carif_oref_data: CarifOrefRecord | None,
    conflicts: list[ConflictRecord] | None,
    repo: ReconciliationRepository,
) -> dict[str, Any]:
    """Create a reconciliation status record.

    Args:
        program_id: ID of the program
        status: Reconciliation status
        carif_oref_data: Carif-Oref data used
        conflicts: Detected conflicts
        repo: Reconciliation repository

    Returns:
        Reconciliation status record

    Raises:
        PipelineError: If creation fails
    """
    try:
        logger.info(
            "Creating reconciliation status",
            extra={"program_id": program_id, "status": status},
        )

        record = await repo.create_reconciliation_status(
            program_id=program_id,
            status=status,
            carif_oref_data=carif_oref_data,
            conflicts=conflicts,
        )

        logger.info(
            "Reconciliation status created",
            extra={"program_id": program_id, "status": status},
        )

        return record
    except Exception as e:
        logger.error(
            "Failed to create reconciliation status",
            extra={"error": str(e), "program_id": program_id},
        )
        raise PipelineError(f"Failed to create reconciliation status: {str(e)}") from e


# Pure helper functions


def _build_carif_oref_url(carif_oref_data: CarifOrefRecord) -> str:
    """Build Carif-Oref website URL from data."""
    base_url = "https://www.intercariforef.org/dian"
    dept = carif_oref_data.get("department", "")
    structure_id = carif_oref_data.get("structure_id", "")
    service_id = carif_oref_data.get("service_id", "")
    name = carif_oref_data.get("name", "").replace(" ", "-").lower()

    if dept and structure_id and service_id:
        url = f"{base_url}/{dept}_{structure_id}/" f"{dept}_{service_id}/{name}"
        return url

    return base_url


def _calculate_conflict_severity(field: str) -> str:
    """Calculate severity of a conflict based on field."""
    critical_fields = ["name", "description"]
    high_fields = ["address", "phone", "email"]

    if field in critical_fields:
        return "critical"
    elif field in high_fields:
        return "high"
    else:
        return "medium"


def _calculate_completeness(data: dict[str, Any]) -> float:
    """Calculate data completeness score."""
    if not data:
        return 0.0

    important_fields = [
        "name",
        "description",
        "address",
        "phone",
        "email",
        "website",
    ]

    filled_fields = sum(
        1 for field in important_fields if data.get(field) and str(data.get(field)).strip()
    )

    return filled_fields / len(important_fields)
