"""Unit tests for reconciliation service."""

import pytest

from services.reconciliation import (
    create_reconciliation_status,
    detect_conflicts,
    fetch_carif_oref_csv,
    match_programs,
    merge_data,
    resolve_conflicts,
)


class TestFetchCarifOrefCsv:
    """Test fetch_carif_oref_csv function."""

    @pytest.mark.asyncio
    async def test_fetch_carif_oref_csv_success(self, mock_reconciliation_repo):
        """Test successful CSV fetch."""
        result = await fetch_carif_oref_csv(mock_reconciliation_repo)

        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_fetch_carif_oref_csv_empty(self, mock_reconciliation_repo):
        """Test CSV fetch returns empty list when no data."""
        result = await fetch_carif_oref_csv(mock_reconciliation_repo)

        assert result == []

    @pytest.mark.asyncio
    async def test_fetch_carif_oref_csv_with_data(self):
        """Test CSV fetch with sample data."""
        # Create mock repository with CSV data
        csv_data = [
            {
                "structure_id": "struct-001",
                "service_id": "svc-001",
                "name": "Service 1",
            }
        ]
        from tests.conftest import MockReconciliationRepository

        mock_repo = MockReconciliationRepository(csv_data=csv_data)

        result = await fetch_carif_oref_csv(mock_repo)

        assert isinstance(result, list)
        assert len(result) == 1


class TestMatchPrograms:
    """Test match_programs function."""

    @pytest.mark.asyncio
    async def test_match_programs_success(self, mock_reconciliation_repo):
        """Test successful program matching."""
        program_data = {
            "id": "prog-001",
            "structure_id": "struct-001",
            "service_id": "svc-001",
            "name": "Test Program",
        }
        csv_data = [
            {
                "structure_id": "struct-001",
                "service_id": "svc-001",
                "name": "Carif-Oref Program",
            }
        ]

        result = await match_programs(mock_reconciliation_repo, program_data, csv_data)

        assert result is not None
        assert result["structure_id"] == "struct-001"

    @pytest.mark.asyncio
    async def test_match_programs_no_match(self, mock_reconciliation_repo):
        """Test when no matching program found."""
        program_data = {
            "id": "prog-001",
            "structure_id": "struct-001",
            "service_id": "svc-001",
        }
        csv_data = [
            {
                "structure_id": "struct-999",
                "service_id": "svc-999",
            }
        ]

        result = await match_programs(mock_reconciliation_repo, program_data, csv_data)

        assert result is None

    @pytest.mark.asyncio
    async def test_match_programs_missing_ids(self, mock_reconciliation_repo):
        """Test matching with missing structure/service IDs."""
        program_data = {
            "id": "prog-001",
            "name": "Test Program",
        }
        csv_data = [
            {
                "structure_id": "struct-001",
                "service_id": "svc-001",
            }
        ]

        result = await match_programs(mock_reconciliation_repo, program_data, csv_data)

        assert result is None

    @pytest.mark.asyncio
    async def test_match_programs_empty_csv(self, mock_reconciliation_repo):
        """Test matching with empty CSV data."""
        program_data = {
            "id": "prog-001",
            "structure_id": "struct-001",
            "service_id": "svc-001",
        }

        result = await match_programs(mock_reconciliation_repo, program_data, [])

        assert result is None


