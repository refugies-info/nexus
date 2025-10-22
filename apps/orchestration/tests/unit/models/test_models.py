"""Unit tests for Pydantic models with validation."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from models.diff import DiffRequest, DiffResponse, ReviewStatus, RiskScore
from models.stage import StageExecutionRequest, StageExecutionResponse, StageStatus
from models.update import UpdateEventRequest, UpdateEventResponse, UpdateStatus, UpdateStrategy
from models.workflow import WorkflowRunRequest, WorkflowRunResponse, WorkflowStatus


@pytest.mark.unit
class TestWorkflowModels:
    """Tests for workflow models."""

    def test_workflow_run_request_valid(self) -> None:
        """Test creating a valid WorkflowRunRequest."""
        request = WorkflowRunRequest(
            program_id="prog_123",
            source="data_inclusion",
            initial_stage="ingestion",
        )

        assert request.program_id == "prog_123"
        assert request.source == "data_inclusion"
        assert request.initial_stage == "ingestion"

    def test_workflow_run_request_missing_required(self) -> None:
        """Test WorkflowRunRequest with missing required fields."""
        with pytest.raises(ValidationError):
            WorkflowRunRequest(program_id="prog_123")

    def test_workflow_run_response_valid(self) -> None:
        """Test creating a valid WorkflowRunResponse."""
        now = datetime.utcnow()
        response = WorkflowRunResponse(
            id="wf_123",
            program_id="prog_123",
            source="data_inclusion",
            current_stage="enrichment",
            status=WorkflowStatus.RUNNING,
            metadata={},
            created_at=now,
            updated_at=now,
        )

        assert response.id == "wf_123"
        assert response.status == WorkflowStatus.RUNNING

    def test_workflow_status_enum(self) -> None:
        """Test WorkflowStatus enum values."""
        assert WorkflowStatus.RUNNING == "running"
        assert WorkflowStatus.COMPLETED == "completed"
        assert WorkflowStatus.FAILED == "failed"
        assert WorkflowStatus.PAUSED == "paused"


@pytest.mark.unit
class TestStageModels:
    """Tests for stage models."""

    def test_stage_execution_request_valid(self) -> None:
        """Test creating a valid StageExecutionRequest."""
        request = StageExecutionRequest(
            workflow_id="wf_123",
            stage_name="enrichment",
            program_id="prog_123",
        )

        assert request.workflow_id == "wf_123"
        assert request.stage_name == "enrichment"

    def test_stage_execution_request_missing_required(self) -> None:
        """Test StageExecutionRequest with missing required fields."""
        with pytest.raises(ValidationError):
            StageExecutionRequest(workflow_id="wf_123")

    def test_stage_execution_response_valid(self) -> None:
        """Test creating a valid StageExecutionResponse."""
        now = datetime.utcnow()
        response = StageExecutionResponse(
            id="stage_123",
            workflow_id="wf_123",
            stage_name="enrichment",
            program_id="prog_123",
            status=StageStatus.COMPLETED,
            attempt=1,
            metadata={},
            created_at=now,
            updated_at=now,
        )

        assert response.id == "stage_123"
        assert response.status == StageStatus.COMPLETED
        assert response.attempt == 1

    def test_stage_status_enum(self) -> None:
        """Test StageStatus enum values."""
        assert StageStatus.PENDING == "pending"
        assert StageStatus.RUNNING == "running"
        assert StageStatus.COMPLETED == "completed"
        assert StageStatus.FAILED == "failed"
        assert StageStatus.SKIPPED == "skipped"


@pytest.mark.unit
class TestUpdateModels:
    """Tests for update models."""

    def test_update_event_request_valid(self) -> None:
        """Test creating a valid UpdateEventRequest."""
        request = UpdateEventRequest(
            program_id="prog_123",
            original_stage="enrichment",
            update_strategy=UpdateStrategy.SMART_CATCHUP,
            source_data={"name": "Updated"},
            checksum="abc123",
        )

        assert request.program_id == "prog_123"
        assert request.update_strategy == UpdateStrategy.SMART_CATCHUP

    def test_update_event_request_missing_required(self) -> None:
        """Test UpdateEventRequest with missing required fields."""
        with pytest.raises(ValidationError):
            UpdateEventRequest(program_id="prog_123")

    def test_update_event_response_valid(self) -> None:
        """Test creating a valid UpdateEventResponse."""
        now = datetime.utcnow()
        response = UpdateEventResponse(
            id="upd_123",
            program_id="prog_123",
            original_stage="enrichment",
            update_strategy=UpdateStrategy.FULL_REPROCESS,
            source_data={"name": "Updated"},
            checksum="abc123",
            status=UpdateStatus.COMPLETED,
            metadata={},
            created_at=now,
            updated_at=now,
        )

        assert response.id == "upd_123"
        assert response.status == UpdateStatus.COMPLETED

    def test_update_strategy_enum(self) -> None:
        """Test UpdateStrategy enum values."""
        assert UpdateStrategy.FULL_REPROCESS == "full_reprocess"
        assert UpdateStrategy.SMART_CATCHUP == "smart_catchup"

    def test_update_status_enum(self) -> None:
        """Test UpdateStatus enum values."""
        assert UpdateStatus.PENDING == "pending"
        assert UpdateStatus.PROCESSING == "processing"
        assert UpdateStatus.COMPLETED == "completed"
        assert UpdateStatus.FAILED == "failed"


@pytest.mark.unit
class TestDiffModels:
    """Tests for diff models."""

    def test_risk_score_valid(self) -> None:
        """Test creating a valid RiskScore."""
        risk = RiskScore(value=0.3, category="low")

        assert risk.value == 0.3
        assert risk.category == "low"
        assert risk.is_low_risk is True
        assert risk.is_medium_risk is False
        assert risk.is_high_risk is False

    def test_risk_score_high_risk(self) -> None:
        """Test RiskScore with high-risk value."""
        risk = RiskScore(value=0.85, category="high")

        assert risk.is_high_risk is True
        assert risk.is_medium_risk is False
        assert risk.is_low_risk is False

    def test_risk_score_medium_risk(self) -> None:
        """Test RiskScore with medium-risk value."""
        risk = RiskScore(value=0.65, category="medium")

        assert risk.is_medium_risk is True
        assert risk.is_high_risk is False
        assert risk.is_low_risk is False

    def test_risk_score_invalid_range(self) -> None:
        """Test RiskScore with invalid value range."""
        with pytest.raises(ValidationError):
            RiskScore(value=1.5, category="invalid")

    def test_diff_request_valid(self) -> None:
        """Test creating a valid DiffRequest."""
        request = DiffRequest(
            update_id="upd_123",
            program_id="prog_123",
            original_data={"name": "Original"},
            updated_data={"name": "Updated"},
            diff_content={"name": {"old": "Original", "new": "Updated"}},
            risk_score=0.3,
        )

        assert request.update_id == "upd_123"
        assert request.risk_score == 0.3

    def test_diff_request_missing_required(self) -> None:
        """Test DiffRequest with missing required fields."""
        with pytest.raises(ValidationError):
            DiffRequest(update_id="upd_123", program_id="prog_123")

    def test_diff_response_valid(self) -> None:
        """Test creating a valid DiffResponse."""
        now = datetime.utcnow()
        response = DiffResponse(
            id="diff_123",
            update_id="upd_123",
            program_id="prog_123",
            original_data={"name": "Original"},
            updated_data={"name": "Updated"},
            diff_content={"name": {"old": "Original", "new": "Updated"}},
            risk_score=RiskScore(value=0.3, category="low"),
            review_status=ReviewStatus.PENDING,
            metadata={},
            created_at=now,
            updated_at=now,
        )

        assert response.id == "diff_123"
        assert response.review_status == ReviewStatus.PENDING

    def test_review_status_enum(self) -> None:
        """Test ReviewStatus enum values."""
        assert ReviewStatus.PENDING == "pending"
        assert ReviewStatus.APPROVED == "approved"
        assert ReviewStatus.REJECTED == "rejected"
        assert ReviewStatus.NEEDS_EDIT == "needs_edit"

    def test_diff_response_with_reviewer_info(self) -> None:
        """Test DiffResponse with reviewer information."""
        now = datetime.utcnow()
        response = DiffResponse(
            id="diff_123",
            update_id="upd_123",
            program_id="prog_123",
            original_data={"name": "Original"},
            updated_data={"name": "Updated"},
            diff_content={"name": {"old": "Original", "new": "Updated"}},
            risk_score=RiskScore(value=0.3, category="low"),
            review_status=ReviewStatus.APPROVED,
            reviewer_id="user_123",
            review_notes="Looks good",
            metadata={},
            created_at=now,
            updated_at=now,
        )

        assert response.reviewer_id == "user_123"
        assert response.review_notes == "Looks good"


@pytest.mark.unit
class TestModelValidation:
    """Tests for model validation constraints."""

    def test_workflow_run_request_default_stage(self) -> None:
        """Test WorkflowRunRequest uses default initial_stage."""
        request = WorkflowRunRequest(
            program_id="prog_123",
            source="data_inclusion",
        )

        assert request.initial_stage == "ingestion"

    def test_workflow_run_request_default_metadata(self) -> None:
        """Test WorkflowRunRequest uses default empty metadata."""
        request = WorkflowRunRequest(
            program_id="prog_123",
            source="data_inclusion",
        )

        assert request.metadata == {}

    def test_update_event_request_default_metadata(self) -> None:
        """Test UpdateEventRequest uses default empty metadata."""
        request = UpdateEventRequest(
            program_id="prog_123",
            original_stage="enrichment",
            update_strategy=UpdateStrategy.SMART_CATCHUP,
            source_data={"name": "Updated"},
            checksum="abc123",
        )

        assert request.metadata == {}

    def test_diff_request_default_metadata(self) -> None:
        """Test DiffRequest uses default empty metadata."""
        request = DiffRequest(
            update_id="upd_123",
            program_id="prog_123",
            original_data={"name": "Original"},
            updated_data={"name": "Updated"},
            diff_content={"name": {"old": "Original", "new": "Updated"}},
            risk_score=0.3,
        )

        assert request.metadata == {}
