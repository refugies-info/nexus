import logging
from datetime import datetime
from typing import Any

from supabase import Client

from .base_repository import BaseRepository

logger = logging.getLogger(__name__)


class InformationSheetRepository(BaseRepository):
    """Repository for information_sheets table operations."""

    def __init__(self, client: Client):
        """Initialize information sheet repository.

        Args:
            client: Supabase client instance
        """
        super().__init__(client, "information_sheets")

    async def create_information_sheet(
        self,
        program_id: str,
        workflow_id: str,
        source_data: dict[str, Any],
        current_stage: str = "ingestion",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a new information sheet.

        Args:
            program_id: ID of the program
            workflow_id: ID of the associated workflow
            source_data: Original source data from Data Inclusion
            current_stage: Current processing stage
            metadata: Optional metadata

        Returns:
            Created information sheet record
        """
        data = {
            "program_id": program_id,
            "workflow_id": workflow_id,
            "source_data": source_data,
            "current_stage": current_stage,
            "status": "processing",
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        return await self.create(data)

    async def get_information_sheet(self, sheet_id: str) -> dict[str, Any]:
        """Get an information sheet by ID.

        Args:
            sheet_id: ID of the information sheet

        Returns:
            Information sheet record if found, None otherwise
        """
        return await self.get_by_id(sheet_id)

    async def get_by_program_id(self, program_id: str) -> dict[str, Any]:
        """Get the information sheet for a program.

        Args:
            program_id: ID of the program

        Returns:
            Information sheet record if found, None otherwise
        """
        sheets = await self.filter({"program_id": program_id}, limit=1)
        return sheets[0] if sheets else None

    async def update_information_sheet(
        self,
        sheet_id: str,
        updates: dict[str, Any],
    ) -> dict[str, Any]:
        """Update an information sheet.

        Args:
            sheet_id: ID of the information sheet
            updates: Fields to update

        Returns:
            Updated information sheet record
        """
        updates["updated_at"] = datetime.utcnow().isoformat()
        return await self.update(sheet_id, updates)

    async def update_stage(self, sheet_id: str, stage: str) -> dict[str, Any]:
        """Update the current stage of an information sheet.

        Args:
            sheet_id: ID of the information sheet
            stage: New stage name

        Returns:
            Updated information sheet record
        """
        return await self.update_information_sheet(sheet_id, {"current_stage": stage})

    async def update_status(self, sheet_id: str, status: str) -> dict[str, Any]:
        """Update the status of an information sheet.

        Args:
            sheet_id: ID of the information sheet
            status: New status (processing, completed, failed, published, rejected)

        Returns:
            Updated information sheet record
        """
        return await self.update_information_sheet(sheet_id, {"status": status})

    async def mark_published(self, sheet_id: str) -> dict[str, Any]:
        """Mark an information sheet as published.

        Args:
            sheet_id: ID of the information sheet

        Returns:
            Updated information sheet record
        """
        return await self.update_information_sheet(
            sheet_id,
            {
                "status": "published",
                "published_at": datetime.utcnow().isoformat(),
            },
        )

    async def mark_rejected(self, sheet_id: str, reason: str) -> dict[str, Any]:
        """Mark an information sheet as rejected.

        Args:
            sheet_id: ID of the information sheet
            reason: Reason for rejection

        Returns:
            Updated information sheet record
        """
        return await self.update_information_sheet(
            sheet_id,
            {
                "status": "rejected",
                "rejection_reason": reason,
                "rejected_at": datetime.utcnow().isoformat(),
            },
        )

    async def list_by_status(
        self, status: str, limit: int = 100, offset: int = 0
    ) -> list[dict[str, Any]]:
        """List information sheets by status.

        Args:
            status: Status to filter by
            limit: Maximum number of records to return
            offset: Number of records to skip

        Returns:
            List of information sheet records
        """
        return await self.filter({"status": status}, limit)

    async def list_by_stage(
        self, stage: str, limit: int = 100, offset: int = 0
    ) -> list[dict[str, Any]]:
        """List information sheets by current stage.

        Args:
            stage: Stage to filter by
            limit: Maximum number of records to return
            offset: Number of records to skip

        Returns:
            List of information sheet records
        """
        return await self.filter({"current_stage": stage}, limit)

    async def count_by_status(self, status: str) -> int:
        """Count information sheets with a specific status.

        Args:
            status: Status to count

        Returns:
            Number of information sheets with the status
        """
        return await self.count({"status": status})

    async def count_by_stage(self, stage: str) -> int:
        """Count information sheets at a specific stage.

        Args:
            stage: Stage to count

        Returns:
            Number of information sheets at the stage
        """
        return await self.count({"current_stage": stage})