class TestMergeData:
    """Test merge_data function."""

    @pytest.mark.asyncio
    async def test_merge_data_no_carif_oref(self):
        """Test merge when no Carif-Oref data available."""
        program_data = {
            "id": "prog-001",
            "name": "Test Program",
            "description": "Test Description",
        }

        result = await merge_data(program_data, None)

        assert result == program_data

    @pytest.mark.asyncio
    async def test_merge_data_with_carif_oref(self):
        """Test merge with Carif-Oref data."""
        program_data = {
            "id": "prog-001",
            "name": "Data Inclusion Name",
            "description": "Data Inclusion Description",
            "address": "123 Main St",
        }
        carif_oref_data = {
            "name": "Carif-Oref Name",
            "phone": "01234567890",
            "email": "test@example.com",
            "updated_at": "2025-10-21",
        }

        result = await merge_data(program_data, carif_oref_data)

        assert result["id"] == "prog-001"
        assert "carif_oref_name" in result
        assert result["carif_oref_name"] == "Carif-Oref Name"
        assert "carif_oref_phone" in result
        assert "carif_oref_email" in result

    @pytest.mark.asyncio
    async def test_merge_data_includes_url(self):
        """Test merge includes Carif-Oref URL."""
        program_data = {
            "id": "prog-001",
            "name": "Test Program",
        }
        carif_oref_data = {
            "department": "75",
            "structure_id": "struct-001",
            "service_id": "svc-001",
            "name": "Test Service",
        }

        result = await merge_data(program_data, carif_oref_data)

        assert "carif_oref_url" in result
        assert "intercariforef.org" in result["carif_oref_url"]

    @pytest.mark.asyncio
    async def test_merge_data_preserves_original(self):
        """Test merge preserves original program data."""
        program_data = {
            "id": "prog-001",
            "name": "Original Name",
            "custom_field": "custom_value",
        }
        carif_oref_data = {
            "name": "Carif Name",
        }

        result = await merge_data(program_data, carif_oref_data)

        assert result["name"] == "Original Name"
        assert result["custom_field"] == "custom_value"


class TestDetectConflicts:
    """Test detect_conflicts function."""

    @pytest.mark.asyncio
    async def test_detect_conflicts_no_carif_oref(self):
        """Test conflict detection with no Carif-Oref data."""
        program_data = {
            "id": "prog-001",
            "name": "Test Program",
        }

        result = await detect_conflicts(program_data, None)

        assert result == []

    @pytest.mark.asyncio
    async def test_detect_conflicts_no_conflicts(self):
        """Test when no conflicts exist."""
        program_data = {
            "id": "prog-001",
            "name": "Test Program",
            "address": "123 Main St",
        }
        carif_oref_data = {
            "name": "Test Program",
            "address": "123 Main St",
        }

        result = await detect_conflicts(program_data, carif_oref_data)

        assert result == []

    @pytest.mark.asyncio
    async def test_detect_conflicts_single_conflict(self):
        """Test detection of single conflict."""
        program_data = {
            "id": "prog-001",
            "name": "Program Name A",
            "address": "123 Main St",
        }
        carif_oref_data = {
            "name": "Program Name B",
            "address": "123 Main St",
        }

        result = await detect_conflicts(program_data, carif_oref_data)

        assert len(result) == 1
        assert result[0]["field"] == "name"
        assert result[0]["data_inclusion_value"] == "Program Name A"
        assert result[0]["carif_oref_value"] == "Program Name B"

    @pytest.mark.asyncio
    async def test_detect_conflicts_multiple(self):
        """Test detection of multiple conflicts."""
        program_data = {
            "id": "prog-001",
            "name": "Name A",
            "description": "Desc A",
            "address": "Address A",
            "phone": "111",
        }
        carif_oref_data = {
            "name": "Name B",
            "description": "Desc B",
            "address": "Address B",
            "phone": "222",
        }

        result = await detect_conflicts(program_data, carif_oref_data)

        assert len(result) == 4
        field_names = [c["field"] for c in result]
        assert "name" in field_names
        assert "description" in field_names

    @pytest.mark.asyncio
    async def test_detect_conflicts_severity_levels(self):
        """Test conflict severity calculation."""
        program_data = {
            "id": "prog-001",
            "name": "Name A",
            "address": "Address A",
            "phone": "111",
        }
        carif_oref_data = {
            "name": "Name B",
            "address": "Address B",
            "phone": "222",
        }

        result = await detect_conflicts(program_data, carif_oref_data)

        # Find each conflict and check severity
        name_conflict = next(c for c in result if c["field"] == "name")
        assert name_conflict["severity"] == "critical"

        address_conflict = next(c for c in result if c["field"] == "address")
        assert address_conflict["severity"] == "high"

    @pytest.mark.asyncio
    async def test_detect_conflicts_ignores_empty_values(self):
        """Test that empty values don't create conflicts."""
        program_data = {
            "id": "prog-001",
            "name": "Test Program",
            "phone": "",
        }
        carif_oref_data = {
            "name": "Test Program",
            "phone": "01234567890",
        }

        result = await detect_conflicts(program_data, carif_oref_data)

        assert result == []

    @pytest.mark.asyncio
    async def test_detect_conflicts_case_insensitive(self):
        """Test conflict detection is case-insensitive."""
        program_data = {
            "id": "prog-001",
            "name": "TEST PROGRAM",
        }
        carif_oref_data = {
            "name": "test program",
        }

        result = await detect_conflicts(program_data, carif_oref_data)

        assert result == []


