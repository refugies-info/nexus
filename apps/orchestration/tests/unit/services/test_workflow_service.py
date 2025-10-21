"""Unit tests for workflow service."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from models.workflow import WorkflowRunRequest, WorkflowStatus
from services.workflow_service import WorkflowService
from utils.errors import PipelineError, RecordNotFoundError


@pytest.fixture
def mock_workflow_repo():
    """Create a mock workflow repository."""
    return MagicMock()


@pytest.fixture
def workflow_service(mock_workflow_repo):
    """Create a workflow service with mocked repository."""
    return WorkflowService(mock_workflow_repo)


@pytest.mark.unit
class TestWorkflowServiceStartWorkflow:
    """Tests for starting workflows."""

    @pytest.mark.asyncio
    async def test_start_workflow_success(self, workflow_service, mock_workflow_repo):
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

        result = await workflow_service.start_workflow(request)

        assert result.id == "wf_123"
        assert result.program_id == "prog_123"
        assert result.status == WorkflowStatus.RUNNING
        mock_workflow_repo.create_workflow_run.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_workflow_with_metadata(self, workflow_service, mock_workflow_repo):
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

        result = await workflow_service.start_workflow(request)

        assert result.metadata == {"batch_id": "batch_001"}

    @pytest.mark.asyncio
    async def test_start_workflow_failure(self, workflow_service, mock_workflow_repo):
        """Test workflow start failure."""
        request = WorkflowRunRequest(
            program_id="prog_123",
            source="data_inclusion",
        )

        mock_workflow_repo.create_workflow_run = AsyncMock(side_effect=Exception("Database error"))

        with pytest.raises(PipelineError):
            await workflow_service.start_workflow(request)


@pytest.mark.unit
class TestWorkflowServiceGetStatus:
    """Tests for getting workflow status."""

    @pytest.mark.asyncio
    async def test_get_workflow_status_success(self, workflow_service, mock_workflow_repo):
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

        result = await workflow_service.get_workflow_status("wf_123")

        assert result.id == "wf_123"
        assert result.current_stage == "enrichment"
        mock_workflow_repo.get_workflow_run.assert_called_once_with("wf_123")

    @pytest.mark.asyncio
    async def test_get_workflow_status_not_found(self, workflow_service, mock_workflow_repo):
        """Test retrieving non-existent workflow."""
        mock_workflow_repo.get_workflow_run = AsyncMock(return_value=None)

        with pytest.raises(RecordNotFoundError):
            await workflow_service.get_workflow_status("wf_nonexistent")

    @pytest.mark.asyncio
    async def test_get_workflow_status_failure(self, workflow_service, mock_workflow_repo):
        """Test workflow status retrieval failure."""
        mock_workflow_repo.get_workflow_run = AsyncMock(side_effect=Exception("Database error"))

        with pytest.raises(PipelineError):
            await workflow_service.get_workflow_status("wf_123")


@pytest.mark.unit
class TestWorkflowServiceUpdateStage:
    """Tests for updating workflow stage."""

    @pytest.mark.asyncio
    async def test_update_workflow_stage_success(self, workflow_service, mock_workflow_repo):
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

        result = await workflow_service.update_workflow_stage("wf_123", "enrichment")

        assert result.current_stage == "enrichment"
        mock_workflow_repo.update_workflow_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_workflow_stage_not_found(self, workflow_service, mock_workflow_repo):
        """Test updating non-existent workflow."""
        mock_workflow_repo.update_workflow_status = AsyncMock(return_value=None)

        with pytest.raises(RecordNotFoundError):
            await workflow_service.update_workflow_stage("wf_nonexistent", "enrichment")


@pytest.mark.unit
class TestWorkflowServiceHandleCompletion:
    """Tests for handling stage completion."""

    @pytest.mark.asyncio
    async def test_handle_stage_completion_success(self, workflow_service, mock_workflow_repo):
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

        result = await workflow_service.handle_stage_completion(
            "wf_123", "enrichment", {"status": "success"}
        )

        assert result.id == "wf_123"
        mock_workflow_repo.get_workflow_run.assert_called_once()
        mock_workflow_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_stage_completion_not_found(self, workflow_service, mock_workflow_repo):
        """Test handling completion for non-existent workflow."""
        mock_workflow_repo.get_workflow_run = AsyncMock(return_value=None)

        with pytest.raises(RecordNotFoundError):
            await workflow_service.handle_stage_completion("wf_nonexistent", "enrichment")


@pytest.mark.unit
class TestWorkflowServiceMarkCompleted:
    """Tests for marking workflows as completed."""

    @pytest.mark.asyncio
    async def test_mark_workflow_completed_success(self, workflow_service, mock_workflow_repo):
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

        result = await workflow_service.mark_workflow_completed("wf_123")

        assert result.status == WorkflowStatus.COMPLETED
        mock_workflow_repo.mark_workflow_completed.assert_called_once_with("wf_123")

    @pytest.mark.asyncio
    async def test_mark_workflow_completed_not_found(self, workflow_service, mock_workflow_repo):
        """Test marking non-existent workflow as completed."""
        mock_workflow_repo.mark_workflow_completed = AsyncMock(return_value=None)

        with pytest.raises(RecordNotFoundError):
            await workflow_service.mark_workflow_completed("wf_nonexistent")


@pytest.mark.unit
class TestWorkflowServiceMarkFailed:
    """Tests for marking workflows as failed."""

    @pytest.mark.asyncio
    async def test_mark_workflow_failed_success(self, workflow_service, mock_workflow_repo):
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

        result = await workflow_service.mark_workflow_failed("wf_123", "Stage timeout")

        assert result.status == WorkflowStatus.FAILED
        assert result.error_message == "Stage timeout"
        mock_workflow_repo.mark_workflow_failed.assert_called_once()

    @pytest.mark.asyncio
    async def test_mark_workflow_failed_not_found(self, workflow_service, mock_workflow_repo):
        """Test marking non-existent workflow as failed."""
        mock_workflow_repo.mark_workflow_failed = AsyncMock(return_value=None)

        with pytest.raises(RecordNotFoundError):
            await workflow_service.mark_workflow_failed("wf_nonexistent", "Error")


@pytest.mark.unit
class TestWorkflowServiceListWorkflows:
    """Tests for listing workflows."""

    @pytest.mark.asyncio
    async def test_list_workflows_success(self, workflow_service, mock_workflow_repo):
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

        result = await workflow_service.list_workflows()

        assert len(result) == 2
        assert result[0].id == "wf_123"
        assert result[1].id == "wf_124"

    @pytest.mark.asyncio
    async def test_list_workflows_with_filters(self, workflow_service, mock_workflow_repo):
        """Test listing workflows with filters."""
        mock_workflow_repo.list_workflow_runs = AsyncMock(return_value=[])

        await workflow_service.list_workflows(program_id="prog_123", status="running", limit=50)

        mock_workflow_repo.list_workflow_runs.assert_called_once_with(
            program_id="prog_123", status="running", limit=50
        )

    @pytest.mark.asyncio
    async def test_list_workflows_empty(self, workflow_service, mock_workflow_repo):
        """Test listing workflows when none exist."""
        mock_workflow_repo.list_workflow_runs = AsyncMock(return_value=[])

        result = await workflow_service.list_workflows()

        assert result == []
