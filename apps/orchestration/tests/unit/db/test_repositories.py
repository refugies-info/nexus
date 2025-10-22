"""Unit tests for repository layer with mocked Supabase client."""

from typing import Any

import pytest

from db.repositories.diff import DiffRepository
from db.repositories.information_sheet import InformationSheetRepository
from db.repositories.stage import StageRepository
from db.repositories.update import UpdateRepository
from db.repositories.workflow import WorkflowRepository


class MockSupabaseResponse:
    """Mock Supabase response object."""

    def __init__(self, data: list[dict[str, Any]] | None = None, count: int = 0):
        self.data = data or []
        self.count = count


class MockSupabaseQuery:
    """Mock Supabase query builder."""

    def __init__(self, table_name: str):
        self.table_name = table_name
        self._filters = {}
        self._limit_value = None
        self._range_start = None
        self._range_end = None

    def select(self, *args: str) -> "MockSupabaseQuery":
        """Mock select method."""
        return self

    def eq(self, field: str, value: Any) -> "MockSupabaseQuery":
        """Mock eq filter."""
        self._filters[field] = value
        return self

    def limit(self, limit: int) -> "MockSupabaseQuery":
        """Mock limit method."""
        self._limit_value = limit
        return self

    def range(self, start: int, end: int) -> "MockSupabaseQuery":
        """Mock range method."""
        self._range_start = start
        self._range_end = end
        return self

    def insert(self, data: dict[str, Any]) -> "MockSupabaseQuery":
        """Mock insert method."""
        self._insert_data = data
        return self

    def update(self, data: dict[str, Any]) -> "MockSupabaseQuery":
        """Mock update method."""
        self._update_data = data
        return self

    def delete(self) -> "MockSupabaseQuery":
        """Mock delete method."""
        return self

    def execute(self) -> MockSupabaseResponse:
        """Mock execute method."""
        # Return mock data based on operation
        if hasattr(self, "_insert_data"):
            return MockSupabaseResponse(data=[{**self._insert_data, "id": "test_id"}])
        elif hasattr(self, "_update_data"):
            return MockSupabaseResponse(data=[{**self._update_data, "id": "test_id"}])
        else:
            return MockSupabaseResponse(data=[{"id": "test_id", "status": "running"}])


class MockSupabaseClient:
    """Mock Supabase client."""

    def __init__(self):
        self.tables = {}

    def table(self, table_name: str) -> MockSupabaseQuery:
        """Mock table method."""
        return MockSupabaseQuery(table_name)


@pytest.fixture
def mock_supabase_client() -> MockSupabaseClient:
    """Create a mock Supabase client."""
    return MockSupabaseClient()


@pytest.fixture
def workflow_repo(mock_supabase_client: MockSupabaseClient) -> WorkflowRepository:
    """Create a WorkflowRepository with mocked client."""
    return WorkflowRepository(mock_supabase_client)


@pytest.fixture
def stage_repo(mock_supabase_client: MockSupabaseClient) -> StageRepository:
    """Create a StageRepository with mocked client."""
    return StageRepository(mock_supabase_client)


@pytest.fixture
def info_sheet_repo(mock_supabase_client: MockSupabaseClient) -> InformationSheetRepository:
    """Create an InformationSheetRepository with mocked client."""
    return InformationSheetRepository(mock_supabase_client)


@pytest.fixture
def update_repo(mock_supabase_client: MockSupabaseClient) -> UpdateRepository:
    """Create an UpdateRepository with mocked client."""
    return UpdateRepository(mock_supabase_client)


@pytest.fixture
def diff_repo(mock_supabase_client: MockSupabaseClient) -> DiffRepository:
    """Create a DiffRepository with mocked client."""
    return DiffRepository(mock_supabase_client)


@pytest.mark.unit
class TestWorkflowRepository:
    """Tests for WorkflowRepository."""

    @pytest.mark.asyncio
    async def test_create_workflow_run(self, workflow_repo: WorkflowRepository) -> None:
        """Test creating a workflow run."""
        result = await workflow_repo.create_workflow_run(
            program_id="prog_123",
            source="data_inclusion",
            initial_stage="ingestion",
        )

        assert result is not None
        assert result["id"] == "test_id"

    @pytest.mark.asyncio
    async def test_get_workflow_run(self, workflow_repo: WorkflowRepository) -> None:
        """Test retrieving a workflow run."""
        result = await workflow_repo.get_workflow_run("wf_123")

        assert result is not None
        assert result["id"] == "test_id"

    @pytest.mark.asyncio
    async def test_update_workflow_status(self, workflow_repo: WorkflowRepository) -> None:
        """Test updating workflow status."""
        result = await workflow_repo.update_workflow_status("wf_123", "completed", "publication")

        assert result is not None
        assert result["id"] == "test_id"

    @pytest.mark.asyncio
    async def test_mark_workflow_completed(self, workflow_repo: WorkflowRepository) -> None:
        """Test marking workflow as completed."""
        result = await workflow_repo.mark_workflow_completed("wf_123")

        assert result is not None
        assert result["id"] == "test_id"

    @pytest.mark.asyncio
    async def test_mark_workflow_failed(self, workflow_repo: WorkflowRepository) -> None:
        """Test marking workflow as failed."""
        result = await workflow_repo.mark_workflow_failed("wf_123", "Test error")

        assert result is not None
        assert result["id"] == "test_id"


