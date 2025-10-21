import logging
from datetime import datetime
from typing import Any

from supabase import Client

from .base import BaseRepository


logger = logging.getLogger(__name__)


class UpdateRepository(BaseRepository):
    """Repository for update_events table operations."""

    def __init__(self, client: Client):
        """Initialize update repository.

        Args:
            client: Supabase client instance
        """
        super().__init__(client, "update_events")

    async def create_update_event(
        self,
        program_id: str,
        original_stage: str,
        update_strategy: str,
        source_data: dict[str, Any],
        checksum: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a new update event.

        Args:
            program_id: ID of the program being updated
            original_stage: Stage the program was at when update detected
            update_strategy: Strategy to use (full_reprocess or smart_catchup)
            source_data: Updated source data
            checksum: Checksum of the updated data
            metadata: Optional metadata

        Returns:
            Created update event record
        """
        data = {
            "program_id": program_id,
            "original_stage": original_stage,
            "update_strategy": update_strategy,
            "source_data": source_data,
            "checksum": checksum,
            "status": "pending",
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        return await self.create(data)

    async def get_update_event(self, update_id: str) -> dict[str, Any] | None:
        """Get an update event by ID.

        Args:
            update_id: ID of the update event

        Returns:
            Update event record if found, None otherwise
        """
        return await self.get_by_id(update_id)

    async def update_processing_status(
        self,
        update_id: str,
        status: str,
        processing_result: dict[str, Any] | None = None,
        error_message: str | None = None,
    ) -> dict[str, Any]:
        """Update the processing status of an update event.

        Args:
            update_id: ID of the update event
            status: New status (pending, processing, completed, failed)
            processing_result: Optional result from processing
            error_message: Optional error message if failed

        Returns:
            Updated update event record
        """
        data = {
            "status": status,
            "updated_at": datetime.utcnow().isoformat(),
        }
        if processing_result:
            data["processing_result"] = processing_result
        if error_message:
            data["error_message"] = error_message

        return await self.update(update_id, data)

    async def list_pending_updates(self, limit: int = 100) -> list[dict[str, Any]]:
        """List pending update events.

        Args:
            limit: Maximum number of records to return

        Returns:
            List of pending update event records
        """
        return await self.filter({"status": "pending"}, limit)

    async def list_updates_for_program(
        self, program_id: str, limit: int = 100
    ) -> list[dict[str, Any]]:
        """List all updates for a program.

        Args:
            program_id: ID of the program
            limit: Maximum number of records to return

        Returns:
            List of update event records for the program
        """
        return await self.filter({"program_id": program_id}, limit)

    async def list_by_strategy(self, strategy: str, limit: int = 100) -> list[dict[str, Any]]:
        """List updates by strategy type.

        Args:
            strategy: Strategy type (full_reprocess or smart_catchup)
            limit: Maximum number of records to return

        Returns:
            List of update event records with the strategy
        """
        return await self.filter({"update_strategy": strategy}, limit)

    async def mark_processing(self, update_id: str) -> dict[str, Any]:
        """Mark an update event as processing.

        Args:
            update_id: ID of the update event

        Returns:
            Updated update event record
        """
        return await self.update_processing_status(update_id, "processing")

    async def mark_completed(
        self, update_id: str, result: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Mark an update event as completed.

        Args:
            update_id: ID of the update event
            result: Optional result from processing

        Returns:
            Updated update event record
        """
        return await self.update_processing_status(update_id, "completed", processing_result=result)

    async def mark_failed(self, update_id: str, error_message: str) -> dict[str, Any]:
        """Mark an update event as failed.

        Args:
            update_id: ID of the update event
            error_message: Error message describing the failure

        Returns:
            Updated update event record
        """
        return await self.update_processing_status(update_id, "failed", error_message=error_message)

    async def count_by_status(self, status: str) -> int:
        """Count update events with a specific status.

        Args:
            status: Status to count

        Returns:
            Number of update events with the status
        """
        return await self.count({"status": status})

    async def count_by_strategy(self, strategy: str) -> int:
        """Count update events by strategy type.

        Args:
            strategy: Strategy type to count

        Returns:
            Number of update events with the strategy
        """
        return await self.count({"update_strategy": strategy})
