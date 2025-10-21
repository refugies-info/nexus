import logging
from datetime import datetime
from typing import Any

from supabase import Client

from .base_repository import BaseRepository

logger = logging.getLogger(__name__)


class WorkflowRepository(BaseRepository):
    """Repository for workflow_runs table operations."""

    def __init__(self, client: Client):
        """Initialize workflow repository.

        Args:
            client: Supabase client instance
        """
        super().__init__(client, "workflow_runs")

    async def create_workflow_run(
        self,
        program_id: str,
        source: str,
        initial_stage: str = "ingestion",
        metadata: dict[str, Any] = None,
    ) -> dict[str, Any]:
        """Create a new workflow run.

        Args:
            program_id: ID of the program being processed
            source: Source of the program (e.g., 'data_inclusion')
            initial_stage: Starting stage of the workflow
            metadata: Optional metadata about the workflow

        Returns:
            Created workflow run record
        """
        data = {
            "program_id": program_id,
            "source": source,
            "current_stage": initial_stage,
            "status": "running",
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        return await self.create(data)

    async def get_workflow_run(self, workflow_id: str) -> dict[str, Any]:
        """Get a workflow run by ID.

        Args:
            workflow_id: ID of the workflow run

        Returns:
            Workflow run record if found, None otherwise
        """
        return await self.get_by_id(workflow_id)

    async def update_workflow_status(
        self, workflow_id: str, status: str, current_stage: str = None
    ) -> dict[str, Any]:
        """Update workflow status and optionally current stage.

        Args:
            workflow_id: ID of the workflow run
            status: New status (running, completed, failed, paused)
            current_stage: Optional new current stage

        Returns:
            Updated workflow run record
        """
        data = {
            "status": status,
            "updated_at": datetime.utcnow().isoformat(),
        }
        if current_stage:
            data["current_stage"] = current_stage

        return await self.update(workflow_id, data)

    async def list_workflow_runs(
        self,
        program_id: str = None,
        status: str = None,
        source: str = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """List workflow runs with optional filtering.

        Args:
            program_id: Optional program ID to filter by
            status: Optional status to filter by
            source: Optional source to filter by
            limit: Maximum number of records to return
            offset: Number of records to skip

        Returns:
            List of workflow run records
        """
        filters = {}
        if program_id:
            filters["program_id"] = program_id
        if status:
            filters["status"] = status
        if source:
            filters["source"] = source

        if filters:
            return await self.filter(filters, limit)
        else:
            return await self.list_all(limit, offset)

    async def get_active_workflow_for_program(self, program_id: str) -> dict[str, Any]:
        """Get the active (running) workflow for a program.

        Args:
            program_id: ID of the program

        Returns:
            Active workflow run if found, None otherwise
        """
        workflows = await self.filter({"program_id": program_id, "status": "running"}, limit=1)
        return workflows[0] if workflows else None

    async def mark_workflow_completed(self, workflow_id: str) -> dict[str, Any]:
        """Mark a workflow as completed.

        Args:
            workflow_id: ID of the workflow run

        Returns:
            Updated workflow run record
        """
        return await self.update_workflow_status(workflow_id, "completed")

    async def mark_workflow_failed(
        self, workflow_id: str, error_message: str = None
    ) -> dict[str, Any]:
        """Mark a workflow as failed.

        Args:
            workflow_id: ID of the workflow run
            error_message: Optional error message

        Returns:
            Updated workflow run record
        """
        data = {
            "status": "failed",
            "updated_at": datetime.utcnow().isoformat(),
        }
        if error_message:
            data["error_message"] = error_message

        return await self.update(workflow_id, data)

    async def count_workflows_by_status(self, status: str) -> int:
        """Count workflows with a specific status.

        Args:
            status: Status to count

        Returns:
            Number of workflows with the status
        """
        return await self.count({"status": status})
