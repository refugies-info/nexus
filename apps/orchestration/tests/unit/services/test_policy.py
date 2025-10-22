"""Unit tests for policy validation service."""

import pytest

from services.policy import (
    check_applicable_rules,
    generate_audit_trail,
    reject_program,
    validate_program,
)


class TestValidateProgram:
    """Test validate_program function."""

    @pytest.mark.asyncio
    async def test_validate_program_compliant(self):
        """Test validation of compliant program."""
        program_data = {
            "id": "prog-001",
            "name": "French Learning Program",
            "is_for_profit": False,
            "is_temporary": False,
            "target_publics": ["adults"],
        }
        policy_rules = [
            {
                "id": "rule-1",
                "category": "for_profit",
                "criteria": {},
            }
        ]

        result = await validate_program(
            program_id="prog-001",
            program_data=program_data,
            policy_rules=policy_rules,
        )

        assert result["is_compliant"] is True
        assert len(result["violations"]) == 0

    @pytest.mark.asyncio
    async def test_validate_program_non_compliant(self):
        """Test validation of non-compliant program."""
        program_data = {
            "id": "prog-002",
            "name": "Commercial Program",
            "is_for_profit": True,
            "is_temporary": False,
        }
        policy_rules = [
            {
                "id": "rule-1",
                "category": "for_profit",
                "criteria": {},
            }
        ]

        result = await validate_program(
            program_id="prog-002",
            program_data=program_data,
            policy_rules=policy_rules,
        )

        assert result["is_compliant"] is False
        assert len(result["violations"]) > 0

    @pytest.mark.asyncio
    async def test_validate_program_temporary_initiative(self):
        """Test validation rejects temporary initiatives."""
        program_data = {
            "id": "prog-003",
            "name": "One-Time Workshop",
            "is_temporary": True,
        }
        policy_rules = [
            {
                "id": "rule-2",
                "category": "temporary",
                "criteria": {},
            }
        ]

        result = await validate_program(
            program_id="prog-003",
            program_data=program_data,
            policy_rules=policy_rules,
        )

        assert result["is_compliant"] is False

    @pytest.mark.asyncio
    async def test_validate_program_with_audit_trail(self):
        """Test validation includes audit trail."""
        program_data = {
            "id": "prog-004",
            "name": "Test Program",
        }
        policy_rules = [
            {
                "id": "rule-1",
                "category": "for_profit",
                "criteria": {},
            }
        ]

        result = await validate_program(
            program_id="prog-004",
            program_data=program_data,
            policy_rules=policy_rules,
        )

        assert "audit_trail" in result
        assert isinstance(result["audit_trail"], list)

    @pytest.mark.asyncio
    async def test_validate_program_empty_rules(self):
        """Test validation with no policy rules."""
        program_data = {
            "id": "prog-005",
            "name": "Test Program",
        }

        result = await validate_program(
            program_id="prog-005",
            program_data=program_data,
            policy_rules=[],
        )

        assert result["is_compliant"] is True


class TestCheckApplicableRules:
    """Test check_applicable_rules function."""

    @pytest.mark.asyncio
    async def test_check_applicable_rules_all_applicable(self):
        """Test when all policy rules are applicable."""
        program_data = {
            "is_for_profit": False,
            "is_temporary": False,
            "target_publics": ["adults"],
        }
        policy_rules = [
            {
                "id": "rule-1",
                "category": "for_profit",
                "criteria": {},
            },
            {
                "id": "rule-2",
                "category": "temporary",
                "criteria": {},
            },
        ]

        applicable = await check_applicable_rules(
            program_data=program_data,
            policy_rules=policy_rules,
        )

        assert len(applicable) == 2

    @pytest.mark.asyncio
    async def test_check_applicable_rules_filters_correctly(self):
        """Test that applicable rules are filtered correctly."""
        program_data = {
            "is_for_profit": True,
            "is_temporary": True,
        }
        policy_rules = [
            {
                "id": "rule-1",
                "category": "for_profit",
                "criteria": {},
            },
            {
                "id": "rule-2",
                "category": "temporary",
                "criteria": {},
            },
        ]

        applicable = await check_applicable_rules(
            program_data=program_data,
            policy_rules=policy_rules,
        )

        assert len(applicable) > 0

    @pytest.mark.asyncio
    async def test_check_applicable_rules_with_exceptions(self):
        """Test policy rules with exceptions."""
        program_data = {
            "is_for_profit": True,
            "is_subsidized": True,
        }
        policy_rules = [
            {
                "id": "rule-1",
                "category": "for_profit",
                "criteria": {"exceptions": ["subsidized"]},
            }
        ]

        applicable = await check_applicable_rules(
            program_data=program_data,
            policy_rules=policy_rules,
        )

        # Should still be applicable, but validation will check exceptions
        assert len(applicable) > 0


