"""Unit tests for workflow functions."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from models.workflow import WorkflowRunRequest, WorkflowStatus
from services.workflow import (
    get_workflow_status,
    handle_stage_completion,
    list_workflows,
    mark_workflow_completed,
    mark_workflow_failed,
    start_workflow,
    update_workflow_stage,
)
from utils.errors import PipelineError, RecordNotFoundError


@pytest.fixture
def mock_workflow_repo():
    """Create a mock workflow repository."""
    return MagicMock()


@pytest.mark.unit
class TestWorkflowFunctionsStartWorkflow:
    """Tests for starting workflows."""

    @pytest.mark.asyncio
    async def test_start_workflow_success(self, mock_workflow_repo):
        """Test successfully starting a workflow."""
        request = WorkflowRunRequest(
            program_id="prog_123",
            source="data_inclusion",
            initial_stage="ingestion",
        )

        mock_workflow_repo.create_workflow_run = AsyncMock(
            return_value={
                "id": "wf_123",
                "program_id": "prog_123",
                "source": "data_inclusion",
                "current_stage": "ingestion",
                "status": "running",
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )

        result = await start_workflow(mock_workflow_repo, request)

        assert result.id == "wf_123"
        assert result.program_id == "prog_123"
        assert result.status == WorkflowStatus.RUNNING
        mock_workflow_repo.create_workflow_run.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_workflow_with_metadata(self, mock_workflow_repo):
        """Test starting workflow with metadata."""
        request = WorkflowRunRequest(
            program_id="prog_123",
            source="data_inclusion",
            metadata={"batch_id": "batch_001"},
        )

        mock_workflow_repo.create_workflow_run = AsyncMock(
            return_value={
                "id": "wf_123",
                "program_id": "prog_123",
                "source": "data_inclusion",
                "current_stage": "ingestion",
                "status": "running",
                "metadata": {"batch_id": "batch_001"},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )

        result = await start_workflow(mock_workflow_repo, request)

        assert result.metadata == {"batch_id": "batch_001"}

    @pytest.mark.asyncio
    async def test_start_workflow_failure(self, mock_workflow_repo):
        """Test workflow start failure."""
        request = WorkflowRunRequest(
            program_id="prog_123",
            source="data_inclusion",
        )

        mock_workflow_repo.create_workflow_run = AsyncMock(side_effect=Exception("Database error"))

        with pytest.raises(PipelineError):
            await start_workflow(mock_workflow_repo, request)


@pytest.mark.unit
class TestWorkflowFunctionsGetStatus:
    """Tests for getting workflow status."""

    @pytest.mark.asyncio
    async def test_get_workflow_status_success(self, mock_workflow_repo):
        """Test successfully retrieving workflow status."""
        mock_workflow_repo.get_workflow_run = AsyncMock(
            return_value={
                "id": "wf_123",
                "program_id": "prog_123",
                "source": "data_inclusion",
                "current_stage": "enrichment",
                "status": "running",
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )

        result = await get_workflow_status(mock_workflow_repo, "wf_123")

        assert result.id == "wf_123"
        assert result.current_stage == "enrichment"
        mock_workflow_repo.get_workflow_run.assert_called_once_with("wf_123")

    @pytest.mark.asyncio
    async def test_get_workflow_status_not_found(self, mock_workflow_repo):
        """Test retrieving non-existent workflow."""
        mock_workflow_repo.get_workflow_run = AsyncMock(return_value=None)

        with pytest.raises(RecordNotFoundError):
            await get_workflow_status(mock_workflow_repo, "wf_nonexistent")

    @pytest.mark.asyncio
    async def test_get_workflow_status_failure(self, mock_workflow_repo):
        """Test workflow status retrieval failure."""
        mock_workflow_repo.get_workflow_run = AsyncMock(side_effect=Exception("Database error"))

        with pytest.raises(PipelineError):
            await get_workflow_status(mock_workflow_repo, "wf_123")


@pytest.mark.unit
class TestWorkflowFunctionsUpdateStage:
    """Tests for updating workflow stage."""

    @pytest.mark.asyncio
    async def test_update_workflow_stage_success(self, mock_workflow_repo):
        """Test successfully updating workflow stage."""
        mock_workflow_repo.update_workflow_status = AsyncMock(
            return_value={
                "id": "wf_123",
                "program_id": "prog_123",
                "source": "data_inclusion",
                "current_stage": "enrichment",
                "status": "running",
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )

        result = await update_workflow_stage(mock_workflow_repo, "wf_123", "enrichment")

        assert result.current_stage == "enrichment"
        mock_workflow_repo.update_workflow_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_workflow_stage_not_found(self, mock_workflow_repo):
        """Test updating non-existent workflow."""
        mock_workflow_repo.update_workflow_status = AsyncMock(return_value=None)

        with pytest.raises(RecordNotFoundError):
            await update_workflow_stage(mock_workflow_repo, "wf_nonexistent", "enrichment")


@pytest.mark.unit
class TestWorkflowFunctionsHandleCompletion:
    """Tests for handling stage completion."""

    @pytest.mark.asyncio
    async def test_handle_stage_completion_success(self, mock_workflow_repo):
        """Test successfully handling stage completion."""
        mock_workflow_repo.get_workflow_run = AsyncMock(
            return_value={
                "id": "wf_123",
                "program_id": "prog_123",
                "source": "data_inclusion",
                "current_stage": "enrichment",
                "status": "running",
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )

        mock_workflow_repo.update = AsyncMock(
            return_value={
                "id": "wf_123",
                "program_id": "prog_123",
                "source": "data_inclusion",
                "current_stage": "enrichment",
                "status": "running",
                "metadata": {"stage_results": {"enrichment": {"status": "success"}}},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )

        result = await handle_stage_completion(
            mock_workflow_repo, "wf_123", "enrichment", {"status": "success"}
        )

        assert result.id == "wf_123"
        mock_workflow_repo.get_workflow_run.assert_called_once()
        mock_workflow_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_stage_completion_not_found(self, mock_workflow_repo):
        """Test handling completion for non-existent workflow."""
        mock_workflow_repo.get_workflow_run = AsyncMock(return_value=None)

        with pytest.raises(RecordNotFoundError):
            await handle_stage_completion(
                mock_workflow_repo, "wf_nonexistent", "enrichment", {"status": "success"}
            )


@pytest.mark.unit
class TestWorkflowFunctionsMarkCompleted:
    """Tests for marking workflows as completed."""

    @pytest.mark.asyncio
    async def test_mark_workflow_completed_success(self, mock_workflow_repo):
        """Test successfully marking workflow as completed."""
        mock_workflow_repo.mark_workflow_completed = AsyncMock(
            return_value={
                "id": "wf_123",
                "program_id": "prog_123",
                "source": "data_inclusion",
                "current_stage": "publication",
                "status": "completed",
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )

        result = await mark_workflow_completed(mock_workflow_repo, "wf_123")

        assert result.status == WorkflowStatus.COMPLETED
        mock_workflow_repo.mark_workflow_completed.assert_called_once_with("wf_123")

    @pytest.mark.asyncio
    async def test_mark_workflow_completed_not_found(self, mock_workflow_repo):
        """Test marking non-existent workflow as completed."""
        mock_workflow_repo.mark_workflow_completed = AsyncMock(return_value=None)

        with pytest.raises(RecordNotFoundError):
            await mark_workflow_completed(mock_workflow_repo, "wf_nonexistent")


@pytest.mark.unit
class TestWorkflowFunctionsMarkFailed:
    """Tests for marking workflows as failed."""

    @pytest.mark.asyncio
    async def test_mark_workflow_failed_success(self, mock_workflow_repo):
        """Test successfully marking workflow as failed."""
        mock_workflow_repo.mark_workflow_failed = AsyncMock(
            return_value={
                "id": "wf_123",
                "program_id": "prog_123",
                "source": "data_inclusion",
                "current_stage": "enrichment",
                "status": "failed",
                "error_message": "Stage timeout",
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )

        result = await mark_workflow_failed(mock_workflow_repo, "wf_123", "Stage timeout")

        assert result.status == WorkflowStatus.FAILED
        assert result.error_message == "Stage timeout"
        mock_workflow_repo.mark_workflow_failed.assert_called_once()

    @pytest.mark.asyncio
    async def test_mark_workflow_failed_not_found(self, mock_workflow_repo):
        """Test marking non-existent workflow as failed."""
        mock_workflow_repo.mark_workflow_failed = AsyncMock(return_value=None)

        with pytest.raises(RecordNotFoundError):
            await mark_workflow_failed(mock_workflow_repo, "wf_nonexistent", "Error")


@pytest.mark.unit
class TestWorkflowFunctionsListWorkflows:
    """Tests for listing workflows."""

    @pytest.mark.asyncio
    async def test_list_workflows_success(self, mock_workflow_repo):
        """Test successfully listing workflows."""
        mock_workflow_repo.list_workflow_runs = AsyncMock(
            return_value=[
                {
                    "id": "wf_123",
                    "program_id": "prog_123",
                    "source": "data_inclusion",
                    "current_stage": "enrichment",
                    "status": "running",
                    "metadata": {},
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                },
                {
                    "id": "wf_124",
                    "program_id": "prog_124",
                    "source": "data_inclusion",
                    "current_stage": "publication",
                    "status": "completed",
                    "metadata": {},
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                },
            ]
        )

        result = await list_workflows(mock_workflow_repo)

        assert len(result) == 2
        assert result[0].id == "wf_123"
        assert result[1].id == "wf_124"

    @pytest.mark.asyncio
    async def test_list_workflows_with_filters(self, mock_workflow_repo):
        """Test listing workflows with filters."""
        mock_workflow_repo.list_workflow_runs = AsyncMock(return_value=[])

        await list_workflows(mock_workflow_repo, program_id="prog_123", status="running", limit=50)

        mock_workflow_repo.list_workflow_runs.assert_called_once_with(
            program_id="prog_123", status="running", limit=50
        )

    @pytest.mark.asyncio
    async def test_list_workflows_empty(self, mock_workflow_repo):
        """Test listing workflows when none exist."""
        mock_workflow_repo.list_workflow_runs = AsyncMock(return_value=[])

        result = await list_workflows(mock_workflow_repo)

        assert result == []
