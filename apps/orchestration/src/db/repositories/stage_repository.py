import logging
from datetime import datetime
from typing import Any

from supabase import Client

from .base_repository import BaseRepository

logger = logging.getLogger(__name__)


class StageRepository(BaseRepository):
    """Repository for stage_executions table operations."""

    def __init__(self, client: Client):
        """Initialize stage repository.

        Args:
            client: Supabase client instance
        """
        super().__init__(client, "stage_executions")

    async def create_stage_execution(
        self,
        workflow_id: str,
        stage_name: str,
        program_id: str,
        metadata: dict[str, Any] = None,
    ) -> dict[str, Any]:
        """Create a new stage execution.

        Args:
            workflow_id: ID of the parent workflow
            stage_name: Name of the stage
            program_id: ID of the program being processed
            metadata: Optional metadata about the stage execution

        Returns:
            Created stage execution record
        """
        data = {
            "workflow_id": workflow_id,
            "stage_name": stage_name,
            "program_id": program_id,
            "status": "pending",
            "attempt": 1,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        return await self.create(data)

    async def get_stage_execution(self, stage_id: str) -> dict[str, Any]:
        """Get a stage execution by ID.

        Args:
            stage_id: ID of the stage execution

        Returns:
            Stage execution record if found, None otherwise
        """
        return await self.get_by_id(stage_id)

    async def update_stage_status(
        self,
        stage_id: str,
        status: str,
        result: dict[str, Any] = None,
        error_message: str = None,
    ) -> dict[str, Any]:
        """Update stage execution status.

        Args:
            stage_id: ID of the stage execution
            status: New status (pending, running, completed, failed, skipped)
            result: Optional result data from stage execution
            error_message: Optional error message if failed

        Returns:
            Updated stage execution record
        """
        data = {
            "status": status,
            "updated_at": datetime.utcnow().isoformat(),
        }
        if result:
            data["result"] = result
        if error_message:
            data["error_message"] = error_message

        return await self.update(stage_id, data)

    async def list_stage_executions(
        self,
        workflow_id: str = None,
        stage_name: str = None,
        status: str = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """List stage executions with optional filtering.

        Args:
            workflow_id: Optional workflow ID to filter by
            stage_name: Optional stage name to filter by
            status: Optional status to filter by
            limit: Maximum number of records to return
            offset: Number of records to skip

        Returns:
            List of stage execution records
        """
        filters = {}
        if workflow_id:
            filters["workflow_id"] = workflow_id
        if stage_name:
            filters["stage_name"] = stage_name
        if status:
            filters["status"] = status

        if filters:
            return await self.filter(filters, limit)
        else:
            return await self.list_all(limit, offset)

    async def get_stages_for_workflow(self, workflow_id: str) -> list[dict[str, Any]]:
        """Get all stages for a workflow, ordered by creation time.

        Args:
            workflow_id: ID of the workflow

        Returns:
            List of stage execution records ordered by creation time
        """
        stages = await self.filter({"workflow_id": workflow_id}, limit=1000)
        return sorted(stages, key=lambda x: x.get("created_at", ""))

    async def mark_stage_completed(
        self, stage_id: str, result: dict[str, Any] = None
    ) -> dict[str, Any]:
        """Mark a stage as completed.

        Args:
            stage_id: ID of the stage execution
            result: Optional result data from stage

        Returns:
            Updated stage execution record
        """
        return await self.update_stage_status(stage_id, "completed", result=result)

    async def mark_stage_failed(self, stage_id: str, error_message: str) -> dict[str, Any]:
        """Mark a stage as failed.

        Args:
            stage_id: ID of the stage execution
            error_message: Error message describing the failure

        Returns:
            Updated stage execution record
        """
        return await self.update_stage_status(stage_id, "failed", error_message=error_message)

    async def increment_attempt(self, stage_id: str) -> dict[str, Any]:
        """Increment the attempt counter for a stage.

        Args:
            stage_id: ID of the stage execution

        Returns:
            Updated stage execution record
        """
        stage = await self.get_by_id(stage_id)
        if not stage:
            raise ValueError(f"Stage {stage_id} not found")

        current_attempt = stage.get("attempt", 1)
        return await self.update(stage_id, {"attempt": current_attempt + 1})

    async def count_stages_by_status(self, workflow_id: str, status: str) -> int:
        """Count stages in a workflow with a specific status.

        Args:
            workflow_id: ID of the workflow
            status: Status to count

        Returns:
            Number of stages with the status
        """
        return await self.count({"workflow_id": workflow_id, "status": status})

    async def get_failed_stages(self, workflow_id: str) -> list[dict[str, Any]]:
        """Get all failed stages for a workflow.

        Args:
            workflow_id: ID of the workflow

        Returns:
            List of failed stage execution records
        """
        return await self.filter({"workflow_id": workflow_id, "status": "failed"}, limit=1000)