class TestGenerateAuditTrail:
    """Test generate_audit_trail function."""

    def test_generate_audit_trail_approved(self):
        """Test audit trail for approved program."""
        program_id = "prog-001"
        validation_result = {
            "program_id": program_id,
            "is_compliant": True,
            "violations": [],
            "audit_trail": [],
        }

        trail = generate_audit_trail(
            program_id=program_id,
            validation_result=validation_result,
        )

        assert isinstance(trail, dict)
        assert trail["program_id"] == program_id
        assert trail["is_compliant"] is True

    def test_generate_audit_trail_rejected(self):
        """Test audit trail for rejected program."""
        program_id = "prog-002"
        violations = [
            {
                "rule_id": "rule-1",
                "category": "for_profit",
                "reason": "Program is for-profit",
            }
        ]
        validation_result = {
            "program_id": program_id,
            "is_compliant": False,
            "violations": violations,
            "audit_trail": [],
        }

        trail = generate_audit_trail(
            program_id=program_id,
            validation_result=validation_result,
        )

        assert isinstance(trail, dict)
        assert trail["program_id"] == program_id
        assert trail["is_compliant"] is False

    def test_generate_audit_trail_includes_timestamp(self):
        """Test audit trail includes timestamp."""
        program_id = "prog-003"
        validation_result = {
            "program_id": program_id,
            "is_compliant": True,
            "violations": [],
            "audit_trail": [],
        }

        trail = generate_audit_trail(
            program_id=program_id,
            validation_result=validation_result,
        )

        assert "validation_timestamp" in trail

    def test_generate_audit_trail_includes_violations(self):
        """Test audit trail includes violation details."""
        program_id = "prog-004"
        violations = [
            {
                "rule_id": "rule-1",
                "category": "temporary",
                "reason": "Program is temporary",
            },
            {
                "rule_id": "rule-2",
                "category": "for_profit",
                "reason": "Program is for-profit",
            },
        ]
        validation_result = {
            "program_id": program_id,
            "is_compliant": False,
            "violations": violations,
            "audit_trail": [],
        }

        trail = generate_audit_trail(
            program_id=program_id,
            validation_result=validation_result,
        )

        assert len(trail["violations"]) == 2


class TestRejectProgram:
    """Test reject_program function."""

    @pytest.mark.asyncio
    async def test_reject_program_basic(self, mock_policy_repo):
        """Test basic program rejection."""
        program_id = "prog-001"
        reason = "Program does not meet policy requirements"
        violations = []

        result = await reject_program(
            program_id=program_id,
            reason=reason,
            violations=violations,
            repo=mock_policy_repo,
        )

        assert result["program_id"] == program_id
        assert result["status"] == "rejected"
        assert result["reason"] == reason

    @pytest.mark.asyncio
    async def test_reject_program_with_violations(self, mock_policy_repo):
        """Test rejection with violation details."""
        program_id = "prog-002"
        reason = "Multiple policy violations"
        violations = [
            {"rule_id": "rule-1", "category": "for_profit"},
            {"rule_id": "rule-2", "category": "temporary"},
        ]

        result = await reject_program(
            program_id=program_id,
            reason=reason,
            violations=violations,
            repo=mock_policy_repo,
        )

        assert result["program_id"] == program_id
        assert "violations" in result
        assert len(result["violations"]) == 2

    @pytest.mark.asyncio
    async def test_reject_program_includes_timestamp(self, mock_policy_repo):
        """Test rejection includes timestamp."""
        program_id = "prog-003"
        reason = "Policy violation"
        violations = []

        result = await reject_program(
            program_id=program_id,
            reason=reason,
            violations=violations,
            repo=mock_policy_repo,
        )

        assert "rejected_at" in result


class TestPolicyEdgeCases:
    """Test edge cases in policy validation."""

    @pytest.mark.asyncio
    async def test_validate_program_missing_fields(self):
        """Test validation with missing program fields."""
        program_data = {
            "id": "prog-001",
            "name": "Test Program",
        }
        policy_rules = [
            {
                "id": "rule-1",
                "category": "for_profit",
                "criteria": {},
            }
        ]

        result = await validate_program(
            program_id="prog-001",
            program_data=program_data,
            policy_rules=policy_rules,
        )

        # Should handle missing fields gracefully
        assert "is_compliant" in result
        assert "violations" in result

    @pytest.mark.asyncio
    async def test_validate_program_null_values(self):
        """Test validation with null values in program data."""
        program_data = {
            "id": "prog-002",
            "name": "Test Program",
            "is_for_profit": None,
            "is_temporary": None,
        }
        policy_rules = [
            {
                "id": "rule-1",
                "category": "for_profit",
                "criteria": {},
            }
        ]

        result = await validate_program(
            program_id="prog-002",
            program_data=program_data,
            policy_rules=policy_rules,
        )

        assert "is_compliant" in result

    @pytest.mark.asyncio
    async def test_validate_program_specialized_structure(self):
        """Test validation with specialized structure."""
        program_data = {
            "id": "prog-003",
            "name": "Test Program",
            "structure_type": "france_services",
            "target_publics": ["adults", "seniors"],
            "location": "Paris",
        }
        policy_rules = [
            {
                "id": "rule-1",
                "category": "specialized_structure",
                "criteria": {"specialized_structures": ["france_services"]},
            }
        ]

        result = await validate_program(
            program_id="prog-003",
            program_data=program_data,
            policy_rules=policy_rules,
        )

        assert result["is_compliant"] is False
