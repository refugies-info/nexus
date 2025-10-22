"""Contract tests for workflow API endpoints.

These tests validate that API responses match the OpenAPI contract specification
defined in specs/002-orchestration-decision/contracts/orchestration-api.yaml
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from models.stage import StageExecutionRequest, StageExecutionResponse, StageStatus
from models.workflow import WorkflowRunRequest, WorkflowRunResponse, WorkflowStatus


@pytest.mark.contract
class TestWorkflowAPIContract:
    """Contract tests for workflow API endpoints."""

    @pytest.fixture
    def workflow_request_valid(self) -> dict:
        """Valid StartWorkflowRequest payload."""
        return {
            "program_id": "emplois-de-linclusion--17",
            "source": "data_inclusion",
        }

    @pytest.fixture
    def workflow_response_valid(self) -> dict:
        """Valid WorkflowResponse payload."""
        return {
            "id": "wf_001",
            "program_id": "emplois-de-linclusion--17",
            "current_stage": "ingestion",
            "status": "running",
            "source": "data_inclusion",
            "metadata": {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "completed_at": None,
            "error_message": None,
        }

    @pytest.mark.asyncio
    async def test_start_workflow_request_schema_valid(self, workflow_request_valid):
        """Test StartWorkflowRequest schema validation."""
        # Should not raise ValidationError
        request = WorkflowRunRequest(**workflow_request_valid)
        assert request.program_id == "emplois-de-linclusion--17"
        assert request.source == "data_inclusion"

    @pytest.mark.asyncio
    async def test_start_workflow_request_missing_program_id(self):
        """Test StartWorkflowRequest rejects missing program_id."""
        with pytest.raises(ValidationError) as exc_info:
            WorkflowRunRequest(source="data_inclusion")

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("program_id",) for e in errors)

    @pytest.mark.asyncio
    async def test_start_workflow_request_missing_source(self):
        """Test StartWorkflowRequest rejects missing source."""
        with pytest.raises(ValidationError) as exc_info:
            WorkflowRunRequest(program_id="prog_001")

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("source",) for e in errors)

    @pytest.mark.asyncio
    async def test_workflow_response_schema_valid(self, workflow_response_valid):
        """Test WorkflowResponse schema validation."""
        # Should not raise ValidationError
        response = WorkflowRunResponse(**workflow_response_valid)
        assert response.id == "wf_001"
        assert response.program_id == "emplois-de-linclusion--17"
        assert response.current_stage == "ingestion"
        assert response.status == WorkflowStatus.RUNNING

    @pytest.mark.asyncio
    async def test_workflow_response_status_enum_values(self):
        """Test WorkflowResponse status enum values."""
        valid_statuses = ["running", "completed", "failed", "paused"]

        for status in valid_statuses:
            response_data = {
                "id": "wf_001",
                "program_id": "prog_001",
                "current_stage": "ingestion",
                "status": status,
                "source": "data_inclusion",
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "error_message": None,
            }
            response = WorkflowRunResponse(**response_data)
            assert response.status.value == status

    @pytest.mark.asyncio
    async def test_workflow_response_current_stage_enum_values(self):
        """Test WorkflowResponse current_stage enum values."""
        valid_stages = [
            "ingestion",
            "editorial_policy_validation",
            "reconciliation",
            "enrichment",
            "langage_clair",
            "translation",
            "validation",
            "publication",
        ]

        for stage in valid_stages:
            response_data = {
                "id": "wf_001",
                "program_id": "prog_001",
                "current_stage": stage,
                "status": "running",
                "source": "data_inclusion",
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "completed_at": None,
                "error_message": None,
            }
            response = WorkflowRunResponse(**response_data)
            assert response.current_stage == stage

    @pytest.mark.asyncio
    async def test_workflow_response_invalid_status(self):
        """Test WorkflowResponse rejects invalid status."""
        response_data = {
            "id": "wf_001",
            "program_id": "prog_001",
            "current_stage": "ingestion",
            "status": "invalid_status",
            "source": "data_inclusion",
            "metadata": {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "completed_at": None,
            "error_message": None,
        }

        with pytest.raises(ValidationError):
            WorkflowRunResponse(**response_data)

    @pytest.mark.asyncio
    async def test_workflow_response_with_valid_stage(self):
        """Test WorkflowResponse accepts valid stage."""
        response_data = {
            "id": "wf_001",
            "program_id": "prog_001",
            "current_stage": "enrichment",
            "status": "running",
            "source": "data_inclusion",
            "metadata": {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "error_message": None,
        }

        response = WorkflowRunResponse(**response_data)
        assert response.current_stage == "enrichment"

    @pytest.mark.asyncio
    async def test_workflow_response_nullable_fields(self):
        """Test WorkflowResponse nullable fields."""
        response_data = {
            "id": "wf_001",
            "program_id": "prog_001",
            "current_stage": "ingestion",
            "status": "running",
            "source": "data_inclusion",
            "metadata": {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "error_message": None,
        }

        response = WorkflowRunResponse(**response_data)
        assert response.error_message is None

    @pytest.mark.asyncio
    async def test_workflow_response_with_error_message(self):
        """Test WorkflowResponse with error message."""
        response_data = {
            "id": "wf_001",
            "program_id": "prog_001",
            "current_stage": "enrichment",
            "status": "failed",
            "source": "data_inclusion",
            "metadata": {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "completed_at": datetime.utcnow(),
            "error_message": "Stage execution timeout",
        }

        response = WorkflowRunResponse(**response_data)
        assert response.error_message == "Stage execution timeout"
        assert response.status == WorkflowStatus.FAILED


@pytest.mark.contract
class TestStageExecutionAPIContract:
    """Contract tests for stage execution API endpoints."""

    @pytest.fixture
    def execute_stage_request_valid(self) -> dict:
        """Valid ExecuteStageRequest payload."""
        return {
            "workflow_id": "wf_001",
            "stage_name": "enrichment",
            "program_id": "prog_001",
            "metadata": {"model": "v2.1"},
        }

    @pytest.fixture
    def stage_execution_response_valid(self) -> dict:
        """Valid StageExecutionResponse payload."""
        return {
            "id": "stage_001",
            "workflow_id": "wf_001",
            "stage_name": "enrichment",
            "program_id": "prog_001",
            "status": "pending",
            "attempt": 1,
            "result": None,
            "error_message": None,
            "metadata": {"model": "v2.1"},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

    @pytest.mark.asyncio
    async def test_execute_stage_request_schema_valid(self, execute_stage_request_valid):
        """Test ExecuteStageRequest schema validation."""
        request = StageExecutionRequest(**execute_stage_request_valid)
        assert request.workflow_id == "wf_001"
        assert request.stage_name == "enrichment"
        assert request.program_id == "prog_001"

    @pytest.mark.asyncio
    async def test_execute_stage_request_missing_workflow_id(self):
        """Test ExecuteStageRequest rejects missing workflow_id."""
        with pytest.raises(ValidationError) as exc_info:
            StageExecutionRequest(
                stage_name="enrichment",
                program_id="prog_001",
            )

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("workflow_id",) for e in errors)

    @pytest.mark.asyncio
    async def test_execute_stage_request_missing_stage_name(self):
        """Test ExecuteStageRequest rejects missing stage_name."""
        with pytest.raises(ValidationError) as exc_info:
            StageExecutionRequest(
                workflow_id="wf_001",
                program_id="prog_001",
            )

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("stage_name",) for e in errors)

    @pytest.mark.asyncio
    async def test_stage_execution_response_schema_valid(self, stage_execution_response_valid):
        """Test StageExecutionResponse schema validation."""
        response = StageExecutionResponse(**stage_execution_response_valid)
        assert response.id == "stage_001"
        assert response.stage_name == "enrichment"
        assert response.status == StageStatus.PENDING

    @pytest.mark.asyncio
    async def test_stage_execution_response_status_enum_values(self):
        """Test StageExecutionResponse status enum values."""
        valid_statuses = ["pending", "running", "completed", "failed", "skipped"]

        for status in valid_statuses:
            response_data = {
                "id": "stage_001",
                "workflow_id": "wf_001",
                "stage_name": "enrichment",
                "program_id": "prog_001",
                "status": status,
                "attempt": 1,
                "result": None,
                "error_message": None,
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            response = StageExecutionResponse(**response_data)
            assert response.status.value == status

    @pytest.mark.asyncio
    async def test_stage_execution_response_invalid_status(self):
        """Test StageExecutionResponse rejects invalid status."""
        response_data = {
            "id": "stage_001",
            "workflow_id": "wf_001",
            "stage_name": "enrichment",
            "program_id": "prog_001",
            "status": "invalid_status",
            "attempt": 1,
            "result": None,
            "error_message": None,
            "metadata": {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        with pytest.raises(ValidationError):
            StageExecutionResponse(**response_data)

    @pytest.mark.asyncio
    async def test_stage_execution_response_with_result(self):
        """Test StageExecutionResponse with result data."""
        response_data = {
            "id": "stage_001",
            "workflow_id": "wf_001",
            "stage_name": "enrichment",
            "program_id": "prog_001",
            "status": "completed",
            "attempt": 1,
            "result": {"enriched_fields": 15, "processing_time_ms": 1234},
            "error_message": None,
            "metadata": {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        response = StageExecutionResponse(**response_data)
        assert response.result == {"enriched_fields": 15, "processing_time_ms": 1234}
        assert response.status == StageStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_stage_execution_response_with_error(self):
        """Test StageExecutionResponse with error message."""
        response_data = {
            "id": "stage_001",
            "workflow_id": "wf_001",
            "stage_name": "enrichment",
            "program_id": "prog_001",
            "status": "failed",
            "attempt": 3,
            "result": None,
            "error_message": "API timeout after 30 seconds",
            "metadata": {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        response = StageExecutionResponse(**response_data)
        assert response.error_message == "API timeout after 30 seconds"
        assert response.attempt == 3

    @pytest.mark.asyncio
    async def test_stage_execution_response_attempt_counter(self):
        """Test StageExecutionResponse attempt counter."""
        for attempt in [1, 2, 5, 10]:
            response_data = {
                "id": "stage_001",
                "workflow_id": "wf_001",
                "stage_name": "enrichment",
                "program_id": "prog_001",
                "status": "pending",
                "attempt": attempt,
                "result": None,
                "error_message": None,
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }

            response = StageExecutionResponse(**response_data)
            assert response.attempt == attempt


@pytest.mark.contract
class TestAPIResponseConsistency:
    """Contract tests for API response consistency."""

    @pytest.mark.asyncio
    async def test_workflow_response_completed_at_field(self):
        """Test WorkflowResponse completed_at field."""
        response_data = {
            "id": "wf_001",
            "program_id": "prog_001",
            "current_stage": "publication",
            "status": "completed",
            "source": "data_inclusion",
            "metadata": {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "error_message": None,
        }

        response = WorkflowRunResponse(**response_data)
        assert response.status == WorkflowStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_stage_execution_response_metadata_preservation(self):
        """Test StageExecutionResponse preserves metadata."""
        metadata = {
            "model": "gpt-4",
            "processing_time_ms": 1234,
            "tokens_used": 500,
        }

        response_data = {
            "id": "stage_001",
            "workflow_id": "wf_001",
            "stage_name": "enrichment",
            "program_id": "prog_001",
            "status": "completed",
            "attempt": 1,
            "result": None,
            "error_message": None,
            "metadata": metadata,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        response = StageExecutionResponse(**response_data)
        assert response.metadata == metadata