@pytest.mark.unit
class TestStageRepository:
    """Tests for StageRepository."""

    @pytest.mark.asyncio
    async def test_create_stage_execution(self, stage_repo: StageRepository) -> None:
        """Test creating a stage execution."""
        result = await stage_repo.create_stage_execution(
            workflow_id="wf_123",
            stage_name="enrichment",
            program_id="prog_123",
        )

        assert result is not None
        assert result["id"] == "test_id"

    @pytest.mark.asyncio
    async def test_get_stage_execution(self, stage_repo: StageRepository) -> None:
        """Test retrieving a stage execution."""
        result = await stage_repo.get_stage_execution("stage_123")

        assert result is not None
        assert result["id"] == "test_id"

    @pytest.mark.asyncio
    async def test_mark_stage_completed(self, stage_repo: StageRepository) -> None:
        """Test marking stage as completed."""
        result = await stage_repo.mark_stage_completed("stage_123")

        assert result is not None
        assert result["id"] == "test_id"

    @pytest.mark.asyncio
    async def test_mark_stage_failed(self, stage_repo: StageRepository) -> None:
        """Test marking stage as failed."""
        result = await stage_repo.mark_stage_failed("stage_123", "Test error")

        assert result is not None
        assert result["id"] == "test_id"


@pytest.mark.unit
class TestInformationSheetRepository:
    """Tests for InformationSheetRepository."""

    @pytest.mark.asyncio
    async def test_create_information_sheet(
        self, info_sheet_repo: InformationSheetRepository
    ) -> None:
        """Test creating an information sheet."""
        result = await info_sheet_repo.create_information_sheet(
            program_id="prog_123",
            workflow_id="wf_123",
            source_data={"name": "Test Program"},
        )

        assert result is not None
        assert result["id"] == "test_id"

    @pytest.mark.asyncio
    async def test_get_information_sheet(self, info_sheet_repo: InformationSheetRepository) -> None:
        """Test retrieving an information sheet."""
        result = await info_sheet_repo.get_information_sheet("sheet_123")

        assert result is not None
        assert result["id"] == "test_id"

    @pytest.mark.asyncio
    async def test_mark_published(self, info_sheet_repo: InformationSheetRepository) -> None:
        """Test marking information sheet as published."""
        result = await info_sheet_repo.mark_published("sheet_123")

        assert result is not None
        assert result["id"] == "test_id"

    @pytest.mark.asyncio
    async def test_mark_rejected(self, info_sheet_repo: InformationSheetRepository) -> None:
        """Test marking information sheet as rejected."""
        result = await info_sheet_repo.mark_rejected("sheet_123", "Non-compliant")

        assert result is not None
        assert result["id"] == "test_id"


@pytest.mark.unit
class TestUpdateRepository:
    """Tests for UpdateRepository."""

    @pytest.mark.asyncio
    async def test_create_update_event(self, update_repo: UpdateRepository) -> None:
        """Test creating an update event."""
        result = await update_repo.create_update_event(
            program_id="prog_123",
            original_stage="enrichment",
            update_strategy="smart_catchup",
            source_data={"name": "Updated"},
            checksum="abc123",
        )

        assert result is not None
        assert result["id"] == "test_id"

    @pytest.mark.asyncio
    async def test_get_update_event(self, update_repo: UpdateRepository) -> None:
        """Test retrieving an update event."""
        result = await update_repo.get_update_event("upd_123")

        assert result is not None
        assert result["id"] == "test_id"

    @pytest.mark.asyncio
    async def test_mark_completed(self, update_repo: UpdateRepository) -> None:
        """Test marking update as completed."""
        result = await update_repo.mark_completed("upd_123")

        assert result is not None
        assert result["id"] == "test_id"

    @pytest.mark.asyncio
    async def test_mark_failed(self, update_repo: UpdateRepository) -> None:
        """Test marking update as failed."""
        result = await update_repo.mark_failed("upd_123", "Processing error")

        assert result is not None
        assert result["id"] == "test_id"


@pytest.mark.unit
class TestDiffRepository:
    """Tests for DiffRepository."""

    @pytest.mark.asyncio
    async def test_create_diff(self, diff_repo: DiffRepository) -> None:
        """Test creating a diff."""
        result = await diff_repo.create_diff(
            update_id="upd_123",
            program_id="prog_123",
            original_data={"name": "Original"},
            updated_data={"name": "Updated"},
            diff_content={"name": {"old": "Original", "new": "Updated"}},
            risk_score=0.3,
        )

        assert result is not None
        assert result["id"] == "test_id"

    @pytest.mark.asyncio
    async def test_get_diff(self, diff_repo: DiffRepository) -> None:
        """Test retrieving a diff."""
        result = await diff_repo.get_diff("diff_123")

        assert result is not None
        assert result["id"] == "test_id"

    @pytest.mark.asyncio
    async def test_mark_approved(self, diff_repo: DiffRepository) -> None:
        """Test marking diff as approved."""
        result = await diff_repo.mark_approved("diff_123", "user_123")

        assert result is not None
        assert result["id"] == "test_id"

    @pytest.mark.asyncio
    async def test_mark_rejected(self, diff_repo: DiffRepository) -> None:
        """Test marking diff as rejected."""
        result = await diff_repo.mark_rejected("diff_123", "user_123", "Invalid changes")

        assert result is not None
        assert result["id"] == "test_id"