class TestResolveConflicts:
    """Test resolve_conflicts function."""

    @pytest.mark.asyncio
    async def test_resolve_conflicts_no_conflicts(self):
        """Test resolution with no conflicts."""
        program_data = {
            "id": "prog-001",
            "name": "Test Program",
        }
        carif_oref_data = {
            "name": "Test Program",
        }

        result = await resolve_conflicts(program_data, carif_oref_data, [])

        assert result == program_data

    @pytest.mark.asyncio
    async def test_resolve_conflicts_no_carif_oref(self):
        """Test resolution with no Carif-Oref data."""
        program_data = {
            "id": "prog-001",
            "name": "Test Program",
        }
        conflicts = [
            {
                "field": "name",
                "data_inclusion_value": "Name A",
                "carif_oref_value": "Name B",
            }
        ]

        result = await resolve_conflicts(program_data, None, conflicts)

        assert result == program_data

    @pytest.mark.asyncio
    async def test_resolve_conflicts_prefer_recent_carif_oref(self):
        """Test conflict resolution prefers more recent Carif-Oref data."""
        program_data = {
            "id": "prog-001",
            "name": "Name A",
            "updated_at": "2025-10-20",
        }
        carif_oref_data = {
            "name": "Name B",
            "updated_at": "2025-10-21",
        }
        conflicts = [
            {
                "field": "name",
                "data_inclusion_value": "Name A",
                "carif_oref_value": "Name B",
            }
        ]

        result = await resolve_conflicts(program_data, carif_oref_data, conflicts)

        assert result["name"] == "Name B"

    @pytest.mark.asyncio
    async def test_resolve_conflicts_prefer_complete_data_inclusion(self):
        """Test conflict resolution prefers more complete Data Inclusion data."""
        program_data = {
            "id": "prog-001",
            "name": "Name A",
            "description": "Complete description",
            "address": "123 Main St",
            "phone": "01234567890",
            "email": "test@example.com",
            "website": "https://example.com",
            "updated_at": "2025-10-21",
        }
        carif_oref_data = {
            "name": "Name B",
            "updated_at": "2025-10-20",
        }
        conflicts = [
            {
                "field": "name",
                "data_inclusion_value": "Name A",
                "carif_oref_value": "Name B",
            }
        ]

        result = await resolve_conflicts(program_data, carif_oref_data, conflicts)

        # Data Inclusion is more complete, so keep its value
        assert result["name"] == "Name A"

    @pytest.mark.asyncio
    async def test_resolve_conflicts_default_to_carif_oref(self):
        """Test conflict resolution defaults to Carif-Oref."""
        program_data = {
            "id": "prog-001",
            "name": "Name A",
            "updated_at": "2025-10-21",
        }
        carif_oref_data = {
            "name": "Name B",
            "updated_at": "2025-10-21",
        }
        conflicts = [
            {
                "field": "name",
                "data_inclusion_value": "Name A",
                "carif_oref_value": "Name B",
            }
        ]

        result = await resolve_conflicts(program_data, carif_oref_data, conflicts)

        # Same recency, same completeness -> default to Carif-Oref
        assert result["name"] == "Name B"

    @pytest.mark.asyncio
    async def test_resolve_conflicts_multiple(self):
        """Test resolution of multiple conflicts."""
        program_data = {
            "id": "prog-001",
            "name": "Name A",
            "description": "Desc A",
            "address": "Address A",
            "updated_at": "2025-10-20",
        }
        carif_oref_data = {
            "name": "Name B",
            "description": "Desc B",
            "address": "Address B",
            "updated_at": "2025-10-21",
        }
        conflicts = [
            {
                "field": "name",
                "data_inclusion_value": "Name A",
                "carif_oref_value": "Name B",
            },
            {
                "field": "description",
                "data_inclusion_value": "Desc A",
                "carif_oref_value": "Desc B",
            },
            {
                "field": "address",
                "data_inclusion_value": "Address A",
                "carif_oref_value": "Address B",
            },
        ]

        result = await resolve_conflicts(program_data, carif_oref_data, conflicts)

        # Carif-Oref is more recent, so all should be updated
        assert result["name"] == "Name B"
        assert result["description"] == "Desc B"
        assert result["address"] == "Address B"


