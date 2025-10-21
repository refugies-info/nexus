"""Workflow API endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from db.repositories.workflow import WorkflowRepository, get_workflow_repository
from models.workflow import WorkflowRunRequest, WorkflowRunResponse, WorkflowStatusUpdate
from services.workflow_functions import (
    get_workflow_status,
    list_workflows,
    mark_workflow_completed,
    mark_workflow_failed,
    start_workflow,
    update_workflow_stage,
)
from utils.errors import ApplicationError, RecordNotFoundError


logger = logging.getLogger(__name__)

# Module-level dependency
workflow_repo_dependency = Depends(get_workflow_repository)

router = APIRouter(prefix="/api/v1/workflows", tags=["workflows"])


@router.post(
    "",
    response_model=WorkflowRunResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new workflow",
    description="Create and start a new workflow run for processing a program",
)
async def create_workflow(
    request: WorkflowRunRequest,
    repo: WorkflowRepository = workflow_repo_dependency,
) -> WorkflowRunResponse:
    """Create a new workflow."""
    try:
        logger.info(
            "API: Starting workflow",
            extra={"program_id": request.program_id, "source": request.source},
        )

        workflow = await start_workflow(repo, request)

        logger.info(
            "API: Workflow started successfully",
            extra={"workflow_id": workflow.id, "program_id": request.program_id},
        )

        return workflow
    except ApplicationError as e:
        logger.error(
            "API: Application error starting workflow",
            extra={"error": str(e), "program_id": request.program_id},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(
            "API: Unexpected error starting workflow",
            extra={"error": str(e), "program_id": request.program_id},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start workflow",
        ) from e


@router.get(
    "/{workflow_id}",
    response_model=WorkflowRunResponse,
    summary="Get workflow status",
    description="Retrieve the current status of a workflow run",
)
async def read_workflow(
    workflow_id: str,
    repo: WorkflowRepository = workflow_repo_dependency,
) -> WorkflowRunResponse:
    """Get workflow by ID."""
    try:
        logger.debug("API: Getting workflow status", extra={"workflow_id": workflow_id})

        workflow = await get_workflow_status(repo, workflow_id)

        logger.debug(
            "API: Workflow status retrieved",
            extra={"workflow_id": workflow_id, "status": workflow.status},
        )

        return workflow
    except RecordNotFoundError as e:
        logger.warning(
            "API: Workflow not found",
            extra={"workflow_id": workflow_id},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except ApplicationError as e:
        logger.error(
            "API: Application error getting workflow status",
            extra={"error": str(e), "workflow_id": workflow_id},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(
            "API: Unexpected error getting workflow status",
            extra={"error": str(e), "workflow_id": workflow_id},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get workflow status",
        ) from e


@router.post(
    "/{workflow_id}/status",
    response_model=WorkflowRunResponse,
    summary="Update workflow status",
    description="Update the status of a workflow run",
)
async def update_status(
    workflow_id: str,
    update: WorkflowStatusUpdate,
    repo: WorkflowRepository = workflow_repo_dependency,
) -> WorkflowRunResponse:
    """Update workflow status."""
    try:
        logger.info(
            "API: Updating workflow status",
            extra={
                "workflow_id": workflow_id,
                "status": update.status,
                "stage": update.current_stage,
            },
        )

        # Determine which method to call based on status
        if update.status.value == "completed":
            workflow = await mark_workflow_completed(repo, workflow_id)
        elif update.status.value == "failed":
            workflow = await mark_workflow_failed(
                repo, workflow_id, update.error_message or "Unknown error"
            )
        else:
            # For running status, update the stage if provided
            workflow = await update_workflow_stage(
                repo, workflow_id, update.current_stage or "ingestion"
            )

        logger.info(
            "API: Workflow status updated",
            extra={"workflow_id": workflow_id, "status": workflow.status},
        )

        return workflow
    except RecordNotFoundError as e:
        logger.warning(
            "API: Workflow not found",
            extra={"workflow_id": workflow_id},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except ApplicationError as e:
        logger.error(
            "API: Application error updating workflow status",
            extra={"error": str(e), "workflow_id": workflow_id},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(
            "API: Unexpected error updating workflow status",
            extra={"error": str(e), "workflow_id": workflow_id},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update workflow status",
        ) from e


@router.post(
    "/{workflow_id}/stages/{stage}",
    response_model=WorkflowRunResponse,
    summary="Update workflow stage",
    description="Update the stage of a workflow run",
)
async def update_stage(
    workflow_id: str,
    stage: str,
    repo: WorkflowRepository = workflow_repo_dependency,
) -> WorkflowRunResponse:
    """Update workflow stage."""
    try:
        logger.info(
            "API: Updating workflow stage",
            extra={"workflow_id": workflow_id, "stage": stage},
        )

        workflow = await update_workflow_stage(repo, workflow_id, stage)

        logger.info(
            "API: Workflow stage updated",
            extra={"workflow_id": workflow_id, "stage": workflow.current_stage},
        )

        return workflow
    except RecordNotFoundError as e:
        logger.warning(
            "API: Workflow not found",
            extra={"workflow_id": workflow_id},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except ApplicationError as e:
        logger.error(
            "API: Application error updating workflow stage",
            extra={"error": str(e), "workflow_id": workflow_id},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(
            "API: Unexpected error updating workflow stage",
            extra={"error": str(e), "workflow_id": workflow_id},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update workflow stage",
        ) from e


@router.get(
    "",
    response_model=list[WorkflowRunResponse],
    summary="List workflows",
    description="List workflows with optional filtering",
)
async def list_all_workflows(
    program_id: str | None = None,
    status: str | None = None,
    limit: int = 100,
    repo: WorkflowRepository = workflow_repo_dependency,
) -> list[WorkflowRunResponse]:
    """List workflows with optional filtering."""
    try:
        logger.debug(
            "API: Listing workflows",
            extra={"program_id": program_id, "status": status, "limit": limit},
        )

        workflows = await list_workflows(repo, program_id, status, limit)

        logger.debug(
            "API: Workflows listed",
            extra={"count": len(workflows)},
        )

        return workflows
    except ApplicationError as e:
        logger.error(
            "API: Application error listing workflows",
            extra={"error": str(e)},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(
            "API: Unexpected error listing workflows",
            extra={"error": str(e)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list workflows",
        ) from e
