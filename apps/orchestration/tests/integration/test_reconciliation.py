"""Integration tests for Carif-Oref reconciliation."""

import pytest

from services.reconciliation import (
    create_reconciliation_status,
    detect_conflicts,
    fetch_carif_oref_csv,
    match_programs,
    merge_data,
    resolve_conflicts,
)


class TestCarifOrefReconciliationIntegration:
    """Integration tests for Carif-Oref reconciliation with CSV data."""

    @pytest.mark.asyncio
    async def test_reconciliation_end_to_end_with_match(self, mock_reconciliation_repo):
        """Test end-to-end reconciliation with matching Carif-Oref data."""
        # Simulate CSV data from Carif-Oref
        csv_data = [
            {
                "structure_id": "struct-001",
                "service_id": "svc-001",
                "name": "Carif-Oref Program",
                "description": "Carif-Oref Description",
                "address": "456 Oak Ave",
                "phone": "01234567890",
                "email": "carif@example.com",
                "updated_at": "2025-10-21",
            }
        ]

        program_data = {
            "id": "prog-001",
            "structure_id": "struct-001",
            "service_id": "svc-001",
            "name": "Data Inclusion Program",
            "description": "Data Inclusion Description",
            "address": "123 Main St",
            "phone": "09876543210",
            "email": "di@example.com",
            "updated_at": "2025-10-20",
        }

        # Step 1: Match programs
        matched = await match_programs(mock_reconciliation_repo, program_data, csv_data)
        assert matched is not None
        assert matched["structure_id"] == "struct-001"

        # Step 2: Detect conflicts
        conflicts = await detect_conflicts(program_data, matched)
        assert len(conflicts) > 0

        # Step 3: Merge data
        merged = await merge_data(program_data, matched)
        assert "carif_oref_name" in merged
        assert "carif_oref_phone" in merged

        # Step 4: Resolve conflicts
        resolved = await resolve_conflicts(program_data, matched, conflicts)
        assert resolved is not None

        # Step 5: Create reconciliation status
        status = await create_reconciliation_status(
            mock_reconciliation_repo,
            program_id="prog-001",
            status="fully_reconciled",
            carif_oref_data=matched,
            conflicts=conflicts,
        )
        assert status["program_id"] == "prog-001"
        assert status["status"] == "fully_reconciled"

    @pytest.mark.asyncio
    async def test_reconciliation_no_match_in_csv(self, mock_reconciliation_repo):
        """Test reconciliation when program not found in CSV."""
        csv_data = [
            {
                "structure_id": "struct-999",
                "service_id": "svc-999",
                "name": "Other Program",
            }
        ]

        program_data = {
            "id": "prog-001",
            "structure_id": "struct-001",
            "service_id": "svc-001",
            "name": "Test Program",
        }

        # Try to match
        matched = await match_programs(mock_reconciliation_repo, program_data, csv_data)
        assert matched is None

        # Create partial reconciliation status
        status = await create_reconciliation_status(
            mock_reconciliation_repo,
            program_id="prog-001",
            status="partially_reconciled",
            carif_oref_data=None,
        )
        assert status["status"] == "partially_reconciled"

    @pytest.mark.asyncio
    async def test_reconciliation_with_conflicts_detected(self, mock_reconciliation_repo):
        """Test reconciliation with multiple conflicts."""
        csv_data = [
            {
                "structure_id": "struct-001",
                "service_id": "svc-001",
                "name": "Carif Program A",
                "description": "Carif Description A",
                "address": "456 Oak Ave",
                "phone": "01111111111",
                "email": "carif@example.com",
                "updated_at": "2025-10-21",
            }
        ]

        program_data = {
            "id": "prog-001",
            "structure_id": "struct-001",
            "service_id": "svc-001",
            "name": "Data Program A",
            "description": "Data Description A",
            "address": "123 Main St",
            "phone": "02222222222",
            "email": "data@example.com",
            "updated_at": "2025-10-20",
        }

        # Match and detect conflicts
        matched = await match_programs(mock_reconciliation_repo, program_data, csv_data)
        conflicts = await detect_conflicts(program_data, matched)

        # Should have multiple conflicts
        assert len(conflicts) >= 3

        # Create conflict status
        status = await create_reconciliation_status(
            mock_reconciliation_repo,
            program_id="prog-001",
            status="data_conflict",
            carif_oref_data=matched,
            conflicts=conflicts,
        )
        assert status["status"] == "data_conflict"
        assert len(status["conflicts"]) >= 3

    @pytest.mark.asyncio
    async def test_reconciliation_carif_oref_precedence(self, mock_reconciliation_repo):
        """Test that Carif-Oref data takes precedence when more recent."""
        csv_data = [
            {
                "structure_id": "struct-001",
                "service_id": "svc-001",
                "name": "Updated Name",
                "description": "Updated Description",
                "address": "456 Oak Ave",
                "phone": "01234567890",
                "updated_at": "2025-10-21",
            }
        ]

        program_data = {
            "id": "prog-001",
            "structure_id": "struct-001",
            "service_id": "svc-001",
            "name": "Old Name",
            "description": "Old Description",
            "address": "123 Main St",
            "phone": "09876543210",
            "updated_at": "2025-10-20",
        }

        matched = await match_programs(mock_reconciliation_repo, program_data, csv_data)
        conflicts = await detect_conflicts(program_data, matched)
        resolved = await resolve_conflicts(program_data, matched, conflicts)

        # Carif-Oref is more recent, so its values should be used
        assert resolved["name"] == "Updated Name"
        assert resolved["description"] == "Updated Description"

    @pytest.mark.asyncio
    async def test_reconciliation_data_inclusion_completeness(self, mock_reconciliation_repo):
        """Test that Data Inclusion data is preferred when more complete."""
        csv_data = [
            {
                "structure_id": "struct-001",
                "service_id": "svc-001",
                "name": "Carif Program",
                "updated_at": "2025-10-21",
            }
        ]

        program_data = {
            "id": "prog-001",
            "structure_id": "struct-001",
            "service_id": "svc-001",
            "name": "Data Program",
            "description": "Complete description",
            "address": "123 Main St",
            "phone": "01234567890",
            "email": "test@example.com",
            "website": "https://example.com",
            "updated_at": "2025-10-21",
        }

        matched = await match_programs(mock_reconciliation_repo, program_data, csv_data)
        conflicts = await detect_conflicts(program_data, matched)
        resolved = await resolve_conflicts(program_data, matched, conflicts)

        # Data Inclusion is more complete, so keep its name
        assert resolved["name"] == "Data Program"

    @pytest.mark.asyncio
    async def test_reconciliation_with_empty_csv(self, mock_reconciliation_repo):
        """Test reconciliation with empty CSV data."""
        program_data = {
            "id": "prog-001",
            "structure_id": "struct-001",
            "service_id": "svc-001",
            "name": "Test Program",
        }

        # Fetch empty CSV
        csv_data = await fetch_carif_oref_csv(mock_reconciliation_repo)
        assert csv_data == []

        # Try to match with empty CSV
        matched = await match_programs(mock_reconciliation_repo, program_data, csv_data)
        assert matched is None

    @pytest.mark.asyncio
    async def test_reconciliation_preserves_custom_fields(self, mock_reconciliation_repo):
        """Test that custom fields are preserved during reconciliation."""
        csv_data = [
            {
                "structure_id": "struct-001",
                "service_id": "svc-001",
                "name": "Carif Program",
                "phone": "01234567890",
            }
        ]

        program_data = {
            "id": "prog-001",
            "structure_id": "struct-001",
            "service_id": "svc-001",
            "name": "Data Program",
            "custom_field_1": "custom_value_1",
            "custom_field_2": "custom_value_2",
            "internal_notes": "Important notes",
        }

        matched = await match_programs(mock_reconciliation_repo, program_data, csv_data)
        merged = await merge_data(program_data, matched)

        # Custom fields should be preserved
        assert merged["custom_field_1"] == "custom_value_1"
        assert merged["custom_field_2"] == "custom_value_2"
        assert merged["internal_notes"] == "Important notes"


