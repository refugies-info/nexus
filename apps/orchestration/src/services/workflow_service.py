"""DEPRECATED: WorkflowService class - Use workflow_functions.py instead.

This module is kept for backwards compatibility but will be removed in a future version.
All new code should use the functional versions in workflow_functions.py.
"""

import logging
import warnings
from datetime import datetime
from typing import Any

from db.repositories.workflow import WorkflowRepository
from models.workflow import WorkflowRunRequest, WorkflowRunResponse, WorkflowStatus
from utils.errors import PipelineError, RecordNotFoundError


warnings.warn(
    "WorkflowService is deprecated. Use workflow_functions.py instead",
    DeprecationWarning,
    stacklevel=2,
)

logger = logging.getLogger(__name__)


class WorkflowService:
    """Service for managing workflow execution."""

    def __init__(self, workflow_repo: WorkflowRepository):
        """Initialize workflow service.

        Args:
            workflow_repo: WorkflowRepository instance
        """
        self.workflow_repo = workflow_repo

    async def start_workflow(self, request: WorkflowRunRequest) -> WorkflowRunResponse:
        """Start a new workflow run.

        Args:
            request: WorkflowRunRequest with program_id, source, initial_stage

        Returns:
            WorkflowRunResponse with workflow details

        Raises:
            PipelineError: If workflow creation fails
        """
        try:
            logger.info(
                "Starting workflow",
                extra={
                    "program_id": request.program_id,
                    "source": request.source,
                    "initial_stage": request.initial_stage,
                },
            )

            workflow = await self.workflow_repo.create_workflow_run(
                program_id=request.program_id,
                source=request.source,
                initial_stage=request.initial_stage,
                metadata=request.metadata,
            )

            logger.info(
                "Workflow started successfully",
                extra={"workflow_id": workflow["id"], "program_id": request.program_id},
            )

            return self._to_response(workflow)
        except Exception as e:
            logger.error(
                "Failed to start workflow",
                extra={"error": str(e), "program_id": request.program_id},
            )
            raise PipelineError(f"Failed to start workflow: {str(e)}") from e

    async def get_workflow_status(self, workflow_id: str) -> WorkflowRunResponse:
        """Get the current status of a workflow.

        Args:
            workflow_id: ID of the workflow

        Returns:
            WorkflowRunResponse with current workflow state

        Raises:
            RecordNotFoundError: If workflow not found
            PipelineError: If retrieval fails
        """
        try:
            logger.debug("Getting workflow status", extra={"workflow_id": workflow_id})

            workflow = await self.workflow_repo.get_workflow_run(workflow_id)

            if not workflow:
                logger.warning("Workflow not found", extra={"workflow_id": workflow_id})
                raise RecordNotFoundError("Workflow", workflow_id)

            return self._to_response(workflow)
        except RecordNotFoundError:
            raise
        except Exception as e:
            logger.error(
                "Failed to get workflow status",
                extra={"error": str(e), "workflow_id": workflow_id},
            )
            raise PipelineError(f"Failed to get workflow status: {str(e)}") from e

    async def update_workflow_stage(self, workflow_id: str, stage: str) -> WorkflowRunResponse:
        """Update the current stage of a workflow.

        Args:
            workflow_id: ID of the workflow
            stage: New stage name

        Returns:
            WorkflowRunResponse with updated workflow state

        Raises:
            RecordNotFoundError: If workflow not found
            PipelineError: If update fails
        """
        try:
            logger.info(
                "Updating workflow stage",
                extra={"workflow_id": workflow_id, "stage": stage},
            )

            workflow = await self.workflow_repo.update_workflow_status(
                workflow_id, "running", current_stage=stage
            )

            if not workflow:
                logger.warning("Workflow not found", extra={"workflow_id": workflow_id})
                raise RecordNotFoundError("Workflow", workflow_id)

            logger.info(
                "Workflow stage updated",
                extra={"workflow_id": workflow_id, "stage": stage},
            )

            return self._to_response(workflow)
        except RecordNotFoundError:
            raise
        except Exception as e:
            logger.error(
                "Failed to update workflow stage",
                extra={"error": str(e), "workflow_id": workflow_id, "stage": stage},
            )
            raise PipelineError(f"Failed to update workflow stage: {str(e)}") from e

    async def handle_stage_completion(
        self, workflow_id: str, stage: str, result: dict[str, Any] | None = None
    ) -> WorkflowRunResponse:
        """Handle completion of a pipeline stage.

        Args:
            workflow_id: ID of the workflow
            stage: Name of the completed stage
            result: Optional result data from the stage

        Returns:
            WorkflowRunResponse with updated workflow state

        Raises:
            RecordNotFoundError: If workflow not found
            PipelineError: If update fails
        """
        try:
            logger.info(
                "Handling stage completion",
                extra={"workflow_id": workflow_id, "stage": stage},
            )

            workflow = await self.workflow_repo.get_workflow_run(workflow_id)

            if not workflow:
                logger.warning("Workflow not found", extra={"workflow_id": workflow_id})
                raise RecordNotFoundError("Workflow", workflow_id)

            # Update metadata with stage result if provided
            metadata = workflow.get("metadata", {})
            if result:
                if "stage_results" not in metadata:
                    metadata["stage_results"] = {}
                metadata["stage_results"][stage] = result

            updated_workflow = await self.workflow_repo.update(
                workflow_id,
                {
                    "metadata": metadata,
                    "updated_at": datetime.utcnow().isoformat(),
                },
            )

            logger.info(
                "Stage completion handled",
                extra={"workflow_id": workflow_id, "stage": stage},
            )

            return self._to_response(updated_workflow)
        except RecordNotFoundError:
            raise
        except Exception as e:
            logger.error(
                "Failed to handle stage completion",
                extra={"error": str(e), "workflow_id": workflow_id, "stage": stage},
            )
            raise PipelineError(f"Failed to handle stage completion: {str(e)}") from e

    async def mark_workflow_completed(self, workflow_id: str) -> WorkflowRunResponse:
        """Mark a workflow as completed.

        Args:
            workflow_id: ID of the workflow

        Returns:
            WorkflowRunResponse with completed workflow state

        Raises:
            RecordNotFoundError: If workflow not found
            PipelineError: If update fails
        """
        try:
            logger.info("Marking workflow as completed", extra={"workflow_id": workflow_id})

            workflow = await self.workflow_repo.mark_workflow_completed(workflow_id)

            if not workflow:
                logger.warning("Workflow not found", extra={"workflow_id": workflow_id})
                raise RecordNotFoundError("Workflow", workflow_id)

            logger.info("Workflow marked as completed", extra={"workflow_id": workflow_id})

            return self._to_response(workflow)
        except RecordNotFoundError:
            raise
        except Exception as e:
            logger.error(
                "Failed to mark workflow as completed",
                extra={"error": str(e), "workflow_id": workflow_id},
            )
            raise PipelineError(f"Failed to mark workflow as completed: {str(e)}") from e

    async def mark_workflow_failed(
        self, workflow_id: str, error_message: str
    ) -> WorkflowRunResponse:
        """Mark a workflow as failed.

        Args:
            workflow_id: ID of the workflow
            error_message: Error message describing the failure

        Returns:
            WorkflowRunResponse with failed workflow state

        Raises:
            RecordNotFoundError: If workflow not found
            PipelineError: If update fails
        """
        try:
            logger.error(
                "Marking workflow as failed",
                extra={"workflow_id": workflow_id, "error": error_message},
            )

            workflow = await self.workflow_repo.mark_workflow_failed(workflow_id, error_message)

            if not workflow:
                logger.warning("Workflow not found", extra={"workflow_id": workflow_id})
                raise RecordNotFoundError("Workflow", workflow_id)

            logger.error(
                "Workflow marked as failed",
                extra={"workflow_id": workflow_id, "error": error_message},
            )

            return self._to_response(workflow)
        except RecordNotFoundError:
            raise
        except Exception as e:
            logger.error(
                "Failed to mark workflow as failed",
                extra={"error": str(e), "workflow_id": workflow_id},
            )
            raise PipelineError(f"Failed to mark workflow as failed: {str(e)}") from e

    async def list_workflows(
        self,
        program_id: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[WorkflowRunResponse]:
        """List workflows with optional filtering.

        Args:
            program_id: Optional program ID to filter by
            status: Optional status to filter by
            limit: Maximum number of workflows to return

        Returns:
            List of WorkflowRunResponse objects

        Raises:
            PipelineError: If listing fails
        """
        try:
            logger.debug(
                "Listing workflows",
                extra={"program_id": program_id, "status": status, "limit": limit},
            )

            workflows = await self.workflow_repo.list_workflow_runs(
                program_id=program_id, status=status, limit=limit
            )

            return [self._to_response(w) for w in workflows]
        except Exception as e:
            logger.error(
                "Failed to list workflows",
                extra={"error": str(e)},
            )
            raise PipelineError(f"Failed to list workflows: {str(e)}") from e

    def _to_response(self, workflow: dict[str, Any]) -> WorkflowRunResponse:
        """Convert workflow dict to response model.

        Args:
            workflow: Workflow data from repository

        Returns:
            WorkflowRunResponse instance
        """
        return WorkflowRunResponse(
            id=workflow["id"],
            program_id=workflow["program_id"],
            source=workflow["source"],
            current_stage=workflow["current_stage"],
            status=WorkflowStatus(workflow["status"]),
            metadata=workflow.get("metadata", {}),
            created_at=workflow["created_at"],
            updated_at=workflow["updated_at"],
            error_message=workflow.get("error_message"),
        )
