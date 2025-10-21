"""Functional workflow state machine enforcing pipeline stage sequence."""

import logging
from enum import Enum
from typing import Any

from utils.errors import PipelineError


logger = logging.getLogger(__name__)


class PipelineStage(str, Enum):
    """Pipeline stages in order."""

    INGESTION = "ingestion"
    EDITORIAL_POLICY_VALIDATION = "editorial_policy_validation"
    RECONCILIATION = "reconciliation"
    ENRICHMENT = "enrichment"
    LANGAGE_CLAIR = "langage_clair"
    TRANSLATION = "translation"
    VALIDATION = "validation"
    PUBLICATION = "publication"


# Ordered list of stages
STAGE_SEQUENCE = [
    PipelineStage.INGESTION,
    PipelineStage.EDITORIAL_POLICY_VALIDATION,
    PipelineStage.RECONCILIATION,
    PipelineStage.ENRICHMENT,
    PipelineStage.LANGAGE_CLAIR,
    PipelineStage.TRANSLATION,
    PipelineStage.VALIDATION,
    PipelineStage.PUBLICATION,
]

# Create stage-to-index mapping
STAGE_TO_INDEX = {stage: idx for idx, stage in enumerate(STAGE_SEQUENCE)}

# Type aliases
StageIndex = int
WorkflowState = dict[str, Any]


def validate_stage_transition(
    current_stage: str,
    next_stage: str,
) -> bool:
    """Validate that a stage transition is allowed.

    Args:
        current_stage: Current stage name
        next_stage: Requested next stage name

    Returns:
        True if transition is valid

    Raises:
        PipelineError: If transition is invalid
    """
    try:
        current_idx = STAGE_TO_INDEX.get(current_stage)
        next_idx = STAGE_TO_INDEX.get(next_stage)

        if current_idx is None:
            logger.error(
                "Invalid current stage",
                extra={"current_stage": current_stage},
            )
            raise PipelineError(f"Invalid current stage: {current_stage}")

        if next_idx is None:
            logger.error(
                "Invalid next stage",
                extra={"next_stage": next_stage},
            )
            raise PipelineError(f"Invalid next stage: {next_stage}")

        # Next stage must be exactly one position ahead
        if next_idx != current_idx + 1:
            logger.error(
                "Invalid stage transition",
                extra={
                    "current_stage": current_stage,
                    "next_stage": next_stage,
                    "current_idx": current_idx,
                    "next_idx": next_idx,
                },
            )
            expected_stage = STAGE_SEQUENCE[current_idx + 1].value
            raise PipelineError(
                f"Cannot transition from {current_stage} to {next_stage}. "
                f"Next stage must be {expected_stage}"
            )

        logger.debug(
            "Stage transition validated",
            extra={"current_stage": current_stage, "next_stage": next_stage},
        )
        return True
    except PipelineError:
        raise
    except Exception as e:
        logger.error(
            "Failed to validate stage transition",
            extra={
                "error": str(e),
                "current_stage": current_stage,
                "next_stage": next_stage,
            },
        )
        raise PipelineError(f"Failed to validate stage transition: {str(e)}") from e


def get_next_stage(current_stage: str) -> str:
    """Get the next stage in the sequence.

    Args:
        current_stage: Current stage name

    Returns:
        Next stage name

    Raises:
        PipelineError: If current stage is invalid or is the last stage
    """
    try:
        current_idx = STAGE_TO_INDEX.get(current_stage)

        if current_idx is None:
            logger.error(
                "Invalid current stage",
                extra={"current_stage": current_stage},
            )
            raise PipelineError(f"Invalid current stage: {current_stage}")

        if current_idx >= len(STAGE_SEQUENCE) - 1:
            logger.error(
                "No next stage available",
                extra={"current_stage": current_stage},
            )
            raise PipelineError(f"No next stage after {current_stage}. Pipeline complete.")

        next_stage = STAGE_SEQUENCE[current_idx + 1].value
        logger.debug(
            "Next stage determined",
            extra={"current_stage": current_stage, "next_stage": next_stage},
        )
        return next_stage
    except PipelineError:
        raise
    except Exception as e:
        logger.error(
            "Failed to get next stage",
            extra={"error": str(e), "current_stage": current_stage},
        )
        raise PipelineError(f"Failed to get next stage: {str(e)}") from e


