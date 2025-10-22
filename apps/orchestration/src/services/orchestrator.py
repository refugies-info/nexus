"""Functional stage executor for calling external stage services."""

import logging
from collections.abc import Callable
from typing import Any

from services.state_machine import (
    get_all_stages,
    get_next_stage,
    is_final_stage,
    is_valid_stage,
)
from utils.errors import PipelineError


logger = logging.getLogger(__name__)


# Type aliases
StageHandler = Callable[[str, dict[str, Any], dict[str, Any] | None], Any]
StageHandlers = dict[str, StageHandler]


def register_stage_handler(
    handlers: StageHandlers,
    stage_name: str,
    handler: StageHandler,
) -> StageHandlers:
    """Register a handler for a specific stage.

    Args:
        handlers: Current handlers dictionary
        stage_name: Name of the stage
        handler: Async callable that executes the stage

    Returns:
        Updated handlers dictionary

    Raises:
        PipelineError: If stage is invalid
    """
    if not is_valid_stage(stage_name):
        logger.error(
            "Attempted to register handler for invalid stage",
            extra={"stage_name": stage_name},
        )
        raise PipelineError(f"Invalid stage: {stage_name}")

    handlers[stage_name] = handler
    logger.info(
        "Stage handler registered",
        extra={"stage_name": stage_name, "handler": handler.__name__},
    )
    return handlers


def has_handler(handlers: StageHandlers, stage_name: str) -> bool:
    """Check if a handler is registered for a stage.

    Args:
        handlers: Current handlers dictionary
        stage_name: Name of the stage

    Returns:
        True if handler is registered
    """
    return stage_name in handlers


async def execute_stage(
    handlers: StageHandlers,
    stage_name: str,
    program_id: str,
    data: dict[str, Any],
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute a pipeline stage.

    Args:
        handlers: Current handlers dictionary
        stage_name: Name of the stage to execute
        program_id: ID of the program being processed
        data: Input data for the stage
        metadata: Optional metadata about the execution

    Returns:
        Result from the stage execution

    Raises:
        PipelineError: If stage execution fails
    """
    try:
        if not is_valid_stage(stage_name):
            logger.error(
                "Attempted to execute invalid stage",
                extra={"stage_name": stage_name, "program_id": program_id},
            )
            raise PipelineError(f"Invalid stage: {stage_name}")

        if not has_handler(handlers, stage_name):
            logger.warning(
                "No handler registered for stage, returning placeholder result",
                extra={"stage_name": stage_name, "program_id": program_id},
            )
            # Return placeholder result for unimplemented stages
            return {
                "stage": stage_name,
                "program_id": program_id,
                "status": "placeholder",
                "message": f"Placeholder execution for {stage_name}",
            }

        logger.info(
            "Executing stage",
            extra={
                "stage_name": stage_name,
                "program_id": program_id,
            },
        )

        handler = handlers[stage_name]
        result = await handler(
            program_id=program_id,
            data=data,
            metadata=metadata,
        )

        logger.info(
            "Stage executed successfully",
            extra={
                "stage_name": stage_name,
                "program_id": program_id,
            },
        )

        return result
    except PipelineError:
        raise
    except Exception as e:
        logger.error(
            "Failed to execute stage",
            extra={
                "error": str(e),
                "stage_name": stage_name,
                "program_id": program_id,
            },
        )
        raise PipelineError(f"Failed to execute stage {stage_name}: {str(e)}") from e


async def execute_stage_sequence(
    handlers: StageHandlers,
    starting_stage: str,
    program_id: str,
    data: dict[str, Any],
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute a sequence of stages from a starting point.

    Args:
        handlers: Current handlers dictionary
        starting_stage: Stage to start from
        program_id: ID of the program being processed
        data: Input data for the first stage
        metadata: Optional metadata about the execution

    Returns:
        Result from the final stage executed

    Raises:
        PipelineError: If any stage execution fails
    """
    try:
        if not is_valid_stage(starting_stage):
            logger.error(
                "Invalid starting stage",
                extra={"starting_stage": starting_stage, "program_id": program_id},
            )
            raise PipelineError(f"Invalid starting stage: {starting_stage}")

        logger.info(
            "Starting stage sequence",
            extra={
                "starting_stage": starting_stage,
                "program_id": program_id,
            },
        )

        current_stage = starting_stage
        current_data = data
        final_result = None

        while current_stage:
            # Execute current stage
            result = await execute_stage(
                handlers,
                current_stage,
                program_id,
                current_data,
                metadata,
            )

            final_result = result

            # Check if this is the final stage
            if is_final_stage(current_stage):
                logger.info(
                    "Pipeline completed",
                    extra={"program_id": program_id, "final_stage": current_stage},
                )
                break

            # Get next stage
            try:
                current_stage = get_next_stage(current_stage)
                # Use result as input for next stage
                current_data = result.get("data", current_data)
            except PipelineError:
                # No more stages
                break

        return final_result or {}
    except PipelineError:
        raise
    except Exception as e:
        logger.error(
            "Failed to execute stage sequence",
            extra={
                "error": str(e),
                "starting_stage": starting_stage,
                "program_id": program_id,
            },
        )
        raise PipelineError(f"Failed to execute stage sequence: {str(e)}") from e


def get_registered_stages(handlers: StageHandlers) -> list[str]:
    """Get list of registered stage handlers.

    Args:
        handlers: Current handlers dictionary

    Returns:
        List of stage names with registered handlers
    """
    return list(handlers.keys())


def get_unregistered_stages(handlers: StageHandlers) -> list[str]:
    """Get list of stages without registered handlers.

    Args:
        handlers: Current handlers dictionary

    Returns:
        List of stage names without handlers
    """
    all_stages = get_all_stages()
    registered = set(handlers.keys())
    return [stage for stage in all_stages if stage not in registered]


def get_handler_status(handlers: StageHandlers) -> dict[str, Any]:
    """Get status of all stage handlers.

    Args:
        handlers: Current handlers dictionary

    Returns:
        Dictionary with handler registration status
    """
    all_stages = get_all_stages()
    status = {
        "total_stages": len(all_stages),
        "registered_count": len(handlers),
        "unregistered_count": len(all_stages) - len(handlers),
        "registered_stages": get_registered_stages(handlers),
        "unregistered_stages": get_unregistered_stages(handlers),
    }

    logger.debug(
        "Handler status retrieved",
        extra={
            "registered": status["registered_count"],
            "unregistered": status["unregistered_count"],
        },
    )

    return status
