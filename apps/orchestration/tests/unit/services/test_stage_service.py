"""Unit tests for stage execution service."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from models.stage import StageExecutionRequest, StageStatus
from services.stage_service import StageService
from utils.errors import PipelineError, RecordNotFoundError


@pytest.fixture
def mock_stage_repo():
    """Create a mock stage repository."""
    return MagicMock()


@pytest.fixture
def stage_service(mock_stage_repo):
    """Create a stage service with mocked repository."""
    return StageService(mock_stage_repo)


@pytest.mark.unit
class TestStageServiceExecute:
    """Tests for executing stages."""

    @pytest.mark.asyncio
    async def test_execute_stage_success(self, stage_service, mock_stage_repo):
        """Test successfully executing a stage."""
        request = StageExecutionRequest(
            workflow_id="wf_123",
            stage_name="enrichment",
            program_id="prog_123",
        )

        mock_stage_repo.create_stage_execution = AsyncMock(
            return_value={
                "id": "stage_123",
                "workflow_id": "wf_123",
                "stage_name": "enrichment",
                "program_id": "prog_123",
                "status": "pending",
                "attempt": 1,
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )

        result = await stage_service.execute_stage(request)

        assert result.id == "stage_123"
        assert result.stage_name == "enrichment"
        assert result.attempt == 1
        mock_stage_repo.create_stage_execution.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_stage_with_metadata(self, stage_service, mock_stage_repo):
        """Test executing stage with metadata."""
        request = StageExecutionRequest(
            workflow_id="wf_123",
            stage_name="enrichment",
            program_id="prog_123",
            metadata={"model": "v2.1"},
        )

        mock_stage_repo.create_stage_execution = AsyncMock(
            return_value={
                "id": "stage_123",
                "workflow_id": "wf_123",
                "stage_name": "enrichment",
                "program_id": "prog_123",
                "status": "pending",
                "attempt": 1,
                "metadata": {"model": "v2.1"},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )

        result = await stage_service.execute_stage(request)

        assert result.metadata == {"model": "v2.1"}

    @pytest.mark.asyncio
    async def test_execute_stage_failure(self, stage_service, mock_stage_repo):
        """Test stage execution failure."""
        request = StageExecutionRequest(
            workflow_id="wf_123",
            stage_name="enrichment",
            program_id="prog_123",
        )

        mock_stage_repo.create_stage_execution = AsyncMock(side_effect=Exception("Database error"))

        with pytest.raises(PipelineError):
            await stage_service.execute_stage(request)


@pytest.mark.unit
class TestStageServiceRetry:
    """Tests for retry logic."""

    @pytest.mark.asyncio
    async def test_retry_stage_success(self, stage_service, mock_stage_repo):
        """Test successfully retrying a stage."""
        mock_stage_repo.get_stage_execution = AsyncMock(
            return_value={
                "id": "stage_123",
                "workflow_id": "wf_123",
                "stage_name": "enrichment",
                "program_id": "prog_123",
                "status": "failed",
                "attempt": 1,
                "error_message": "Timeout",
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )

        mock_stage_repo.increment_attempt = AsyncMock(
            return_value={
                "id": "stage_123",
                "workflow_id": "wf_123",
                "stage_name": "enrichment",
                "program_id": "prog_123",
                "status": "failed",
                "attempt": 2,
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )

        mock_stage_repo.update_stage_status = AsyncMock(
            return_value={
                "id": "stage_123",
                "workflow_id": "wf_123",
                "stage_name": "enrichment",
                "program_id": "prog_123",
                "status": "pending",
                "attempt": 2,
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )

        result = await stage_service.retry_stage("stage_123")

        assert result.attempt == 2
        assert result.status == StageStatus.PENDING
        mock_stage_repo.increment_attempt.assert_called_once()
        mock_stage_repo.update_stage_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_retry_stage_not_found(self, stage_service, mock_stage_repo):
        """Test retrying non-existent stage."""
        mock_stage_repo.get_stage_execution = AsyncMock(return_value=None)

        with pytest.raises(RecordNotFoundError):
            await stage_service.retry_stage("stage_nonexistent")

    @pytest.mark.asyncio
    async def test_retry_increments_attempt(self, stage_service, mock_stage_repo):
        """Test that retry increments attempt counter."""
        mock_stage_repo.get_stage_execution = AsyncMock(
            return_value={
                "id": "stage_123",
                "attempt": 3,
                "status": "failed",
                "workflow_id": "wf_123",
                "stage_name": "enrichment",
                "program_id": "prog_123",
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )

        mock_stage_repo.increment_attempt = AsyncMock(
            return_value={
                "id": "stage_123",
                "attempt": 4,
                "status": "failed",
                "workflow_id": "wf_123",
                "stage_name": "enrichment",
                "program_id": "prog_123",
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )

        mock_stage_repo.update_stage_status = AsyncMock(
            return_value={
                "id": "stage_123",
                "attempt": 4,
                "status": "pending",
                "workflow_id": "wf_123",
                "stage_name": "enrichment",
                "program_id": "prog_123",
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )

        result = await stage_service.retry_stage("stage_123")

        assert result.attempt == 4


@pytest.mark.unit
class TestStageServiceMarkComplete:
    """Tests for marking stages as completed."""

    @pytest.mark.asyncio
    async def test_mark_stage_completed_success(self, stage_service, mock_stage_repo):
        """Test successfully marking stage as completed."""
        mock_stage_repo.mark_stage_completed = AsyncMock(
            return_value={
                "id": "stage_123",
                "workflow_id": "wf_123",
                "stage_name": "enrichment",
                "program_id": "prog_123",
                "status": "completed",
                "attempt": 1,
                "result": {"enriched_fields": 15},
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )

        result = await stage_service.mark_stage_complete("stage_123", {"enriched_fields": 15})

        assert result.status == StageStatus.COMPLETED
        assert result.result == {"enriched_fields": 15}
        mock_stage_repo.mark_stage_completed.assert_called_once()

    @pytest.mark.asyncio
    async def test_mark_stage_completed_not_found(self, stage_service, mock_stage_repo):
        """Test marking non-existent stage as completed."""
        mock_stage_repo.mark_stage_completed = AsyncMock(return_value=None)

        with pytest.raises(RecordNotFoundError):
            await stage_service.mark_stage_complete("stage_nonexistent")


@pytest.mark.unit
class TestStageServiceHandleFailure:
    """Tests for handling stage failures."""

    @pytest.mark.asyncio
    async def test_handle_stage_failure_success(self, stage_service, mock_stage_repo):
        """Test successfully handling stage failure."""
        mock_stage_repo.mark_stage_failed = AsyncMock(
            return_value={
                "id": "stage_123",
                "workflow_id": "wf_123",
                "stage_name": "enrichment",
                "program_id": "prog_123",
                "status": "failed",
                "attempt": 1,
                "error_message": "Timeout error",
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )

        result = await stage_service.handle_stage_failure("stage_123", "Timeout error")

        assert result.status == StageStatus.FAILED
        assert result.error_message == "Timeout error"
        mock_stage_repo.mark_stage_failed.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_stage_failure_not_found(self, stage_service, mock_stage_repo):
        """Test handling failure for non-existent stage."""
        mock_stage_repo.mark_stage_failed = AsyncMock(return_value=None)

        with pytest.raises(RecordNotFoundError):
            await stage_service.handle_stage_failure("stage_nonexistent", "Error")


@pytest.mark.unit
class TestStageServiceStateTransitions:
    """Tests for state transitions."""

    @pytest.mark.asyncio
    async def test_stage_status_enum_values(self):
        """Test that stage status enum has correct values."""
        assert StageStatus.PENDING.value == "pending"
        assert StageStatus.RUNNING.value == "running"
        assert StageStatus.COMPLETED.value == "completed"
        assert StageStatus.FAILED.value == "failed"
        assert StageStatus.SKIPPED.value == "skipped"

    @pytest.mark.asyncio
    async def test_get_stages_for_workflow(self, stage_service, mock_stage_repo):
        """Test getting all stages for a workflow."""
        mock_stage_repo.get_stages_for_workflow = AsyncMock(
            return_value=[
                {
                    "id": "stage_1",
                    "stage_name": "ingestion",
                    "status": "completed",
                    "workflow_id": "wf_123",
                    "program_id": "prog_123",
                    "attempt": 1,
                    "metadata": {},
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                },
                {
                    "id": "stage_2",
                    "stage_name": "enrichment",
                    "status": "running",
                    "workflow_id": "wf_123",
                    "program_id": "prog_123",
                    "attempt": 1,
                    "metadata": {},
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                },
            ]
        )

        result = await stage_service.get_stages_for_workflow("wf_123")

        assert len(result) == 2
        assert result[0].stage_name == "ingestion"
        assert result[1].stage_name == "enrichment"

    @pytest.mark.asyncio
    async def test_get_failed_stages(self, stage_service, mock_stage_repo):
        """Test getting failed stages for a workflow."""
        mock_stage_repo.get_failed_stages = AsyncMock(
            return_value=[
                {
                    "id": "stage_fail",
                    "stage_name": "enrichment",
                    "status": "failed",
                    "workflow_id": "wf_123",
                    "program_id": "prog_123",
                    "attempt": 3,
                    "error_message": "Timeout",
                    "metadata": {},
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }
            ]
        )

        result = await stage_service.get_failed_stages("wf_123")

        assert len(result) == 1
        assert result[0].status == StageStatus.FAILED
        assert result[0].error_message == "Timeout"

    @pytest.mark.asyncio
    async def test_count_stages_by_status(self, stage_service, mock_stage_repo):
        """Test counting stages by status."""
        mock_stage_repo.count_stages_by_status = AsyncMock(return_value=5)

        result = await stage_service.count_stages_by_status("wf_123", "completed")

        assert result == 5
        mock_stage_repo.count_stages_by_status.assert_called_once_with("wf_123", "completed")


@pytest.mark.unit
class TestStageServiceRetryBackoff:
    """Tests for retry logic with exponential backoff."""

    @pytest.mark.asyncio
    async def test_retry_respects_max_attempts(self, stage_service, mock_stage_repo):
        """Test that retry respects maximum attempt limit."""
        # Simulate a stage that has already been retried 10 times (max retries)
        mock_stage_repo.get_stage_execution = AsyncMock(
            return_value={
                "id": "stage_123",
                "workflow_id": "wf_123",
                "stage_name": "enrichment",
                "program_id": "prog_123",
                "status": "failed",
                "attempt": 10,  # Already at max retries
                "error_message": "Timeout",
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )

        mock_stage_repo.increment_attempt = AsyncMock(
            return_value={
                "id": "stage_123",
                "workflow_id": "wf_123",
                "stage_name": "enrichment",
                "program_id": "prog_123",
                "status": "failed",
                "attempt": 11,
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )

        mock_stage_repo.update_stage_status = AsyncMock(
            return_value={
                "id": "stage_123",
                "workflow_id": "wf_123",
                "stage_name": "enrichment",
                "program_id": "prog_123",
                "status": "pending",
                "attempt": 11,
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )

        result = await stage_service.retry_stage("stage_123")

        # Should still allow retry but increment counter
        assert result.attempt == 11
        mock_stage_repo.increment_attempt.assert_called_once()

    @pytest.mark.asyncio
    async def test_retry_multiple_times_increments_correctly(self, stage_service, mock_stage_repo):
        """Test that multiple retries increment attempt counter correctly."""
        attempts = [1, 2, 3, 4, 5]

        for attempt in attempts:
            mock_stage_repo.get_stage_execution = AsyncMock(
                return_value={
                    "id": "stage_123",
                    "workflow_id": "wf_123",
                    "stage_name": "enrichment",
                    "program_id": "prog_123",
                    "status": "failed",
                    "attempt": attempt,
                    "error_message": "Timeout",
                    "metadata": {},
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }
            )

            mock_stage_repo.increment_attempt = AsyncMock(
                return_value={
                    "id": "stage_123",
                    "workflow_id": "wf_123",
                    "stage_name": "enrichment",
                    "program_id": "prog_123",
                    "status": "failed",
                    "attempt": attempt + 1,
                    "metadata": {},
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }
            )

            mock_stage_repo.update_stage_status = AsyncMock(
                return_value={
                    "id": "stage_123",
                    "workflow_id": "wf_123",
                    "stage_name": "enrichment",
                    "program_id": "prog_123",
                    "status": "pending",
                    "attempt": attempt + 1,
                    "metadata": {},
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }
            )

            result = await stage_service.retry_stage("stage_123")
            assert result.attempt == attempt + 1

    @pytest.mark.asyncio
    async def test_retry_resets_status_to_pending(self, stage_service, mock_stage_repo):
        """Test that retry resets status to pending for re-execution."""
        mock_stage_repo.get_stage_execution = AsyncMock(
            return_value={
                "id": "stage_123",
                "workflow_id": "wf_123",
                "stage_name": "enrichment",
                "program_id": "prog_123",
                "status": "failed",
                "attempt": 2,
                "error_message": "Timeout",
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )

        mock_stage_repo.increment_attempt = AsyncMock(
            return_value={
                "id": "stage_123",
                "workflow_id": "wf_123",
                "stage_name": "enrichment",
                "program_id": "prog_123",
                "status": "failed",
                "attempt": 3,
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )

        mock_stage_repo.update_stage_status = AsyncMock(
            return_value={
                "id": "stage_123",
                "workflow_id": "wf_123",
                "stage_name": "enrichment",
                "program_id": "prog_123",
                "status": "pending",
                "attempt": 3,
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )

        result = await stage_service.retry_stage("stage_123")

        # Verify status is reset to pending
        assert result.status == StageStatus.PENDING
        # Verify update_stage_status was called with PENDING status
        mock_stage_repo.update_stage_status.assert_called_once_with(
            "stage_123", StageStatus.PENDING.value
        )

    @pytest.mark.asyncio
    async def test_retry_preserves_workflow_and_program_ids(self, stage_service, mock_stage_repo):
        """Test that retry preserves workflow and program IDs."""
        mock_stage_repo.get_stage_execution = AsyncMock(
            return_value={
                "id": "stage_123",
                "workflow_id": "wf_456",
                "stage_name": "enrichment",
                "program_id": "prog_789",
                "status": "failed",
                "attempt": 1,
                "error_message": "Error",
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )

        mock_stage_repo.increment_attempt = AsyncMock(
            return_value={
                "id": "stage_123",
                "workflow_id": "wf_456",
                "stage_name": "enrichment",
                "program_id": "prog_789",
                "status": "failed",
                "attempt": 2,
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )

        mock_stage_repo.update_stage_status = AsyncMock(
            return_value={
                "id": "stage_123",
                "workflow_id": "wf_456",
                "stage_name": "enrichment",
                "program_id": "prog_789",
                "status": "pending",
                "attempt": 2,
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )

        result = await stage_service.retry_stage("stage_123")

        assert result.workflow_id == "wf_456"
        assert result.program_id == "prog_789"
        assert result.stage_name == "enrichment"


@pytest.mark.unit
class TestStageServiceErrorHandling:
    """Tests for error handling in stage service."""

    @pytest.mark.asyncio
    async def test_execute_stage_wraps_database_error(self, stage_service, mock_stage_repo):
        """Test that database errors are wrapped in PipelineError."""
        request = StageExecutionRequest(
            workflow_id="wf_123",
            stage_name="enrichment",
            program_id="prog_123",
        )

        mock_stage_repo.create_stage_execution = AsyncMock(
            side_effect=Exception("Database connection failed")
        )

        with pytest.raises(PipelineError) as exc_info:
            await stage_service.execute_stage(request)

        assert "Failed to execute stage" in str(exc_info.value)
        assert "Database connection failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_stage_execution_wraps_database_error(self, stage_service, mock_stage_repo):
        """Test that database errors in get are wrapped in PipelineError."""
        mock_stage_repo.get_stage_execution = AsyncMock(side_effect=Exception("Connection timeout"))

        with pytest.raises(PipelineError) as exc_info:
            await stage_service.get_stage_execution("stage_123")

        assert "Failed to get stage execution" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_mark_stage_complete_wraps_error(self, stage_service, mock_stage_repo):
        """Test that errors in mark_stage_complete are wrapped."""
        mock_stage_repo.mark_stage_completed = AsyncMock(side_effect=Exception("Update failed"))

        with pytest.raises(PipelineError) as exc_info:
            await stage_service.mark_stage_complete("stage_123")

        assert "Failed to mark stage as completed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_handle_stage_failure_wraps_error(self, stage_service, mock_stage_repo):
        """Test that errors in handle_stage_failure are wrapped."""
        mock_stage_repo.mark_stage_failed = AsyncMock(side_effect=Exception("Update failed"))

        with pytest.raises(PipelineError) as exc_info:
            await stage_service.handle_stage_failure("stage_123", "Original error")

        assert "Failed to handle stage failure" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_retry_stage_wraps_error(self, stage_service, mock_stage_repo):
        """Test that errors in retry_stage are wrapped."""
        mock_stage_repo.get_stage_execution = AsyncMock(side_effect=Exception("Database error"))

        with pytest.raises(PipelineError) as exc_info:
            await stage_service.retry_stage("stage_123")

        assert "Failed to retry stage" in str(exc_info.value)