def is_valid_stage(stage: str) -> bool:
    """Check if a stage is valid.

    Args:
        stage: Stage name to validate

    Returns:
        True if stage is valid, False otherwise
    """
    return stage in STAGE_TO_INDEX


def is_final_stage(stage: str) -> bool:
    """Check if a stage is the final stage.

    Args:
        stage: Stage name to check

    Returns:
        True if stage is the final stage (publication)
    """
    return stage == PipelineStage.PUBLICATION.value


def get_stage_index(stage: str) -> StageIndex:
    """Get the index of a stage in the sequence.

    Args:
        stage: Stage name

    Returns:
        Index of the stage (0-based)

    Raises:
        PipelineError: If stage is invalid
    """
    try:
        idx = STAGE_TO_INDEX.get(stage)

        if idx is None:
            logger.error(
                "Invalid stage",
                extra={"stage": stage},
            )
            raise PipelineError(f"Invalid stage: {stage}")

        return idx
    except PipelineError:
        raise
    except Exception as e:
        logger.error(
            "Failed to get stage index",
            extra={"error": str(e), "stage": stage},
        )
        raise PipelineError(f"Failed to get stage index: {str(e)}") from e


def get_remaining_stages(current_stage: str) -> list[str]:
    """Get all remaining stages after the current stage.

    Args:
        current_stage: Current stage name

    Returns:
        List of remaining stage names

    Raises:
        PipelineError: If current stage is invalid
    """
    try:
        current_idx = STAGE_TO_INDEX.get(current_stage)

        if current_idx is None:
            logger.error(
                "Invalid current stage",
                extra={"current_stage": current_stage},
            )
            raise PipelineError(f"Invalid current stage: {current_stage}")

        remaining = [stage.value for stage in STAGE_SEQUENCE[current_idx + 1 :]]

        logger.debug(
            "Remaining stages determined",
            extra={
                "current_stage": current_stage,
                "remaining_count": len(remaining),
            },
        )
        return remaining
    except PipelineError:
        raise
    except Exception as e:
        logger.error(
            "Failed to get remaining stages",
            extra={"error": str(e), "current_stage": current_stage},
        )
        raise PipelineError(f"Failed to get remaining stages: {str(e)}") from e


def get_all_stages() -> list[str]:
    """Get all stages in the pipeline.

    Returns:
        List of all stage names in order
    """
    return [stage.value for stage in STAGE_SEQUENCE]


def get_stage_count() -> int:
    """Get the total number of stages.

    Returns:
        Total number of stages
    """
    return len(STAGE_SEQUENCE)


def validate_workflow_state(
    current_stage: str,
    metadata: dict[str, Any] | None = None,
) -> WorkflowState:
    """Validate and get detailed workflow state information.

    Args:
        current_stage: Current stage name
        metadata: Optional workflow metadata

    Returns:
        Dictionary with state information

    Raises:
        PipelineError: If current stage is invalid
    """
    try:
        if not is_valid_stage(current_stage):
            logger.error(
                "Invalid stage in workflow state",
                extra={"current_stage": current_stage},
            )
            raise PipelineError(f"Invalid stage: {current_stage}")

        current_idx = get_stage_index(current_stage)
        is_final = is_final_stage(current_stage)
        remaining = get_remaining_stages(current_stage) if not is_final else []

        state_info: WorkflowState = {
            "current_stage": current_stage,
            "current_index": current_idx,
            "total_stages": get_stage_count(),
            "progress_percentage": int((current_idx + 1) / get_stage_count() * 100),
            "is_final_stage": is_final,
            "remaining_stages": remaining,
            "remaining_count": len(remaining),
        }

        if metadata:
            state_info["metadata"] = metadata

        logger.debug(
            "Workflow state validated",
            extra={
                "current_stage": current_stage,
                "progress": state_info["progress_percentage"],
            },
        )

        return state_info
    except PipelineError:
        raise
    except Exception as e:
        logger.error(
            "Failed to validate workflow state",
            extra={"error": str(e), "current_stage": current_stage},
        )
        raise PipelineError(f"Failed to validate workflow state: {str(e)}") from e
