"""Editorial policy validator service for program compliance checking."""

import logging
from datetime import datetime
from typing import Any

from db.repositories.policy import PolicyRepository
from utils.errors import PipelineError


logger = logging.getLogger(__name__)


class PolicyValidator:
    """Service for validating programs against editorial policies."""

    def __init__(self, policy_repo: PolicyRepository):
        """Initialize policy validator.

        Args:
            policy_repo: PolicyRepository instance for accessing policy rules
        """
        self.policy_repo = policy_repo

    async def validate_program(
        self, program_id: str, program_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate a program against all applicable editorial policies.

        Args:
            program_id: ID of the program being validated
            program_data: Program data to validate

        Returns:
            Dictionary with validation result and audit trail

        Raises:
            PipelineError: If validation fails
        """
        try:
            logger.info(
                "Starting policy validation",
                extra={"program_id": program_id},
            )

            # Get all active policy rules
            policy_rules = await self.policy_repo.get_policy_rules()

            if not policy_rules:
                logger.warning(
                    "No policy rules found",
                    extra={"program_id": program_id},
                )
                return {
                    "program_id": program_id,
                    "is_compliant": True,
                    "violations": [],
                    "audit_trail": [
                        {
                            "timestamp": datetime.utcnow().isoformat(),
                            "message": "No policy rules configured",
                        }
                    ],
                }

            violations = []
            audit_trail = [
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "message": f"Validating against {len(policy_rules)} policy rules",
                }
            ]

            # Check each policy rule
            for rule in policy_rules:
                is_violated = await self._check_policy_rule(program_id, program_data, rule)

                if is_violated:
                    violations.append(
                        {
                            "rule_id": rule.get("id"),
                            "category": rule.get("category"),
                            "reason": rule.get("criteria"),
                        }
                    )
                    audit_trail.append(
                        {
                            "timestamp": datetime.utcnow().isoformat(),
                            "message": f"Policy violation: {rule.get('category')}",
                            "rule_id": rule.get("id"),
                        }
                    )

            is_compliant = len(violations) == 0

            logger.info(
                "Policy validation completed",
                extra={
                    "program_id": program_id,
                    "is_compliant": is_compliant,
                    "violation_count": len(violations),
                },
            )

            return {
                "program_id": program_id,
                "is_compliant": is_compliant,
                "violations": violations,
                "audit_trail": audit_trail,
            }
        except Exception as e:
            logger.error(
                "Failed to validate program",
                extra={"error": str(e), "program_id": program_id},
            )
            raise PipelineError(f"Failed to validate program: {str(e)}") from e

    async def check_policy_rules(self, program_data: dict[str, Any]) -> list[dict[str, Any]]:
        """Check which policy rules apply to a program.

        Args:
            program_data: Program data to check

        Returns:
            List of applicable policy rules

        Raises:
            PipelineError: If check fails
        """
        try:
            logger.debug("Checking applicable policy rules")

            policy_rules = await self.policy_repo.get_policy_rules()

            applicable_rules = []
            for rule in policy_rules:
                if await self._is_rule_applicable(program_data, rule):
                    applicable_rules.append(rule)

            logger.debug(
                "Policy rules checked",
                extra={"applicable_count": len(applicable_rules)},
            )

            return applicable_rules
        except Exception as e:
            logger.error(
                "Failed to check policy rules",
                extra={"error": str(e)},
            )
            raise PipelineError(f"Failed to check policy rules: {str(e)}") from e

    async def generate_audit_trail(
        self, program_id: str, validation_result: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate detailed audit trail for policy validation.

        Args:
            program_id: ID of the program
            validation_result: Result from validate_program

        Returns:
            Audit trail with timestamps and details

        Raises:
            PipelineError: If audit trail generation fails
        """
        try:
            logger.info(
                "Generating audit trail",
                extra={"program_id": program_id},
            )

            audit_trail = {
                "program_id": program_id,
                "validation_timestamp": datetime.utcnow().isoformat(),
                "is_compliant": validation_result.get("is_compliant"),
                "violations": validation_result.get("violations", []),
                "events": validation_result.get("audit_trail", []),
            }

            logger.info(
                "Audit trail generated",
                extra={
                    "program_id": program_id,
                    "event_count": len(audit_trail["events"]),
                },
            )

            return audit_trail
        except Exception as e:
            logger.error(
                "Failed to generate audit trail",
                extra={"error": str(e), "program_id": program_id},
            )
            raise PipelineError(f"Failed to generate audit trail: {str(e)}") from e

    async def reject_program(
        self, program_id: str, reason: str, violations: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Reject a program due to policy violations.

        Args:
            program_id: ID of the program to reject
            reason: Reason for rejection
            violations: List of policy violations

        Returns:
            Rejection record with details

        Raises:
            PipelineError: If rejection fails
        """
        try:
            logger.warning(
                "Rejecting program due to policy violations",
                extra={
                    "program_id": program_id,
                    "reason": reason,
                    "violation_count": len(violations),
                },
            )

            rejection_record = {
                "program_id": program_id,
                "rejected_at": datetime.utcnow().isoformat(),
                "reason": reason,
                "violations": violations,
                "status": "rejected",
            }

            # Create policy decision record
            decision = await self.policy_repo.create_policy_decision(
                program_id=program_id,
                decision="rejected",
                reason=reason,
                violations=violations,
            )

            logger.warning(
                "Program rejected",
                extra={
                    "program_id": program_id,
                    "decision_id": decision.get("id"),
                },
            )

            return rejection_record
        except Exception as e:
            logger.error(
                "Failed to reject program",
                extra={"error": str(e), "program_id": program_id},
            )
            raise PipelineError(f"Failed to reject program: {str(e)}") from e

    async def _check_policy_rule(
        self, program_id: str, program_data: dict[str, Any], rule: dict[str, Any]
    ) -> bool:
        """Check if a program violates a specific policy rule.

        Args:
            program_id: ID of the program
            program_data: Program data to check
            rule: Policy rule to check

        Returns:
            True if rule is violated, False otherwise
        """
        try:
            rule_category = rule.get("category", "")
            rule_criteria = rule.get("criteria", {})

            # Check based on rule category
            if rule_category == "for_profit":
                return await self._check_for_profit_rule(program_data, rule_criteria)
            elif rule_category == "temporary":
                return await self._check_temporary_rule(program_data, rule_criteria)
            elif rule_category == "out_of_scope_public":
                return await self._check_out_of_scope_public_rule(program_data, rule_criteria)
            elif rule_category == "specialized_structure":
                return await self._check_specialized_structure_rule(program_data, rule_criteria)
            else:
                logger.debug(
                    "Unknown rule category",
                    extra={"category": rule_category, "program_id": program_id},
                )
                return False

        except Exception as e:
            logger.error(
                "Failed to check policy rule",
                extra={
                    "error": str(e),
                    "program_id": program_id,
                    "rule_id": rule.get("id"),
                },
            )
            return False

    async def _is_rule_applicable(self, program_data: dict[str, Any], rule: dict[str, Any]) -> bool:
        """Check if a policy rule is applicable to a program.

        Args:
            program_data: Program data
            rule: Policy rule

        Returns:
            True if rule is applicable, False otherwise
        """
        # For now, all rules are applicable
        # In future, could add conditions based on program type, region, etc.
        return True

    async def _check_for_profit_rule(
        self, program_data: dict[str, Any], criteria: dict[str, Any]
    ) -> bool:
        """Check if program violates for-profit policy.

        Args:
            program_data: Program data
            criteria: Rule criteria

        Returns:
            True if violated, False otherwise
        """
        # Check if program is for-profit
        is_for_profit = program_data.get("is_for_profit", False)

        if not is_for_profit:
            return False

        # Check for exceptions (subsidized, certified)
        exceptions = criteria.get("exceptions", [])
        if "subsidized" in exceptions and program_data.get("is_subsidized"):
            return False
        if "certified" in exceptions and program_data.get("is_certified"):
            return False

        return True

    async def _check_temporary_rule(
        self, program_data: dict[str, Any], criteria: dict[str, Any]
    ) -> bool:
        """Check if program violates temporary initiative policy.

        Args:
            program_data: Program data
            criteria: Rule criteria

        Returns:
            True if violated, False otherwise
        """
        # Check if program is temporary or one-time
        is_temporary = program_data.get("is_temporary", False)
        is_one_time = program_data.get("is_one_time", False)

        return is_temporary or is_one_time

    async def _check_out_of_scope_public_rule(
        self, program_data: dict[str, Any], criteria: dict[str, Any]
    ) -> bool:
        """Check if program targets out-of-scope public.

        Args:
            program_data: Program data
            criteria: Rule criteria

        Returns:
            True if violated, False otherwise
        """
        # Check target publics
        target_publics = program_data.get("target_publics", [])
        out_of_scope_publics = criteria.get("out_of_scope_publics", [])

        for public in target_publics:
            if public in out_of_scope_publics:
                return True

        return False

    async def _check_specialized_structure_rule(
        self, program_data: dict[str, Any], criteria: dict[str, Any]
    ) -> bool:
        """Check if program is a specialized structure.

        Args:
            program_data: Program data
            criteria: Rule criteria

        Returns:
            True if violated, False otherwise
        """
        # Check structure type
        structure_type = program_data.get("structure_type", "")
        specialized_structures = criteria.get("specialized_structures", [])

        return structure_type in specialized_structures
