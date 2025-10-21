"""Unit tests for WorkflowRepository - Test-Driven Development approach."""

import uuid
from typing import Any

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from db.repositories.workflow import WorkflowRepository


@pytest_asyncio.fixture
async def workflow_repo(db_session: AsyncSession) -> WorkflowRepository:
    """Create a WorkflowRepository instance for testing."""

    # Mock Supabase client - we'll use direct SQLAlchemy for tests
    class MockSupabaseClient:
        def __init__(self, session: AsyncSession):
            self.session = session

    client = MockSupabaseClient(db_session)
    repo = WorkflowRepository(client)
    repo.session = db_session  # Inject session for testing
    return repo


@pytest.mark.unit
class TestWorkflowRepositoryCreate:
    """Tests for creating workflow runs."""

    async def test_create_workflow_run_with_minimal_data(
        self, workflow_repo: WorkflowRepository, sample_workflow_data: dict[str, Any]
    ):
        """Test creating a workflow run with required fields."""
        result = await workflow_repo.create_workflow_run(
            program_id=sample_workflow_data["program_id"],
            source=sample_workflow_data["source"],
        )

        assert result is not None
        assert result["program_id"] == sample_workflow_data["program_id"]
        assert result["source"] == sample_workflow_data["source"]
        assert result["current_stage"] == "ingestion"
        assert result["status"] == "running"
        assert result["metadata"] == {}

    async def test_create_workflow_run_with_metadata(
        self, workflow_repo: WorkflowRepository, sample_workflow_data: dict[str, Any]
    ):
        """Test creating a workflow run with metadata."""
        metadata = {"key": "value", "nested": {"data": 123}}

        result = await workflow_repo.create_workflow_run(
            program_id=sample_workflow_data["program_id"],
            source=sample_workflow_data["source"],
            metadata=metadata,
        )

        assert result["metadata"] == metadata

    async def test_create_workflow_run_with_custom_stage(
        self, workflow_repo: WorkflowRepository, sample_workflow_data: dict[str, Any]
    ):
        """Test creating a workflow run with custom initial stage."""
        result = await workflow_repo.create_workflow_run(
            program_id=sample_workflow_data["program_id"],
            source=sample_workflow_data["source"],
            initial_stage="reconciliation",
        )

        assert result["current_stage"] == "reconciliation"

    async def test_create_workflow_run_timestamps(
        self, workflow_repo: WorkflowRepository, sample_workflow_data: dict[str, Any]
    ):
        """Test that timestamps are set correctly."""
        result = await workflow_repo.create_workflow_run(
            program_id=sample_workflow_data["program_id"],
            source=sample_workflow_data["source"],
        )

        assert result["created_at"] is not None
        assert result["updated_at"] is not None
        assert isinstance(result["created_at"], str)


@pytest.mark.unit
class TestWorkflowRepositoryRead:
    """Tests for reading workflow runs."""

    async def test_get_workflow_run_by_id(
        self, workflow_repo: WorkflowRepository, sample_workflow_data: dict[str, Any]
    ):
        """Test retrieving a workflow run by ID."""
        created = await workflow_repo.create_workflow_run(
            program_id=sample_workflow_data["program_id"],
            source=sample_workflow_data["source"],
        )

        retrieved = await workflow_repo.get_workflow_run(created["id"])

        assert retrieved is not None
        assert retrieved["id"] == created["id"]
        assert retrieved["program_id"] == sample_workflow_data["program_id"]

    async def test_get_workflow_run_not_found(self, workflow_repo: WorkflowRepository):
        """Test retrieving a non-existent workflow run."""
        result = await workflow_repo.get_workflow_run(str(uuid.uuid4()))

        assert result is None

    async def test_list_workflow_runs_all(
        self, workflow_repo: WorkflowRepository, sample_workflow_data: dict[str, Any]
    ):
        """Test listing all workflow runs."""
        # Create multiple workflows
        for i in range(3):
            await workflow_repo.create_workflow_run(
                program_id=f"prog_{i:03d}",
                source=sample_workflow_data["source"],
            )

        results = await workflow_repo.list_workflow_runs()

        assert len(results) >= 3

    async def test_list_workflow_runs_with_limit(
        self, workflow_repo: WorkflowRepository, sample_workflow_data: dict[str, Any]
    ):
        """Test listing workflow runs with limit."""
        for i in range(5):
            await workflow_repo.create_workflow_run(
                program_id=f"prog_{i:03d}",
                source=sample_workflow_data["source"],
            )

        results = await workflow_repo.list_workflow_runs(limit=2)

        assert len(results) <= 2

    async def test_list_workflow_runs_filter_by_program_id(
        self, workflow_repo: WorkflowRepository, sample_workflow_data: dict[str, Any]
    ):
        """Test filtering workflow runs by program_id."""
        target_program = "prog_filter_test"

        await workflow_repo.create_workflow_run(
            program_id=target_program,
            source=sample_workflow_data["source"],
        )
        await workflow_repo.create_workflow_run(
            program_id="prog_other",
            source=sample_workflow_data["source"],
        )

        results = await workflow_repo.list_workflow_runs(program_id=target_program)

        assert len(results) == 1
        assert results[0]["program_id"] == target_program

    async def test_list_workflow_runs_filter_by_status(
        self, workflow_repo: WorkflowRepository, sample_workflow_data: dict[str, Any]
    ):
        """Test filtering workflow runs by status."""
        created = await workflow_repo.create_workflow_run(
            program_id=sample_workflow_data["program_id"],
            source=sample_workflow_data["source"],
        )

        await workflow_repo.mark_workflow_completed(created["id"])

        results = await workflow_repo.list_workflow_runs(status="completed")

        assert len(results) >= 1
        assert all(r["status"] == "completed" for r in results)

    async def test_get_active_workflow_for_program(
        self, workflow_repo: WorkflowRepository, sample_workflow_data: dict[str, Any]
    ):
        """Test getting the active workflow for a program."""
        program_id = "prog_active_test"

        created = await workflow_repo.create_workflow_run(
            program_id=program_id,
            source=sample_workflow_data["source"],
        )

        active = await workflow_repo.get_active_workflow_for_program(program_id)

        assert active is not None
        assert active["id"] == created["id"]
        assert active["status"] == "running"

    async def test_get_active_workflow_returns_none_when_completed(
        self, workflow_repo: WorkflowRepository, sample_workflow_data: dict[str, Any]
    ):
        """Test that completed workflows are not returned as active."""
        program_id = "prog_completed_test"

        created = await workflow_repo.create_workflow_run(
            program_id=program_id,
            source=sample_workflow_data["source"],
        )
        await workflow_repo.mark_workflow_completed(created["id"])

        active = await workflow_repo.get_active_workflow_for_program(program_id)

        assert active is None


