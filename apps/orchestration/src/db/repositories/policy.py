"""Policy rule repository for managing editorial policy rules and decisions."""

import logging
from datetime import datetime
from typing import Any

from db.repositories.base import BaseRepository


logger = logging.getLogger(__name__)


class PolicyRepository(BaseRepository):
    """Repository for managing policy rules and validation decisions."""

    async def get_policy_rules(self, active_only: bool = True) -> list[dict[str, Any]]:
        """Get all policy rules.

        Args:
            active_only: If True, only return active rules

        Returns:
            List of policy rule dictionaries

        Raises:
            Exception: If database query fails
        """
        try:
            logger.debug("Getting policy rules", extra={"active_only": active_only})

            query = "SELECT * FROM policy_rules"
            params = []

            if active_only:
                query += " WHERE is_active = true"

            query += " ORDER BY category, created_at"

            result = await self.db.fetch(query, *params)

            logger.debug(
                "Policy rules retrieved",
                extra={"count": len(result) if result else 0},
            )

            return [dict(row) for row in result] if result else []
        except Exception as e:
            logger.error(
                "Failed to get policy rules",
                extra={"error": str(e)},
            )
            raise

    async def get_rule_by_id(self, rule_id: str) -> dict[str, Any] | None:
        """Get a specific policy rule by ID.

        Args:
            rule_id: ID of the policy rule

        Returns:
            Policy rule dictionary or None if not found

        Raises:
            Exception: If database query fails
        """
        try:
            logger.debug("Getting policy rule", extra={"rule_id": rule_id})

            query = "SELECT * FROM policy_rules WHERE id = $1"
            result = await self.db.fetchrow(query, rule_id)

            if result:
                logger.debug("Policy rule found", extra={"rule_id": rule_id})
                return dict(result)

            logger.debug("Policy rule not found", extra={"rule_id": rule_id})
            return None
        except Exception as e:
            logger.error(
                "Failed to get policy rule",
                extra={"error": str(e), "rule_id": rule_id},
            )
            raise

    async def create_policy_decision(
        self,
        program_id: str,
        decision: str,
        reason: str | None = None,
        violations: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Create a policy validation decision record.

        Args:
            program_id: ID of the program
            decision: Decision (approved/rejected)
            reason: Optional reason for decision
            violations: Optional list of violations

        Returns:
            Created policy decision record

        Raises:
            Exception: If database insert fails
        """
        try:
            logger.info(
                "Creating policy decision",
                extra={"program_id": program_id, "decision": decision},
            )

            decision_id = f"pd_{program_id}_{datetime.utcnow().timestamp()}"

            query = """
                INSERT INTO policy_validation_decisions
                (id, program_id, decision, reason, violations, created_at)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING *
            """

            result = await self.db.fetchrow(
                query,
                decision_id,
                program_id,
                decision,
                reason,
                violations or [],
                datetime.utcnow(),
            )

            logger.info(
                "Policy decision created",
                extra={"decision_id": decision_id, "program_id": program_id},
            )

            return dict(result) if result else {}
        except Exception as e:
            logger.error(
                "Failed to create policy decision",
                extra={"error": str(e), "program_id": program_id},
            )
            raise

    async def get_policy_decision(self, program_id: str) -> dict[str, Any] | None:
        """Get the most recent policy decision for a program.

        Args:
            program_id: ID of the program

        Returns:
            Policy decision record or None if not found

        Raises:
            Exception: If database query fails
        """
        try:
            logger.debug(
                "Getting policy decision",
                extra={"program_id": program_id},
            )

            query = """
                SELECT * FROM policy_validation_decisions
                WHERE program_id = $1
                ORDER BY created_at DESC
                LIMIT 1
            """

            result = await self.db.fetchrow(query, program_id)

            if result:
                logger.debug(
                    "Policy decision found",
                    extra={"program_id": program_id},
                )
                return dict(result)

            logger.debug(
                "Policy decision not found",
                extra={"program_id": program_id},
            )
            return None
        except Exception as e:
            logger.error(
                "Failed to get policy decision",
                extra={"error": str(e), "program_id": program_id},
            )
            raise

    async def get_rule_version(
        self, rule_id: str, version: int | None = None
    ) -> dict[str, Any] | None:
        """Get a specific version of a policy rule.

        Args:
            rule_id: ID of the policy rule
            version: Version number (None for latest)

        Returns:
            Policy rule version or None if not found

        Raises:
            Exception: If database query fails
        """
        try:
            logger.debug(
                "Getting policy rule version",
                extra={"rule_id": rule_id, "version": version},
            )

            if version is None:
                query = """
                    SELECT * FROM policy_rules
                    WHERE id = $1
                    ORDER BY version DESC
                    LIMIT 1
                """
                result = await self.db.fetchrow(query, rule_id)
            else:
                query = """
                    SELECT * FROM policy_rules
                    WHERE id = $1 AND version = $2
                """
                result = await self.db.fetchrow(query, rule_id, version)

            return dict(result) if result else None
        except Exception as e:
            logger.error(
                "Failed to get policy rule version",
                extra={"error": str(e), "rule_id": rule_id, "version": version},
            )
            raise

    async def create_rule_version(
        self,
        rule_id: str,
        category: str,
        criteria: dict[str, Any],
        version: int,
    ) -> dict[str, Any]:
        """Create a new version of a policy rule.

        Args:
            rule_id: ID of the policy rule
            category: Rule category
            criteria: Rule criteria
            version: Version number

        Returns:
            Created rule version

        Raises:
            Exception: If database insert fails
        """
        try:
            logger.info(
                "Creating policy rule version",
                extra={"rule_id": rule_id, "version": version},
            )

            query = """
                INSERT INTO policy_rules
                (id, category, criteria, version, is_active, created_at)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING *
            """

            result = await self.db.fetchrow(
                query,
                rule_id,
                category,
                criteria,
                version,
                True,
                datetime.utcnow(),
            )

            logger.info(
                "Policy rule version created",
                extra={"rule_id": rule_id, "version": version},
            )

            return dict(result) if result else {}
        except Exception as e:
            logger.error(
                "Failed to create policy rule version",
                extra={"error": str(e), "rule_id": rule_id, "version": version},
            )
            raise

    async def track_applied_version(
        self, program_id: str, rule_id: str, version: int
    ) -> dict[str, Any]:
        """Track which version of a rule was applied to a program.

        Args:
            program_id: ID of the program
            rule_id: ID of the policy rule
            version: Version number applied

        Returns:
            Applied version record

        Raises:
            Exception: If database insert fails
        """
        try:
            logger.debug(
                "Tracking applied rule version",
                extra={
                    "program_id": program_id,
                    "rule_id": rule_id,
                    "version": version,
                },
            )

            query = """
                INSERT INTO policy_rule_applications
                (id, program_id, rule_id, version, applied_at)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING *
            """

            application_id = f"pra_{program_id}_{rule_id}_{datetime.utcnow().timestamp()}"

            result = await self.db.fetchrow(
                query,
                application_id,
                program_id,
                rule_id,
                version,
                datetime.utcnow(),
            )

            logger.debug(
                "Applied rule version tracked",
                extra={"application_id": application_id},
            )

            return dict(result) if result else {}
        except Exception as e:
            logger.error(
                "Failed to track applied rule version",
                extra={
                    "error": str(e),
                    "program_id": program_id,
                    "rule_id": rule_id,
                },
            )
            raise

    async def get_rules_by_version(self, version: int) -> list[dict[str, Any]]:
        """Get all policy rules for a specific version.

        Args:
            version: Version number

        Returns:
            List of policy rules for that version

        Raises:
            Exception: If database query fails
        """
        try:
            logger.debug(
                "Getting policy rules by version",
                extra={"version": version},
            )

            query = """
                SELECT * FROM policy_rules
                WHERE version = $1
                ORDER BY category, created_at
            """

            result = await self.db.fetch(query, version)

            logger.debug(
                "Policy rules retrieved",
                extra={"version": version, "count": len(result) if result else 0},
            )

            return [dict(row) for row in result] if result else []
        except Exception as e:
            logger.error(
                "Failed to get policy rules by version",
                extra={"error": str(e), "version": version},
            )
            raise
