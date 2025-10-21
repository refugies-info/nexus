"""Unit tests for policy validation service."""

import pytest

from services.policy import (
    check_policy_rules,
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
            "type": "non-profit",
            "is_temporary": False,
            "target_audience": ["adults"],
        }
        policy_rules = [
            {
                "id": "rule-1",
                "category": "for_profit",
                "criteria": {"type": "non-profit"},
                "decision": "approved",
            }
        ]

        result = await validate_program(
            program_id="prog-001",
            program_data=program_data,
            policy_rules=policy_rules,
        )

        assert result["valid"] is True
        assert result["decision"] == "approved"

    @pytest.mark.asyncio
    async def test_validate_program_non_compliant(self):
        """Test validation of non-compliant program."""
        program_data = {
            "id": "prog-002",
            "name": "Commercial Program",
            "type": "for-profit",
            "is_temporary": False,
        }
        policy_rules = [
            {
                "id": "rule-1",
                "category": "for_profit",
                "criteria": {"type": "non-profit"},
                "decision": "approved",
            }
        ]

        result = await validate_program(
            program_id="prog-002",
            program_data=program_data,
            policy_rules=policy_rules,
        )

        assert result["valid"] is False
        assert result["decision"] == "rejected"

    @pytest.mark.asyncio
    async def test_validate_program_temporary_initiative(self):
        """Test validation rejects temporary initiatives."""
        program_data = {
            "id": "prog-003",
            "name": "One-Time Workshop",
            "type": "non-profit",
            "is_temporary": True,
        }
        policy_rules = [
            {
                "id": "rule-2",
                "category": "temporary_initiative",
                "criteria": {"is_temporary": False},
                "decision": "approved",
            }
        ]

        result = await validate_program(
            program_id="prog-003",
            program_data=program_data,
            policy_rules=policy_rules,
        )

        assert result["valid"] is False

    @pytest.mark.asyncio
    async def test_validate_program_with_audit_trail(self):
        """Test validation includes audit trail."""
        program_data = {
            "id": "prog-004",
            "name": "Test Program",
            "type": "non-profit",
        }
        policy_rules = [
            {
                "id": "rule-1",
                "category": "for_profit",
                "criteria": {"type": "non-profit"},
                "decision": "approved",
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

        assert result["valid"] is True


class TestCheckPolicyRules:
    """Test check_policy_rules function."""

    @pytest.mark.asyncio
    async def test_check_policy_rules_all_pass(self):
        """Test when all policy rules pass."""
        program_data = {
            "type": "non-profit",
            "is_temporary": False,
            "target_audience": ["adults"],
        }
        policy_rules = [
            {
                "id": "rule-1",
                "category": "for_profit",
                "criteria": {"type": "non-profit"},
                "decision": "approved",
            },
            {
                "id": "rule-2",
                "category": "temporary",
                "criteria": {"is_temporary": False},
                "decision": "approved",
            },
        ]

        violations = await check_policy_rules(
            program_data=program_data,
            policy_rules=policy_rules,
        )

        assert len(violations) == 0

    @pytest.mark.asyncio
    async def test_check_policy_rules_some_violations(self):
        """Test when some policy rules are violated."""
        program_data = {
            "type": "for-profit",
            "is_temporary": True,
        }
        policy_rules = [
            {
                "id": "rule-1",
                "category": "for_profit",
                "criteria": {"type": "non-profit"},
                "decision": "approved",
            },
            {
                "id": "rule-2",
                "category": "temporary",
                "criteria": {"is_temporary": False},
                "decision": "approved",
            },
        ]

        violations = await check_policy_rules(
            program_data=program_data,
            policy_rules=policy_rules,
        )

        assert len(violations) > 0

    @pytest.mark.asyncio
    async def test_check_policy_rules_with_exceptions(self):
        """Test policy rules with exceptions."""
        program_data = {
            "type": "for-profit",
            "is_subsidized": True,
        }
        policy_rules = [
            {
                "id": "rule-1",
                "category": "for_profit",
                "criteria": {"type": "non-profit"},
                "decision": "approved",
                "exceptions": [{"is_subsidized": True}],
            }
        ]

        violations = await check_policy_rules(
            program_data=program_data,
            policy_rules=policy_rules,
        )

        # Should pass due to exception
        assert len(violations) == 0


class TestGenerateAuditTrail:
    """Test generate_audit_trail function."""

    @pytest.mark.asyncio
    async def test_generate_audit_trail_approved(self):
        """Test audit trail for approved program."""
        program_id = "prog-001"
        violations = []

        trail = await generate_audit_trail(
            program_id=program_id,
            violations=violations,
        )

        assert isinstance(trail, list)
        assert len(trail) > 0
        assert trail[0]["program_id"] == program_id
        assert trail[0]["decision"] == "approved"

    @pytest.mark.asyncio
    async def test_generate_audit_trail_rejected(self):
        """Test audit trail for rejected program."""
        program_id = "prog-002"
        violations = [
            {
                "rule_id": "rule-1",
                "category": "for_profit",
                "reason": "Program is for-profit",
            }
        ]

        trail = await generate_audit_trail(
            program_id=program_id,
            violations=violations,
        )

        assert isinstance(trail, list)
        assert len(trail) > 0
        assert trail[0]["program_id"] == program_id
        assert trail[0]["decision"] == "rejected"

    @pytest.mark.asyncio
    async def test_generate_audit_trail_includes_timestamp(self):
        """Test audit trail includes timestamp."""
        program_id = "prog-003"
        violations = []

        trail = await generate_audit_trail(
            program_id=program_id,
            violations=violations,
        )

        assert "timestamp" in trail[0]

    @pytest.mark.asyncio
    async def test_generate_audit_trail_includes_violations(self):
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

        trail = await generate_audit_trail(
            program_id=program_id,
            violations=violations,
        )

        assert len(trail[0]["violations"]) == 2


class TestRejectProgram:
    """Test reject_program function."""

    @pytest.mark.asyncio
    async def test_reject_program_basic(self):
        """Test basic program rejection."""
        program_id = "prog-001"
        reason = "Program does not meet policy requirements"

        result = await reject_program(
            program_id=program_id,
            reason=reason,
        )

        assert result["program_id"] == program_id
        assert result["decision"] == "rejected"
        assert result["reason"] == reason

    @pytest.mark.asyncio
    async def test_reject_program_with_violations(self):
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
        )

        assert result["program_id"] == program_id
        assert "violations" in result
        assert len(result["violations"]) == 2

    @pytest.mark.asyncio
    async def test_reject_program_includes_timestamp(self):
        """Test rejection includes timestamp."""
        program_id = "prog-003"
        reason = "Policy violation"

        result = await reject_program(
            program_id=program_id,
            reason=reason,
        )

        assert "timestamp" in result


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
                "criteria": {"type": "non-profit"},
                "decision": "approved",
            }
        ]

        result = await validate_program(
            program_id="prog-001",
            program_data=program_data,
            policy_rules=policy_rules,
        )

        # Should handle missing fields gracefully
        assert "valid" in result
        assert "decision" in result

    @pytest.mark.asyncio
    async def test_validate_program_null_values(self):
        """Test validation with null values in program data."""
        program_data = {
            "id": "prog-002",
            "name": "Test Program",
            "type": None,
            "is_temporary": None,
        }
        policy_rules = [
            {
                "id": "rule-1",
                "category": "for_profit",
                "criteria": {"type": "non-profit"},
                "decision": "approved",
            }
        ]

        result = await validate_program(
            program_id="prog-002",
            program_data=program_data,
            policy_rules=policy_rules,
        )

        assert "valid" in result

    @pytest.mark.asyncio
    async def test_validate_program_complex_criteria(self):
        """Test validation with complex criteria matching."""
        program_data = {
            "id": "prog-003",
            "name": "Test Program",
            "type": "non-profit",
            "target_audience": ["adults", "seniors"],
            "location": "Paris",
        }
        policy_rules = [
            {
                "id": "rule-1",
                "category": "audience",
                "criteria": {"target_audience": ["adults"]},
                "decision": "approved",
            }
        ]

        result = await validate_program(
            program_id="prog-003",
            program_data=program_data,
            policy_rules=policy_rules,
        )

        assert result["valid"] is True