@pytest.mark.unit
class TestWorkflowRepositoryUpdate:
    """Tests for updating workflow runs."""

    async def test_update_workflow_status(
        self, workflow_repo: WorkflowRepository, sample_workflow_data: dict[str, Any]
    ):
        """Test updating workflow status."""
        created = await workflow_repo.create_workflow_run(
            program_id=sample_workflow_data["program_id"],
            source=sample_workflow_data["source"],
        )

        updated = await workflow_repo.update_workflow_status(created["id"], "completed")

        assert updated["status"] == "completed"

    async def test_update_workflow_status_and_stage(
        self, workflow_repo: WorkflowRepository, sample_workflow_data: dict[str, Any]
    ):
        """Test updating both status and current stage."""
        created = await workflow_repo.create_workflow_run(
            program_id=sample_workflow_data["program_id"],
            source=sample_workflow_data["source"],
        )

        updated = await workflow_repo.update_workflow_status(
            created["id"], "running", current_stage="enrichment"
        )

        assert updated["status"] == "running"
        assert updated["current_stage"] == "enrichment"

    async def test_mark_workflow_completed(
        self, workflow_repo: WorkflowRepository, sample_workflow_data: dict[str, Any]
    ):
        """Test marking a workflow as completed."""
        created = await workflow_repo.create_workflow_run(
            program_id=sample_workflow_data["program_id"],
            source=sample_workflow_data["source"],
        )

        completed = await workflow_repo.mark_workflow_completed(created["id"])

        assert completed["status"] == "completed"

    async def test_mark_workflow_failed_without_message(
        self, workflow_repo: WorkflowRepository, sample_workflow_data: dict[str, Any]
    ):
        """Test marking a workflow as failed without error message."""
        created = await workflow_repo.create_workflow_run(
            program_id=sample_workflow_data["program_id"],
            source=sample_workflow_data["source"],
        )

        failed = await workflow_repo.mark_workflow_failed(created["id"])

        assert failed["status"] == "failed"
        assert failed.get("error_message") is None

    async def test_mark_workflow_failed_with_message(
        self, workflow_repo: WorkflowRepository, sample_workflow_data: dict[str, Any]
    ):
        """Test marking a workflow as failed with error message."""
        created = await workflow_repo.create_workflow_run(
            program_id=sample_workflow_data["program_id"],
            source=sample_workflow_data["source"],
        )

        error_msg = "Database connection failed"
        failed = await workflow_repo.mark_workflow_failed(created["id"], error_msg)

        assert failed["status"] == "failed"
        assert failed["error_message"] == error_msg


@pytest.mark.unit
class TestWorkflowRepositoryAggregations:
    """Tests for aggregation operations."""

    async def test_count_workflows_by_status(
        self, workflow_repo: WorkflowRepository, sample_workflow_data: dict[str, Any]
    ):
        """Test counting workflows by status."""
        # Create workflows with different statuses
        created1 = await workflow_repo.create_workflow_run(
            program_id="prog_001",
            source=sample_workflow_data["source"],
        )
        await workflow_repo.create_workflow_run(
            program_id="prog_002",
            source=sample_workflow_data["source"],
        )

        await workflow_repo.mark_workflow_completed(created1["id"])

        running_count = await workflow_repo.count_workflows_by_status("running")
        completed_count = await workflow_repo.count_workflows_by_status("completed")

        assert running_count >= 1
        assert completed_count >= 1


@pytest.mark.unit
class TestWorkflowRepositoryEdgeCases:
    """Tests for edge cases and error conditions."""

    async def test_create_duplicate_program_id_fails(
        self, workflow_repo: WorkflowRepository, sample_workflow_data: dict[str, Any]
    ):
        """Test that creating duplicate program_id fails gracefully."""
        await workflow_repo.create_workflow_run(
            program_id=sample_workflow_data["program_id"],
            source=sample_workflow_data["source"],
        )

        # Attempting to create another with same program_id should fail
        from sqlalchemy.exc import IntegrityError

        with pytest.raises(IntegrityError):
            await workflow_repo.create_workflow_run(
                program_id=sample_workflow_data["program_id"],
                source=sample_workflow_data["source"],
            )

    async def test_update_nonexistent_workflow(self, workflow_repo: WorkflowRepository):
        """Test updating a non-existent workflow."""
        result = await workflow_repo.update_workflow_status(str(uuid.uuid4()), "completed")

        assert result is None
