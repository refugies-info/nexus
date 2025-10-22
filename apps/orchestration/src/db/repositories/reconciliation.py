"""Reconciliation repository for managing Carif-Oref data and reconciliation status."""

import logging
from datetime import datetime
from typing import Any

from db.repositories.base import BaseRepository


logger = logging.getLogger(__name__)


class ReconciliationRepository(BaseRepository):
    """Repository for managing Carif-Oref reconciliation data."""

    async def get_latest_csv(self) -> list[dict[str, Any]]:
        """Get the latest Carif-Oref CSV data.

        Returns:
            List of Carif-Oref records

        Raises:
            Exception: If database query fails
        """
        try:
            logger.debug("Getting latest Carif-Oref CSV data")

            query = """
                SELECT * FROM carif_oref_csv
                WHERE fetch_date = (
                    SELECT MAX(fetch_date) FROM carif_oref_csv
                )
                ORDER BY structure_id, service_id
            """

            result = await self.db.fetch(query)

            logger.debug(
                "Carif-Oref CSV retrieved",
                extra={"record_count": len(result) if result else 0},
            )

            return [dict(row) for row in result] if result else []
        except Exception as e:
            logger.error(
                "Failed to get Carif-Oref CSV",
                extra={"error": str(e)},
            )
            raise

    async def create_reconciliation_status(
        self,
        program_id: str,
        status: str,
        carif_oref_data: dict[str, Any] | None = None,
        conflicts: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Create a reconciliation status record.

        Args:
            program_id: ID of the program
            status: Reconciliation status
            carif_oref_data: Carif-Oref data used
            conflicts: Detected conflicts

        Returns:
            Created reconciliation status record

        Raises:
            Exception: If database insert fails
        """
        try:
            logger.info(
                "Creating reconciliation status",
                extra={"program_id": program_id, "status": status},
            )

            status_id = f"rs_{program_id}_{datetime.utcnow().timestamp()}"

            query = """
                INSERT INTO carif_oref_reconciliation_status
                (id, program_id, reconciliation_status, carif_oref_data,
                 conflicts_detected, last_fetch_at, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING *
            """

            result = await self.db.fetchrow(
                query,
                status_id,
                program_id,
                status,
                carif_oref_data or {},
                conflicts or [],
                datetime.utcnow(),
                datetime.utcnow(),
            )

            logger.info(
                "Reconciliation status created",
                extra={"status_id": status_id, "program_id": program_id},
            )

            return dict(result) if result else {}
        except Exception as e:
            logger.error(
                "Failed to create reconciliation status",
                extra={"error": str(e), "program_id": program_id},
            )
            raise

    async def get_reconciliation_status(self, program_id: str) -> dict[str, Any] | None:
        """Get the reconciliation status for a program.

        Args:
            program_id: ID of the program

        Returns:
            Reconciliation status record or None if not found

        Raises:
            Exception: If database query fails
        """
        try:
            logger.debug(
                "Getting reconciliation status",
                extra={"program_id": program_id},
            )

            query = """
                SELECT * FROM carif_oref_reconciliation_status
                WHERE program_id = $1
                ORDER BY created_at DESC
                LIMIT 1
            """

            result = await self.db.fetchrow(query, program_id)

            if result:
                logger.debug(
                    "Reconciliation status found",
                    extra={"program_id": program_id},
                )
                return dict(result)

            logger.debug(
                "Reconciliation status not found",
                extra={"program_id": program_id},
            )
            return None
        except Exception as e:
            logger.error(
                "Failed to get reconciliation status",
                extra={"error": str(e), "program_id": program_id},
            )
            raise

    async def store_csv_fetch(
        self, csv_data: list[dict[str, Any]], fetch_date: datetime
    ) -> dict[str, Any]:
        """Store fetched Carif-Oref CSV data.

        Args:
            csv_data: CSV records to store
            fetch_date: Date of fetch

        Returns:
            Fetch record

        Raises:
            Exception: If database insert fails
        """
        try:
            logger.info(
                "Storing Carif-Oref CSV data",
                extra={"record_count": len(csv_data)},
            )

            fetch_id = f"csf_{datetime.utcnow().timestamp()}"

            # Insert fetch record
            fetch_query = """
                INSERT INTO carif_oref_csv_fetches
                (id, fetch_date, record_count, created_at)
                VALUES ($1, $2, $3, $4)
                RETURNING *
            """

            fetch_result = await self.db.fetchrow(
                fetch_query,
                fetch_id,
                fetch_date,
                len(csv_data),
                datetime.utcnow(),
            )

            # Insert CSV records
            for record in csv_data:
                csv_query = """
                    INSERT INTO carif_oref_csv
                    (id, fetch_id, structure_id, service_id, name,
                     description, address, phone, email, website,
                     department, updated_at, fetch_date)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9,
                            $10, $11, $12, $13)
                """

                record_id = f"csv_{record.get('structure_id')}_{record.get('service_id')}"

                await self.db.execute(
                    csv_query,
                    record_id,
                    fetch_id,
                    record.get("structure_id"),
                    record.get("service_id"),
                    record.get("name"),
                    record.get("description"),
                    record.get("address"),
                    record.get("phone"),
                    record.get("email"),
                    record.get("website"),
                    record.get("department"),
                    record.get("updated_at", datetime.utcnow()),
                    fetch_date,
                )

            logger.info(
                "Carif-Oref CSV data stored",
                extra={"fetch_id": fetch_id, "record_count": len(csv_data)},
            )

            return dict(fetch_result) if fetch_result else {}
        except Exception as e:
            logger.error(
                "Failed to store CSV data",
                extra={"error": str(e), "record_count": len(csv_data)},
            )
            raise

    async def get_csv_by_structure_id(self, structure_id: str) -> list[dict[str, Any]]:
        """Get Carif-Oref records by structure ID.

        Args:
            structure_id: Structure ID

        Returns:
            List of matching records

        Raises:
            Exception: If database query fails
        """
        try:
            logger.debug(
                "Getting Carif-Oref records by structure ID",
                extra={"structure_id": structure_id},
            )

            query = """
                SELECT * FROM carif_oref_csv
                WHERE structure_id = $1
                ORDER BY service_id
            """

            result = await self.db.fetch(query, structure_id)

            logger.debug(
                "Records retrieved",
                extra={"structure_id": structure_id, "count": len(result) if result else 0},
            )

            return [dict(row) for row in result] if result else []
        except Exception as e:
            logger.error(
                "Failed to get records by structure ID",
                extra={"error": str(e), "structure_id": structure_id},
            )
            raise

    async def update_reconciliation_status(
        self, program_id: str, status: str, conflicts: list[dict[str, Any]] | None = None
    ) -> dict[str, Any]:
        """Update reconciliation status for a program.

        Args:
            program_id: ID of the program
            status: New status
            conflicts: Updated conflicts list

        Returns:
            Updated reconciliation status record

        Raises:
            Exception: If database update fails
        """
        try:
            logger.info(
                "Updating reconciliation status",
                extra={"program_id": program_id, "status": status},
            )

            query = """
                UPDATE carif_oref_reconciliation_status
                SET reconciliation_status = $1, conflicts_detected = $2, updated_at = $3
                WHERE program_id = $4
                RETURNING *
            """

            result = await self.db.fetchrow(
                query,
                status,
                conflicts or [],
                datetime.utcnow(),
                program_id,
            )

            logger.info(
                "Reconciliation status updated",
                extra={"program_id": program_id, "status": status},
            )

            return dict(result) if result else {}
        except Exception as e:
            logger.error(
                "Failed to update reconciliation status",
                extra={"error": str(e), "program_id": program_id},
            )
            raise

    async def get_pending_reconciliations(self) -> list[dict[str, Any]]:
        """Get programs pending reconciliation.

        Returns:
            List of programs needing reconciliation

        Raises:
            Exception: If database query fails
        """
        try:
            logger.debug("Getting pending reconciliations")

            query = """
                SELECT * FROM carif_oref_reconciliation_status
                WHERE reconciliation_status IN ('pending', 'data_conflict')
                ORDER BY created_at
            """

            result = await self.db.fetch(query)

            logger.debug(
                "Pending reconciliations retrieved",
                extra={"count": len(result) if result else 0},
            )

            return [dict(row) for row in result] if result else []
        except Exception as e:
            logger.error(
                "Failed to get pending reconciliations",
                extra={"error": str(e)},
            )
            raise
