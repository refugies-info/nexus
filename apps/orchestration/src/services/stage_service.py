"""Stage execution service for pipeline stage management."""

import logging
from typing import Any

from db.repositories.stage import StageRepository
from models.stage import StageExecutionRequest, StageExecutionResponse, StageStatus
from utils.errors import PipelineError, RecordNotFoundError


logger = logging.getLogger(__name__)


class StageService:
    """Service for managing stage execution."""

    def __init__(self, stage_repo: StageRepository):
        """Initialize stage service.

        Args:
            stage_repo: StageRepository instance
        """
        self.stage_repo = stage_repo

    async def execute_stage(self, request: StageExecutionRequest) -> StageExecutionResponse:
        """Execute a pipeline stage.

        Args:
            request: StageExecutionRequest with workflow_id, stage_name, program_id

        Returns:
            StageExecutionResponse with stage details

        Raises:
            PipelineError: If stage execution fails
        """
        try:
            logger.info(
                "Executing stage",
                extra={
                    "workflow_id": request.workflow_id,
                    "stage_name": request.stage_name,
                    "program_id": request.program_id,
                },
            )

            stage = await self.stage_repo.create_stage_execution(
                workflow_id=request.workflow_id,
                stage_name=request.stage_name,
                program_id=request.program_id,
                metadata=request.metadata,
            )

            logger.info(
                "Stage execution created",
                extra={
                    "stage_id": stage["id"],
                    "stage_name": request.stage_name,
                    "workflow_id": request.workflow_id,
                },
            )

            return self._to_response(stage)
        except Exception as e:
            logger.error(
                "Failed to execute stage",
                extra={
                    "error": str(e),
                    "stage_name": request.stage_name,
                    "workflow_id": request.workflow_id,
                },
            )
            raise PipelineError(f"Failed to execute stage: {str(e)}") from e

    async def get_stage_execution(self, stage_id: str) -> StageExecutionResponse:
        """Get the current status of a stage execution.

        Args:
            stage_id: ID of the stage execution

        Returns:
            StageExecutionResponse with current stage state

        Raises:
            RecordNotFoundError: If stage not found
            PipelineError: If retrieval fails
        """
        try:
            logger.debug("Getting stage execution", extra={"stage_id": stage_id})

            stage = await self.stage_repo.get_stage_execution(stage_id)

            if not stage:
                logger.warning("Stage not found", extra={"stage_id": stage_id})
                raise RecordNotFoundError("Stage", stage_id)

            return self._to_response(stage)
        except RecordNotFoundError:
            raise
        except Exception as e:
            logger.error(
                "Failed to get stage execution",
                extra={"error": str(e), "stage_id": stage_id},
            )
            raise PipelineError(f"Failed to get stage execution: {str(e)}") from e

    async def mark_stage_complete(
        self, stage_id: str, result: dict[str, Any] | None = None
    ) -> StageExecutionResponse:
        """Mark a stage as completed.

        Args:
            stage_id: ID of the stage execution
            result: Optional result data from stage execution

        Returns:
            StageExecutionResponse with completed stage state

        Raises:
            RecordNotFoundError: If stage not found
            PipelineError: If update fails
        """
        try:
            logger.info(
                "Marking stage as completed",
                extra={"stage_id": stage_id},
            )

            stage = await self.stage_repo.mark_stage_completed(stage_id, result=result)

            if not stage:
                logger.warning("Stage not found", extra={"stage_id": stage_id})
                raise RecordNotFoundError("Stage", stage_id)

            logger.info(
                "Stage marked as completed",
                extra={"stage_id": stage_id},
            )

            return self._to_response(stage)
        except RecordNotFoundError:
            raise
        except Exception as e:
            logger.error(
                "Failed to mark stage as completed",
                extra={"error": str(e), "stage_id": stage_id},
            )
            raise PipelineError(f"Failed to mark stage as completed: {str(e)}") from e

    async def handle_stage_failure(
        self, stage_id: str, error_message: str
    ) -> StageExecutionResponse:
        """Handle stage execution failure.

        Args:
            stage_id: ID of the stage execution
            error_message: Error message describing the failure

        Returns:
            StageExecutionResponse with failed stage state

        Raises:
            RecordNotFoundError: If stage not found
            PipelineError: If update fails
        """
        try:
            logger.error(
                "Handling stage failure",
                extra={"stage_id": stage_id, "error": error_message},
            )

            stage = await self.stage_repo.mark_stage_failed(stage_id, error_message)

            if not stage:
                logger.warning("Stage not found", extra={"stage_id": stage_id})
                raise RecordNotFoundError("Stage", stage_id)

            logger.error(
                "Stage marked as failed",
                extra={"stage_id": stage_id, "error": error_message},
            )

            return self._to_response(stage)
        except RecordNotFoundError:
            raise
        except Exception as e:
            logger.error(
                "Failed to handle stage failure",
                extra={"error": str(e), "stage_id": stage_id},
            )
            raise PipelineError(f"Failed to handle stage failure: {str(e)}") from e

    async def retry_stage(self, stage_id: str) -> StageExecutionResponse:
        """Retry a failed stage execution.

        Args:
            stage_id: ID of the stage execution

        Returns:
            StageExecutionResponse with retry stage state

        Raises:
            RecordNotFoundError: If stage not found
            PipelineError: If retry fails
        """
        try:
            logger.info("Retrying stage", extra={"stage_id": stage_id})

            stage = await self.stage_repo.get_stage_execution(stage_id)

            if not stage:
                logger.warning("Stage not found", extra={"stage_id": stage_id})
                raise RecordNotFoundError("Stage", stage_id)

            # Increment attempt counter
            updated_stage = await self.stage_repo.increment_attempt(stage_id)

            # Reset status to pending for retry
            updated_stage = await self.stage_repo.update_stage_status(
                stage_id, StageStatus.PENDING.value
            )

            logger.info(
                "Stage retry initiated",
                extra={
                    "stage_id": stage_id,
                    "attempt": updated_stage.get("attempt", 1),
                },
            )

            return self._to_response(updated_stage)
        except RecordNotFoundError:
            raise
        except Exception as e:
            logger.error(
                "Failed to retry stage",
                extra={"error": str(e), "stage_id": stage_id},
            )
            raise PipelineError(f"Failed to retry stage: {str(e)}") from e

    async def get_stages_for_workflow(self, workflow_id: str) -> list[StageExecutionResponse]:
        """Get all stages for a workflow.

        Args:
            workflow_id: ID of the workflow

        Returns:
            List of StageExecutionResponse objects

        Raises:
            PipelineError: If retrieval fails
        """
        try:
            logger.debug("Getting stages for workflow", extra={"workflow_id": workflow_id})

            stages = await self.stage_repo.get_stages_for_workflow(workflow_id)

            return [self._to_response(s) for s in stages]
        except Exception as e:
            logger.error(
                "Failed to get stages for workflow",
                extra={"error": str(e), "workflow_id": workflow_id},
            )
            raise PipelineError(f"Failed to get stages for workflow: {str(e)}") from e

    async def get_failed_stages(self, workflow_id: str) -> list[StageExecutionResponse]:
        """Get all failed stages for a workflow.

        Args:
            workflow_id: ID of the workflow

        Returns:
            List of failed StageExecutionResponse objects

        Raises:
            PipelineError: If retrieval fails
        """
        try:
            logger.debug(
                "Getting failed stages for workflow",
                extra={"workflow_id": workflow_id},
            )

            stages = await self.stage_repo.get_failed_stages(workflow_id)

            return [self._to_response(s) for s in stages]
        except Exception as e:
            logger.error(
                "Failed to get failed stages",
                extra={"error": str(e), "workflow_id": workflow_id},
            )
            raise PipelineError(f"Failed to get failed stages: {str(e)}") from e

    async def count_stages_by_status(self, workflow_id: str, status: str) -> int:
        """Count stages in a workflow with a specific status.

        Args:
            workflow_id: ID of the workflow
            status: Status to count

        Returns:
            Number of stages with the status

        Raises:
            PipelineError: If count fails
        """
        try:
            logger.debug(
                "Counting stages by status",
                extra={"workflow_id": workflow_id, "status": status},
            )

            count = await self.stage_repo.count_stages_by_status(workflow_id, status)

            return count
        except Exception as e:
            logger.error(
                "Failed to count stages by status",
                extra={"error": str(e), "workflow_id": workflow_id, "status": status},
            )
            raise PipelineError(f"Failed to count stages by status: {str(e)}") from e

    def _to_response(self, stage: dict[str, Any]) -> StageExecutionResponse:
        """Convert stage dict to response model.

        Args:
            stage: Stage data from repository

        Returns:
            StageExecutionResponse instance
        """
        return StageExecutionResponse(
            id=stage["id"],
            workflow_id=stage["workflow_id"],
            stage_name=stage["stage_name"],
            program_id=stage["program_id"],
            status=StageStatus(stage["status"]),
            attempt=stage.get("attempt", 1),
            result=stage.get("result"),
            error_message=stage.get("error_message"),
            metadata=stage.get("metadata", {}),
            created_at=stage["created_at"],
            updated_at=stage["updated_at"],
        )