class TestCreateReconciliationStatus:
    """Test create_reconciliation_status function."""

    @pytest.mark.asyncio
    async def test_create_reconciliation_status_fully_reconciled(self, mock_reconciliation_repo):
        """Test creating fully reconciled status."""
        result = await create_reconciliation_status(
            mock_reconciliation_repo,
            program_id="prog-001",
            status="fully_reconciled",
        )

        assert result is not None
        assert result["program_id"] == "prog-001"
        assert result["status"] == "fully_reconciled"

    @pytest.mark.asyncio
    async def test_create_reconciliation_status_with_conflicts(self, mock_reconciliation_repo):
        """Test creating status with conflicts."""
        conflicts = [
            {
                "field": "name",
                "data_inclusion_value": "Name A",
                "carif_oref_value": "Name B",
            }
        ]

        result = await create_reconciliation_status(
            mock_reconciliation_repo,
            program_id="prog-001",
            status="data_conflict",
            conflicts=conflicts,
        )

        assert result is not None
        assert result["status"] == "data_conflict"

    @pytest.mark.asyncio
    async def test_create_reconciliation_status_partially_reconciled(
        self, mock_reconciliation_repo
    ):
        """Test creating partially reconciled status."""
        result = await create_reconciliation_status(
            mock_reconciliation_repo,
            program_id="prog-001",
            status="partially_reconciled",
        )

        assert result is not None
        assert result["status"] == "partially_reconciled"

    @pytest.mark.asyncio
    async def test_create_reconciliation_status_failed(self, mock_reconciliation_repo):
        """Test creating failed reconciliation status."""
        result = await create_reconciliation_status(
            mock_reconciliation_repo,
            program_id="prog-001",
            status="reconciliation_failed",
        )

        assert result is not None
        assert result["status"] == "reconciliation_failed"


class TestReconciliationEdgeCases:
    """Test edge cases in reconciliation."""

    @pytest.mark.asyncio
    async def test_merge_data_with_special_characters(self):
        """Test merge with special characters in data."""
        program_data = {
            "id": "prog-001",
            "name": "Café & Restaurant",
        }
        carif_oref_data = {
            "name": "Café & Restaurant",
            "description": "Spécial édition",
        }

        result = await merge_data(program_data, carif_oref_data)

        assert result["id"] == "prog-001"
        assert "carif_oref_description" in result

    @pytest.mark.asyncio
    async def test_detect_conflicts_with_whitespace(self):
        """Test conflict detection handles whitespace."""
        program_data = {
            "id": "prog-001",
            "name": "  Test Program  ",
        }
        carif_oref_data = {
            "name": "Test Program",
        }

        result = await detect_conflicts(program_data, carif_oref_data)

        # Should not create conflict due to whitespace normalization
        assert result == []

    @pytest.mark.asyncio
    async def test_merge_data_with_null_values(self):
        """Test merge with null values."""
        program_data = {
            "id": "prog-001",
            "name": "Test Program",
            "phone": None,
        }
        carif_oref_data = {
            "phone": "01234567890",
        }

        result = await merge_data(program_data, carif_oref_data)

        assert "carif_oref_phone" in result
        assert result["carif_oref_phone"] == "01234567890"

    @pytest.mark.asyncio
    async def test_merge_data_empty_carif_oref_fields(self):
        """Test merge ignores empty Carif-Oref fields."""
        program_data = {
            "id": "prog-001",
            "name": "Test Program",
        }
        carif_oref_data = {
            "name": "",
            "description": None,
            "phone": "01234567890",
        }

        result = await merge_data(program_data, carif_oref_data)

        assert "carif_oref_name" not in result
        assert "carif_oref_description" not in result
        assert "carif_oref_phone" in result
        assert result["carif_oref_phone"] == "01234567890"
