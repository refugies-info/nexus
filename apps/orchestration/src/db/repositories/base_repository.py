import logging
from typing import Any, TypeVar

from supabase import Client

logger = logging.getLogger(__name__)

T = TypeVar("T")


class BaseRepository:
    """Base repository class with common CRUD operations."""

    def __init__(self, client: Client, table_name: str) -> None:
        """Initialize base repository.

        Args:
            client: Supabase client instance
            table_name: Name of the database table
        """
        self.client = client
        self.table_name = table_name

    async def create(self, data: dict[str, Any]) -> T:
        """Create a new record.

        Args:
            data: Record data to insert

        Returns:
            Created record

        Raises:
            Exception: If creation fails
        """
        try:
            response = self.client.table(self.table_name).insert(data).execute()
            logger.debug(f"Created record in {self.table_name}", extra={"data": data})
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(
                f"Failed to create record in {self.table_name}",
                extra={"error": str(e), "data": data},
            )
            raise

    async def get_by_id(self, record_id: str) -> T | None:
        """Get a record by ID.

        Args:
            record_id: ID of the record to retrieve

        Returns:
            Record if found, None otherwise

        Raises:
            Exception: If retrieval fails
        """
        try:
            response = self.client.table(self.table_name).select("*").eq("id", record_id).execute()
            logger.debug(f"Retrieved record from {self.table_name}", extra={"id": record_id})
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(
                f"Failed to retrieve record from {self.table_name}",
                extra={"error": str(e), "id": record_id},
            )
            raise

    async def update(self, record_id: str, data: dict[str, Any]) -> T:
        """Update an existing record.

        Args:
            record_id: ID of the record to update
            data: Fields to update

        Returns:
            Updated record

        Raises:
            Exception: If update fails
        """
        try:
            response = self.client.table(self.table_name).update(data).eq("id", record_id).execute()
            logger.debug(
                f"Updated record in {self.table_name}",
                extra={"id": record_id, "data": data},
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(
                f"Failed to update record in {self.table_name}",
                extra={"error": str(e), "id": record_id, "data": data},
            )
            raise

    async def delete(self, record_id: str) -> bool:
        """Delete a record.

        Args:
            record_id: ID of the record to delete

        Returns:
            True if deletion was successful

        Raises:
            Exception: If deletion fails
        """
        try:
            self.client.table(self.table_name).delete().eq("id", record_id).execute()
            logger.debug(f"Deleted record from {self.table_name}", extra={"id": record_id})
            return True
        except Exception as e:
            logger.error(
                f"Failed to delete record from {self.table_name}",
                extra={"error": str(e), "id": record_id},
            )
            raise

    async def list_all(self, limit: int = 100, offset: int = 0) -> list[T]:
        """List all records with pagination.

        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip

        Returns:
            List of records

        Raises:
            Exception: If retrieval fails
        """
        try:
            response = (
                self.client.table(self.table_name)
                .select("*")
                .range(offset, offset + limit - 1)
                .execute()
            )
            logger.debug(
                f"Listed records from {self.table_name}",
                extra={"limit": limit, "offset": offset},
            )
            return response.data if response.data else []
        except Exception as e:
            logger.error(
                f"Failed to list records from {self.table_name}",
                extra={"error": str(e), "limit": limit, "offset": offset},
            )
            raise

    async def filter(self, filters: dict[str, Any], limit: int = 100) -> list[T]:
        """Filter records by criteria.

        Args:
            filters: Dictionary of field:value pairs to filter by
            limit: Maximum number of records to return

        Returns:
            List of matching records

        Raises:
            Exception: If filtering fails
        """
        try:
            query = self.client.table(self.table_name).select("*")
            for field, value in filters.items():
                query = query.eq(field, value)
            response = query.limit(limit).execute()
            logger.debug(
                f"Filtered records from {self.table_name}",
                extra={"filters": filters, "limit": limit},
            )
            return response.data if response.data else []
        except Exception as e:
            logger.error(
                f"Failed to filter records from {self.table_name}",
                extra={"error": str(e), "filters": filters},
            )
            raise

    async def count(self, filters: dict[str, Any] | None = None) -> int:
        """Count records matching optional filters.

        Args:
            filters: Optional dictionary of field:value pairs to filter by

        Returns:
            Number of matching records

        Raises:
            Exception: If count fails
        """
        try:
            query = self.client.table(self.table_name).select("id", count="exact")
            if filters:
                for field, value in filters.items():
                    query = query.eq(field, value)
            response = query.execute()
            count = response.count if hasattr(response, "count") else len(response.data)
            logger.debug(
                f"Counted records in {self.table_name}",
                extra={"count": count, "filters": filters},
            )
            return count
        except Exception as e:
            logger.error(
                f"Failed to count records in {self.table_name}",
                extra={"error": str(e), "filters": filters},
            )
            raise
