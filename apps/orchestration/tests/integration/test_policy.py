"""Integration tests for policy validation."""

import pytest

from services.policy import generate_audit_trail, reject_program, validate_program


class TestPolicyValidationIntegration:
    """Integration tests for policy validation with real scenarios."""

    @pytest.mark.asyncio
    async def test_validate_compliant_program_end_to_end(self, mock_policy_repo):
        """Test end-to-end validation of compliant program."""
        program_data = {
            "id": "prog-001",
            "name": "French Language Course",
            "description": "Learn French for refugees",
            "is_for_profit": False,
            "is_temporary": False,
            "is_subsidized": False,
            "target_publics": ["adults", "families"],
            "structure_type": "association",
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

        result = await validate_program(
            program_id="prog-001",
            program_data=program_data,
            policy_rules=policy_rules,
        )

        assert result["is_compliant"] is True
        assert len(result["violations"]) == 0
        assert "audit_trail" in result

    @pytest.mark.asyncio
    async def test_validate_non_compliant_for_profit_program(self, mock_policy_repo):
        """Test validation rejects for-profit programs."""
        program_data = {
            "id": "prog-002",
            "name": "Commercial Training",
            "is_for_profit": True,
            "is_subsidized": False,
            "is_certified": False,
        }

        policy_rules = [
            {
                "id": "rule-1",
                "category": "for_profit",
                "criteria": {"exceptions": []},
            }
        ]

        result = await validate_program(
            program_id="prog-002",
            program_data=program_data,
            policy_rules=policy_rules,
        )

        assert result["is_compliant"] is False
        assert len(result["violations"]) == 1
        assert result["violations"][0]["category"] == "for_profit"

    @pytest.mark.asyncio
    async def test_validate_for_profit_with_subsidy_exception(self, mock_policy_repo):
        """Test for-profit exception when subsidized."""
        program_data = {
            "id": "prog-003",
            "name": "Subsidized Training",
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

        result = await validate_program(
            program_id="prog-003",
            program_data=program_data,
            policy_rules=policy_rules,
        )

        assert result["is_compliant"] is True

    @pytest.mark.asyncio
    async def test_validate_temporary_initiative_rejected(self, mock_policy_repo):
        """Test validation rejects temporary initiatives."""
        program_data = {
            "id": "prog-004",
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
            program_id="prog-004",
            program_data=program_data,
            policy_rules=policy_rules,
        )

        assert result["is_compliant"] is False

    @pytest.mark.asyncio
    async def test_validate_out_of_scope_public_rejected(self, mock_policy_repo):
        """Test validation rejects programs targeting out-of-scope publics."""
        program_data = {
            "id": "prog-005",
            "name": "Specialized Program",
            "target_publics": ["unaccompanied_minors"],
        }

        policy_rules = [
            {
                "id": "rule-3",
                "category": "out_of_scope_public",
                "criteria": {"out_of_scope_publics": ["unaccompanied_minors"]},
            }
        ]

        result = await validate_program(
            program_id="prog-005",
            program_data=program_data,
            policy_rules=policy_rules,
        )

        assert result["is_compliant"] is False
        assert result["violations"][0]["category"] == "out_of_scope_public"

    @pytest.mark.asyncio
    async def test_validate_specialized_structure_rejected(self, mock_policy_repo):
        """Test validation rejects specialized structures."""
        program_data = {
            "id": "prog-006",
            "name": "France Services",
            "structure_type": "france_services",
        }

        policy_rules = [
            {
                "id": "rule-4",
                "category": "specialized_structure",
                "criteria": {"specialized_structures": ["france_services"]},
            }
        ]

        result = await validate_program(
            program_id="prog-006",
            program_data=program_data,
            policy_rules=policy_rules,
        )

        assert result["is_compliant"] is False

    @pytest.mark.asyncio
    async def test_validate_multiple_violations(self, mock_policy_repo):
        """Test validation with multiple policy violations."""
        program_data = {
            "id": "prog-007",
            "name": "Non-Compliant Program",
            "is_for_profit": True,
            "is_temporary": True,
            "target_publics": ["unaccompanied_minors"],
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
            {
                "id": "rule-3",
                "category": "out_of_scope_public",
                "criteria": {"out_of_scope_publics": ["unaccompanied_minors"]},
            },
        ]

        result = await validate_program(
            program_id="prog-007",
            program_data=program_data,
            policy_rules=policy_rules,
        )

        assert result["is_compliant"] is False
        assert len(result["violations"]) == 3

    @pytest.mark.asyncio
    async def test_reject_program_creates_audit_trail(self, mock_policy_repo):
        """Test rejection creates proper audit trail."""
        violations = [
            {
                "rule_id": "rule-1",
                "category": "for_profit",
                "reason": "Program is for-profit",
            }
        ]

        result = await reject_program(
            program_id="prog-008",
            reason="Non-compliant with editorial policy",
            violations=violations,
            repo=mock_policy_repo,
        )

        assert result["program_id"] == "prog-008"
        assert result["status"] == "rejected"
        assert "rejected_at" in result
        assert len(result["violations"]) == 1

    @pytest.mark.asyncio
    async def test_generate_audit_trail_for_approved_program(self):
        """Test audit trail generation for approved program."""
        validation_result = {
            "program_id": "prog-009",
            "is_compliant": True,
            "violations": [],
            "audit_trail": [
                {
                    "timestamp": "2025-10-21T18:00:00",
                    "message": "Validation started",
                }
            ],
        }

        trail = generate_audit_trail(
            program_id="prog-009",
            validation_result=validation_result,
        )

        assert trail["program_id"] == "prog-009"
        assert trail["is_compliant"] is True
        assert len(trail["events"]) >= 1

    @pytest.mark.asyncio
    async def test_generate_audit_trail_for_rejected_program(self):
        """Test audit trail generation for rejected program."""
        violations = [
            {
                "rule_id": "rule-1",
                "category": "for_profit",
                "reason": "Program is for-profit",
            },
            {
                "rule_id": "rule-2",
                "category": "temporary",
                "reason": "Program is temporary",
            },
        ]
        validation_result = {
            "program_id": "prog-010",
            "is_compliant": False,
            "violations": violations,
            "audit_trail": [],
        }

        trail = generate_audit_trail(
            program_id="prog-010",
            validation_result=validation_result,
        )

        assert trail["program_id"] == "prog-010"
        assert trail["is_compliant"] is False
        assert len(trail["violations"]) == 2


class TestPolicyValidationRealWorldScenarios:
    """Test policy validation with real-world program scenarios."""

    @pytest.mark.asyncio
    async def test_validate_legitimate_ngo_program(self, mock_policy_repo):
        """Test validation of legitimate NGO program."""
        program_data = {
            "id": "prog-ngo-001",
            "name": "Integration Support Program",
            "description": "Comprehensive support for refugee integration",
            "is_for_profit": False,
            "is_temporary": False,
            "is_subsidized": True,
            "target_publics": ["adults", "families", "youth"],
            "structure_type": "association",
            "location": "Paris",
            "contact_email": "info@program.org",
        }

        policy_rules = [
            {"id": "rule-1", "category": "for_profit", "criteria": {}},
            {"id": "rule-2", "category": "temporary", "criteria": {}},
            {
                "id": "rule-3",
                "category": "out_of_scope_public",
                "criteria": {"out_of_scope_publics": ["unaccompanied_minors"]},
            },
        ]

        result = await validate_program(
            program_id="prog-ngo-001",
            program_data=program_data,
            policy_rules=policy_rules,
        )

        assert result["is_compliant"] is True

    @pytest.mark.asyncio
    async def test_validate_government_service_program(self, mock_policy_repo):
        """Test validation of government service program."""
        program_data = {
            "id": "prog-gov-001",
            "name": "France Travail Services",
            "structure_type": "france_travail",
            "is_for_profit": False,
            "is_temporary": False,
        }

        policy_rules = [
            {
                "id": "rule-4",
                "category": "specialized_structure",
                "criteria": {
                    "specialized_structures": [
                        "france_services",
                        "france_travail",
                        "local_missions",
                    ]
                },
            }
        ]

        result = await validate_program(
            program_id="prog-gov-001",
            program_data=program_data,
            policy_rules=policy_rules,
        )

        assert result["is_compliant"] is False

    @pytest.mark.asyncio
    async def test_validate_commercial_training_with_subsidy(self, mock_policy_repo):
        """Test validation of commercial training with subsidy exception."""
        program_data = {
            "id": "prog-commercial-001",
            "name": "Vocational Training Center",
            "is_for_profit": True,
            "is_subsidized": True,
            "is_certified": True,
            "target_publics": ["adults"],
        }

        policy_rules = [
            {
                "id": "rule-1",
                "category": "for_profit",
                "criteria": {"exceptions": ["subsidized", "certified"]},
            }
        ]

        result = await validate_program(
            program_id="prog-commercial-001",
            program_data=program_data,
            policy_rules=policy_rules,
        )

        assert result["is_compliant"] is True

    @pytest.mark.asyncio
    async def test_validate_temporary_workshop_rejected(self, mock_policy_repo):
        """Test validation rejects temporary workshop."""
        program_data = {
            "id": "prog-workshop-001",
            "name": "One-Day French Workshop",
            "is_temporary": True,
            "is_one_time": True,
            "target_publics": ["adults"],
        }

        policy_rules = [
            {
                "id": "rule-2",
                "category": "temporary",
                "criteria": {},
            }
        ]

        result = await validate_program(
            program_id="prog-workshop-001",
            program_data=program_data,
            policy_rules=policy_rules,
        )

        assert result["is_compliant"] is False
