import logging
from datetime import datetime
from typing import Any

from supabase import Client

from .base import BaseRepository


logger = logging.getLogger(__name__)


class DiffRepository(BaseRepository):
    """Repository for update_diffs table operations."""

    def __init__(self, client: Client):
        """Initialize diff repository.

        Args:
            client: Supabase client instance
        """
        super().__init__(client, "update_diffs")

    async def create_diff(
        self,
        update_id: str,
        program_id: str,
        original_data: dict[str, Any],
        updated_data: dict[str, Any],
        diff_content: dict[str, Any],
        risk_score: float,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a new diff record.

        Args:
            update_id: ID of the associated update event
            program_id: ID of the program
            original_data: Original information sheet data
            updated_data: Updated information sheet data
            diff_content: Detailed diff content
            risk_score: Risk score (0.0-1.0)
            metadata: Optional metadata

        Returns:
            Created diff record
        """
        data = {
            "update_id": update_id,
            "program_id": program_id,
            "original_data": original_data,
            "updated_data": updated_data,
            "diff_content": diff_content,
            "risk_score": risk_score,
            "review_status": "pending",
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        return await self.create(data)

    async def get_diff(self, diff_id: str) -> dict[str, Any] | None:
        """Get a diff record by ID.

        Args:
            diff_id: ID of the diff

        Returns:
            Diff record if found, None otherwise
        """
        return await self.get_by_id(diff_id)

    async def get_diff_for_update(self, update_id: str) -> dict[str, Any] | None:
        """Get the diff record for an update event.

        Args:
            update_id: ID of the update event

        Returns:
            Diff record if found, None otherwise
        """
        diffs = await self.filter({"update_id": update_id}, limit=1)
        return diffs[0] if diffs else None

    async def update_review_status(
        self,
        diff_id: str,
        review_status: str,
        reviewer_id: str | None = None,
        review_notes: str | None = None,
    ) -> dict[str, Any]:
        """Update the review status of a diff.

        Args:
            diff_id: ID of the diff
            review_status: New review status (pending, approved, rejected, needs_edit)
            reviewer_id: Optional ID of the reviewer
            review_notes: Optional notes from the review

        Returns:
            Updated diff record
        """
        data = {
            "review_status": review_status,
            "updated_at": datetime.utcnow().isoformat(),
        }
        if reviewer_id:
            data["reviewer_id"] = reviewer_id
        if review_notes:
            data["review_notes"] = review_notes

        return await self.update(diff_id, data)

    async def list_pending_diffs(self, limit: int = 100) -> list[dict[str, Any]]:
        """List diffs pending review.

        Args:
            limit: Maximum number of records to return

        Returns:
            List of pending diff records
        """
        return await self.filter({"review_status": "pending"}, limit)

    async def list_diffs_by_risk_level(
        self, min_risk: float, max_risk: float, limit: int = 100
    ) -> list[dict[str, Any]]:
        """List diffs within a risk score range.

        Args:
            min_risk: Minimum risk score
            max_risk: Maximum risk score
            limit: Maximum number of records to return

        Returns:
            List of diff records within the risk range
        """
        diffs = await self.list_all(limit)
        return [d for d in diffs if min_risk <= d.get("risk_score", 0) <= max_risk]

    async def list_high_risk_diffs(
        self, threshold: float = 0.8, limit: int = 100
    ) -> list[dict[str, Any]]:
        """List high-risk diffs (above threshold).

        Args:
            threshold: Risk score threshold for high-risk
            limit: Maximum number of records to return

        Returns:
            List of high-risk diff records
        """
        diffs = await self.list_all(limit)
        return [d for d in diffs if d.get("risk_score", 0) > threshold]

    async def list_diffs_for_program(
        self, program_id: str, limit: int = 100
    ) -> list[dict[str, Any]]:
        """List all diffs for a program.

        Args:
            program_id: ID of the program
            limit: Maximum number of records to return

        Returns:
            List of diff records for the program
        """
        return await self.filter({"program_id": program_id}, limit)

    async def mark_approved(
        self, diff_id: str, reviewer_id: str, notes: str | None = None
    ) -> dict[str, Any]:
        """Mark a diff as approved.

        Args:
            diff_id: ID of the diff
            reviewer_id: ID of the reviewer
            notes: Optional approval notes

        Returns:
            Updated diff record
        """
        return await self.update_review_status(
            diff_id, "approved", reviewer_id=reviewer_id, review_notes=notes
        )

    async def mark_rejected(self, diff_id: str, reviewer_id: str, reason: str) -> dict[str, Any]:
        """Mark a diff as rejected.

        Args:
            diff_id: ID of the diff
            reviewer_id: ID of the reviewer
            reason: Reason for rejection

        Returns:
            Updated diff record
        """
        return await self.update_review_status(
            diff_id, "rejected", reviewer_id=reviewer_id, review_notes=reason
        )

    async def mark_needs_edit(
        self, diff_id: str, reviewer_id: str, edit_notes: str
    ) -> dict[str, Any]:
        """Mark a diff as needing edits.

        Args:
            diff_id: ID of the diff
            reviewer_id: ID of the reviewer
            edit_notes: Notes about required edits

        Returns:
            Updated diff record
        """
        return await self.update_review_status(
            diff_id, "needs_edit", reviewer_id=reviewer_id, review_notes=edit_notes
        )

    async def count_by_review_status(self, review_status: str) -> int:
        """Count diffs with a specific review status.

        Args:
            review_status: Review status to count

        Returns:
            Number of diffs with the review status
        """
        return await self.count({"review_status": review_status})

    async def count_pending_reviews(self) -> int:
        """Count diffs pending review.

        Returns:
            Number of diffs pending review
        """
        return await self.count_by_review_status("pending")