class TestCarifOrefReconciliationRealWorldScenarios:
    """Test reconciliation with real-world program scenarios."""

    @pytest.mark.asyncio
    async def test_reconciliation_language_course_program(self, mock_reconciliation_repo):
        """Test reconciliation of language course program."""
        csv_data = [
            {
                "structure_id": "struct-lang-001",
                "service_id": "svc-lang-001",
                "department": "75",
                "name": "French Language Course",
                "description": "Intensive French for refugees",
                "address": "10 Rue de Paris, 75001 Paris",
                "phone": "01 23 45 67 89",
                "email": "contact@language.org",
                "website": "https://language.org",
                "updated_at": "2025-10-21",
            }
        ]

        program_data = {
            "id": "prog-lang-001",
            "structure_id": "struct-lang-001",
            "service_id": "svc-lang-001",
            "name": "French Language Course",
            "description": "Learn French",
            "address": "10 Rue de Paris, 75001 Paris",
            "updated_at": "2025-10-20",
        }

        matched = await match_programs(mock_reconciliation_repo, program_data, csv_data)
        assert matched is not None

        merged = await merge_data(program_data, matched)
        assert "carif_oref_phone" in merged
        assert "carif_oref_email" in merged
        assert "carif_oref_website" in merged

    @pytest.mark.asyncio
    async def test_reconciliation_job_training_program(self, mock_reconciliation_repo):
        """Test reconciliation of job training program."""
        csv_data = [
            {
                "structure_id": "struct-job-001",
                "service_id": "svc-job-001",
                "department": "92",
                "name": "Professional Skills Training",
                "description": "Vocational training for employment",
                "address": "50 Avenue de la République, 92100 Boulogne",
                "phone": "01 98 76 54 32",
                "email": "training@job.org",
                "updated_at": "2025-10-21",
            }
        ]

        program_data = {
            "id": "prog-job-001",
            "structure_id": "struct-job-001",
            "service_id": "svc-job-001",
            "name": "Professional Skills Training",
            "description": "Job training",
            "address": "50 Avenue de la République, 92100 Boulogne",
            "updated_at": "2025-10-20",
        }

        matched = await match_programs(mock_reconciliation_repo, program_data, csv_data)
        conflicts = await detect_conflicts(program_data, matched)

        # Should have minimal conflicts for similar programs
        assert len(conflicts) <= 1

    @pytest.mark.asyncio
    async def test_reconciliation_integration_program(self, mock_reconciliation_repo):
        """Test reconciliation of integration program."""
        csv_data = [
            {
                "structure_id": "struct-int-001",
                "service_id": "svc-int-001",
                "department": "13",
                "name": "Integration Support Program",
                "description": "Comprehensive integration services",
                "address": "100 Rue de Marseille, 13000 Marseille",
                "phone": "04 91 12 34 56",
                "email": "integration@support.org",
                "website": "https://integration.org",
                "updated_at": "2025-10-21",
            }
        ]

        program_data = {
            "id": "prog-int-001",
            "structure_id": "struct-int-001",
            "service_id": "svc-int-001",
            "name": "Integration Support Program",
            "description": "Integration services",
            "address": "100 Rue de Marseille, 13000 Marseille",
            "updated_at": "2025-10-21",
        }

        matched = await match_programs(mock_reconciliation_repo, program_data, csv_data)
        conflicts = await detect_conflicts(program_data, matched)
        resolved = await resolve_conflicts(program_data, matched, conflicts)

        # Same timestamp, Data Inclusion is equally complete
        assert resolved is not None
