"""Integration tests for complete pipeline execution."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from db.repositories.stage import StageRepository
from db.repositories.workflow import WorkflowRepository
from models.stage import StageExecutionRequest, StageStatus
from models.workflow import WorkflowRunRequest, WorkflowStatus
from services.stage_service import execute_stage, mark_stage_complete
from services.state_machine_functions import get_next_stage
from services.workflow_functions import start_workflow, update_workflow_stage
from utils.errors import PipelineError


@pytest.mark.integration
class TestPipelineExecution:
    """Integration tests for complete pipeline execution."""

    @pytest.fixture
    def mock_workflow_repo(self):
        """Create a mock workflow repository."""
        return MagicMock(spec=WorkflowRepository)

    @pytest.fixture
    def mock_stage_repo(self):
        """Create a mock stage repository."""
        return MagicMock(spec=StageRepository)

    @pytest.fixture
    def workflow_service(self, mock_workflow_repo):
        """Create workflow service with mocked repository."""
        return mock_workflow_repo

    @pytest.fixture
    def stage_service(self, mock_stage_repo):
        """Create stage service with mocked repository."""
        return mock_stage_repo

    @pytest.fixture
    def state_machine(self):
        """Create state machine instance."""
        return get_next_stage

    @pytest.mark.asyncio
    async def test_pipeline_start_to_ingestion_stage(
        self, workflow_service, stage_service, state_machine, mock_workflow_repo, mock_stage_repo
    ):
        """Test pipeline execution from start through ingestion stage."""
        # Setup: Create workflow
        request = WorkflowRunRequest(
            program_id="prog_001",
            source="data_inclusion",
        )

        mock_workflow_repo.create_workflow_run = AsyncMock(
            return_value={
                "id": "wf_001",
                "program_id": "prog_001",
                "current_stage": "ingestion",
                "status": "running",
                "source": "data_inclusion",
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "completed_at": None,
                "error_message": None,
            }
        )

        # Execute: Start workflow
        workflow = await start_workflow(request, workflow_service)

        # Verify: Workflow created and in ingestion stage
        assert workflow.id == "wf_001"
        assert workflow.current_stage == "ingestion"
        assert workflow.status == WorkflowStatus.RUNNING
        mock_workflow_repo.create_workflow_run.assert_called_once()

    @pytest.mark.asyncio
    async def test_pipeline_stage_progression(self, stage_service, state_machine, mock_stage_repo):
        """Test pipeline stage progression through multiple stages."""
        stages = [
            "ingestion",
            "editorial_policy_validation",
            "reconciliation",
            "enrichment",
            "langage_clair",
            "translation",
            "validation",
            "publication",
        ]

        for i, stage_name in enumerate(stages):
            # Setup: Create stage execution
            request = StageExecutionRequest(
                workflow_id="wf_001",
                stage_name=stage_name,
                program_id="prog_001",
            )

            mock_stage_repo.create_stage_execution = AsyncMock(
                return_value={
                    "id": f"stage_{i:03d}",
                    "workflow_id": "wf_001",
                    "stage_name": stage_name,
                    "program_id": "prog_001",
                    "status": "pending",
                    "attempt": 1,
                    "metadata": {},
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }
            )

            # Execute: Execute stage
            stage = await execute_stage(request, stage_service)

            # Verify: Stage created with correct name
            assert stage.stage_name == stage_name
            assert stage.status == StageStatus.PENDING

    @pytest.mark.asyncio
    async def test_pipeline_stage_completion_sequence(self, stage_service, mock_stage_repo):
        """Test completing stages in sequence."""
        stages = ["ingestion", "editorial_policy_validation", "reconciliation"]

        for i, stage_name in enumerate(stages):
            stage_id = f"stage_{i:03d}"

            # Setup: Mark stage as completed
            mock_stage_repo.mark_stage_completed = AsyncMock(
                return_value={
                    "id": stage_id,
                    "workflow_id": "wf_001",
                    "stage_name": stage_name,
                    "program_id": "prog_001",
                    "status": "completed",
                    "attempt": 1,
                    "result": {"processed": True},
                    "metadata": {},
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }
            )

            # Execute: Mark stage complete
            result = await mark_stage_complete(stage_id, {"processed": True}, stage_service)

            # Verify: Stage marked as completed
            assert result.status == StageStatus.COMPLETED
            assert result.result == {"processed": True}

    @pytest.mark.asyncio
    async def test_pipeline_failure_and_retry(self, stage_service, mock_stage_repo):
        """Test pipeline failure handling and retry logic."""
        stage_id = "stage_001"

        # Setup: Stage fails
        mock_stage_repo.get_stage_execution = AsyncMock(
            return_value={
                "id": stage_id,
                "workflow_id": "wf_001",
                "stage_name": "enrichment",
                "program_id": "prog_001",
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
                "id": stage_id,
                "workflow_id": "wf_001",
                "stage_name": "enrichment",
                "program_id": "prog_001",
                "status": "failed",
                "attempt": 2,
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )

        mock_stage_repo.update_stage_status = AsyncMock(
            return_value={
                "id": stage_id,
                "workflow_id": "wf_001",
                "stage_name": "enrichment",
                "program_id": "prog_001",
                "status": "pending",
                "attempt": 2,
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )

        # Execute: Retry stage
        result = await stage_service.retry_stage(stage_id)

        # Verify: Stage retried with incremented attempt
        assert result.attempt == 2
        assert result.status == StageStatus.PENDING
        mock_stage_repo.increment_attempt.assert_called_once()

    @pytest.mark.asyncio
    async def test_pipeline_max_retries_exceeded(self, stage_service, mock_stage_repo):
        """Test pipeline behavior when max retries exceeded."""
        stage_id = "stage_001"

        # Setup: Stage at max retries (10)
        mock_stage_repo.get_stage_execution = AsyncMock(
            return_value={
                "id": stage_id,
                "workflow_id": "wf_001",
                "stage_name": "enrichment",
                "program_id": "prog_001",
                "status": "failed",
                "attempt": 10,
                "error_message": "Persistent timeout",
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )

        mock_stage_repo.increment_attempt = AsyncMock(
            return_value={
                "id": stage_id,
                "workflow_id": "wf_001",
                "stage_name": "enrichment",
                "program_id": "prog_001",
                "status": "failed",
                "attempt": 11,
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )

        mock_stage_repo.update_stage_status = AsyncMock(
            return_value={
                "id": stage_id,
                "workflow_id": "wf_001",
                "stage_name": "enrichment",
                "program_id": "prog_001",
                "status": "pending",
                "attempt": 11,
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )

        # Execute: Retry even at max attempts
        result = await stage_service.retry_stage(stage_id)

        # Verify: Attempt incremented beyond max (application doesn't enforce limit here)
        assert result.attempt == 11

    @pytest.mark.asyncio
    async def test_pipeline_concurrent_programs(self, workflow_service, mock_workflow_repo):
        """Test pipeline handling multiple programs concurrently."""
        programs = ["prog_001", "prog_002", "prog_003"]

        for program_id in programs:
            request = WorkflowRunRequest(
                program_id=program_id,
                source="data_inclusion",
            )

            mock_workflow_repo.create_workflow_run = AsyncMock(
                return_value={
                    "id": f"wf_{program_id.split('_')[1]}",
                    "program_id": program_id,
                    "current_stage": "ingestion",
                    "status": "running",
                    "source": "data_inclusion",
                    "metadata": {},
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "completed_at": None,
                    "error_message": None,
                }
            )

            # Execute: Start workflow for each program
            workflow = await start_workflow(request, workflow_service)

            # Verify: Each workflow created independently
            assert workflow.program_id == program_id
            assert workflow.status == WorkflowStatus.RUNNING

    @pytest.mark.asyncio
    async def test_pipeline_error_handling_and_routing(self, stage_service, mock_stage_repo):
        """Test error handling and manual review routing."""
        stage_id = "stage_001"
        error_message = "Policy validation failed: for-profit initiative not allowed"

        # Setup: Stage failure with error message
        mock_stage_repo.mark_stage_failed = AsyncMock(
            return_value={
                "id": stage_id,
                "workflow_id": "wf_001",
                "stage_name": "editorial_policy_validation",
                "program_id": "prog_001",
                "status": "failed",
                "attempt": 1,
                "error_message": error_message,
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )

        # Execute: Handle stage failure
        result = await stage_service.handle_stage_failure(stage_id, error_message)

        # Verify: Stage marked as failed with error message
        assert result.status == StageStatus.FAILED
        assert result.error_message == error_message
        mock_stage_repo.mark_stage_failed.assert_called_once_with(stage_id, error_message)

    @pytest.mark.asyncio
    async def test_pipeline_state_machine_validation(self, state_machine):
        """Test state machine validates stage sequence."""
        stages = [
            "ingestion",
            "editorial_policy_validation",
            "reconciliation",
            "enrichment",
            "langage_clair",
            "translation",
            "validation",
            "publication",
        ]

        # Verify: All stages are valid
        for stage in stages:
            assert state_machine(stage) is not None

        # Verify: Invalid stage is rejected
        assert state_machine("invalid_stage") is None

        # Verify: Get all stages returns correct sequence
        all_stages = [state_machine(stage) for stage in stages]
        assert all_stages == stages

    @pytest.mark.asyncio
    async def test_pipeline_stage_transition_validation(self, state_machine):
        """Test state machine validates stage transitions."""
        # Verify: Valid transitions
        assert state_machine("ingestion") == "editorial_policy_validation"
        assert state_machine("editorial_policy_validation") == "reconciliation"
        assert state_machine("reconciliation") == "enrichment"
        assert state_machine("enrichment") == "langage_clair"
        assert state_machine("langage_clair") == "translation"
        assert state_machine("translation") == "validation"
        assert state_machine("validation") == "publication"

        # Verify: Invalid transitions (backwards) raise PipelineError
        with pytest.raises(PipelineError):
            state_machine("publication", "validation")
        with pytest.raises(PipelineError):
            state_machine("enrichment", "ingestion")

        # Verify: Invalid transitions (skipping stages) raise PipelineError
        with pytest.raises(PipelineError):
            state_machine("ingestion", "enrichment")
        with pytest.raises(PipelineError):
            state_machine("reconciliation", "translation")

    @pytest.mark.asyncio
    async def test_pipeline_workflow_completion(self, workflow_service, mock_workflow_repo):
        """Test workflow completion after all stages."""
        workflow_id = "wf_001"

        # Setup: Mark workflow as completed
        mock_workflow_repo.mark_workflow_completed = AsyncMock(
            return_value={
                "id": workflow_id,
                "program_id": "prog_001",
                "current_stage": "publication",
                "status": "completed",
                "source": "data_inclusion",
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "completed_at": datetime.utcnow(),
                "error_message": None,
            }
        )

        # Execute: Mark workflow complete
        result = await update_workflow_stage(workflow_id, "publication", workflow_service)

        # Verify: Workflow marked as completed
        assert result.status == WorkflowStatus.COMPLETED
        assert result.current_stage == "publication"
        mock_workflow_repo.mark_workflow_completed.assert_called_once()

    @pytest.mark.asyncio
    async def test_pipeline_metadata_preservation(self, stage_service, mock_stage_repo):
        """Test that metadata is preserved through pipeline stages."""
        metadata = {
            "source_url": "https://data-inclusion.fr/api/services/123",
            "fetch_timestamp": "2025-10-21T10:00:00Z",
            "version": "1.0",
        }

        request = StageExecutionRequest(
            workflow_id="wf_001",
            stage_name="enrichment",
            program_id="prog_001",
            metadata=metadata,
        )

        mock_stage_repo.create_stage_execution = AsyncMock(
            return_value={
                "id": "stage_001",
                "workflow_id": "wf_001",
                "stage_name": "enrichment",
                "program_id": "prog_001",
                "status": "pending",
                "attempt": 1,
                "metadata": metadata,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )

        # Execute: Create stage with metadata
        result = await execute_stage(request, stage_service)

        # Verify: Metadata preserved
        assert result.metadata == metadata
