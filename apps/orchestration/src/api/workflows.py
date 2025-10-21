"""Workflow API endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from db.repositories.workflow import WorkflowRepository
from models.workflow import WorkflowRunRequest, WorkflowRunResponse, WorkflowStatusUpdate
from services.workflow_service import WorkflowService
from utils.errors import ApplicationError, RecordNotFoundError


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/workflows", tags=["workflows"])


def get_workflow_service() -> WorkflowService:
    """Dependency injection for workflow service.

    Returns:
        WorkflowService instance
    """
    # In production, this would use the real Supabase client
    from db.client import get_supabase_client

    client = get_supabase_client()
    repo = WorkflowRepository(client)
    return WorkflowService(repo)


@router.post(
    "",
    response_model=WorkflowRunResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new workflow",
    description="Create and start a new workflow run for processing a program",
)
async def start_workflow(
    request: WorkflowRunRequest,
    workflow_service: WorkflowService = Depends(get_workflow_service),  # noqa: B008
) -> WorkflowRunResponse:
    """Start a new workflow run.

    Args:
        request: WorkflowRunRequest with program_id, source, initial_stage
        workflow_service: WorkflowService instance (injected)

    Returns:
        WorkflowRunResponse with workflow details

    Raises:
        HTTPException: If workflow creation fails
    """
    try:
        logger.info(
            "API: Starting workflow",
            extra={"program_id": request.program_id, "source": request.source},
        )

        workflow = await workflow_service.start_workflow(request)

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
            status_code=e.status_code,
            detail=e.message,
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
async def get_workflow_status(
    workflow_id: str,
    workflow_service: WorkflowService = Depends(get_workflow_service),  # noqa: B008
) -> WorkflowRunResponse:
    """Get the current status of a workflow.

    Args:
        workflow_id: ID of the workflow
        workflow_service: WorkflowService instance (injected)

    Returns:
        WorkflowRunResponse with current workflow state

    Raises:
        HTTPException: If workflow not found or retrieval fails
    """
    try:
        logger.debug("API: Getting workflow status", extra={"workflow_id": workflow_id})

        workflow = await workflow_service.get_workflow_status(workflow_id)

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
            detail=f"Workflow {workflow_id} not found",
        ) from e
    except ApplicationError as e:
        logger.error(
            "API: Application error getting workflow status",
            extra={"error": str(e), "workflow_id": workflow_id},
        )
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message,
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
async def update_workflow_status(
    workflow_id: str,
    update: WorkflowStatusUpdate,
    workflow_service: WorkflowService = Depends(get_workflow_service),  # noqa: B008
) -> WorkflowRunResponse:
    """Update the status of a workflow.

    Args:
        workflow_id: ID of the workflow
        update: WorkflowStatusUpdate with new status and optional stage
        workflow_service: WorkflowService instance (injected)

    Returns:
        WorkflowRunResponse with updated workflow state

    Raises:
        HTTPException: If workflow not found or update fails
    """
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
            workflow = await workflow_service.mark_workflow_completed(workflow_id)
        elif update.status.value == "failed":
            workflow = await workflow_service.mark_workflow_failed(
                workflow_id, update.error_message or "Unknown error"
            )
        else:
            # For running status, update the stage if provided
            workflow = await workflow_service.update_workflow_stage(
                workflow_id, update.current_stage or "ingestion"
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
            detail=f"Workflow {workflow_id} not found",
        ) from e
    except ApplicationError as e:
        logger.error(
            "API: Application error updating workflow status",
            extra={"error": str(e), "workflow_id": workflow_id},
        )
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message,
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


@router.get(
    "",
    response_model=list[WorkflowRunResponse],
    summary="List workflows",
    description="List workflows with optional filtering",
)
async def list_workflows(
    program_id: str | None = None,
    status: str | None = None,
    limit: int = 100,
    workflow_service: WorkflowService = Depends(get_workflow_service),  # noqa: B008
) -> list[WorkflowRunResponse]:
    """List workflows with optional filtering.

    Args:
        program_id: Optional program ID to filter by
        status: Optional status to filter by
        limit: Maximum number of workflows to return (default: 100)
        workflow_service: WorkflowService instance (injected)

    Returns:
        List of WorkflowRunResponse objects

    Raises:
        HTTPException: If listing fails
    """
    try:
        logger.debug(
            "API: Listing workflows",
            extra={"program_id": program_id, "status": status, "limit": limit},
        )

        workflows = await workflow_service.list_workflows(
            program_id=program_id, status=status, limit=limit
        )

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
            status_code=e.status_code,
            detail=e.message,
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
