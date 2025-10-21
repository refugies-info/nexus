from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ReviewStatus(str, Enum):
    """Review status of a diff."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_EDIT = "needs_edit"


class RiskScore(BaseModel):
    """Risk score for a diff (0.0-1.0)."""

    value: float = Field(
        ..., ge=0.0, le=1.0, description="Risk score between 0.0 (low) and 1.0 (high)"
    )
    category: str = Field(..., description="Risk category (low, medium, high)")

    @property
    def is_high_risk(self) -> bool:
        """Check if diff is high-risk (>0.8)."""
        return self.value > 0.8

    @property
    def is_medium_risk(self) -> bool:
        """Check if diff is medium-risk (0.5-0.8)."""
        return 0.5 <= self.value <= 0.8

    @property
    def is_low_risk(self) -> bool:
        """Check if diff is low-risk (<0.5)."""
        return self.value < 0.5

    class Config:
        json_schema_extra = {
            "example": {
                "value": 0.75,
                "category": "medium",
            }
        }


class DiffRequest(BaseModel):
    """Request model for creating a diff."""

    update_id: str = Field(..., description="ID of the associated update event")
    program_id: str = Field(..., description="ID of the program")
    original_data: dict[str, Any] = Field(..., description="Original information sheet data")
    updated_data: dict[str, Any] = Field(..., description="Updated information sheet data")
    diff_content: dict[str, Any] = Field(..., description="Detailed diff content")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Risk score between 0.0 and 1.0")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Optional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "update_id": "upd_456",
                "program_id": "prog_123",
                "original_data": {"name": "Program Name"},
                "updated_data": {"name": "Updated Program Name"},
                "diff_content": {"name": {"old": "Program Name", "new": "Updated Program Name"}},
                "risk_score": 0.3,
                "metadata": {"fields_changed": 1},
            }
        }


class DiffResponse(BaseModel):
    """Response model for a diff."""

    id: str = Field(..., description="Unique diff ID")
    update_id: str = Field(..., description="ID of the associated update event")
    program_id: str = Field(..., description="ID of the program")
    original_data: dict[str, Any] = Field(..., description="Original information sheet data")
    updated_data: dict[str, Any] = Field(..., description="Updated information sheet data")
    diff_content: dict[str, Any] = Field(..., description="Detailed diff content")
    risk_score: RiskScore = Field(..., description="Risk score assessment")
    review_status: ReviewStatus = Field(..., description="Current review status")
    reviewer_id: str | None = Field(default=None, description="ID of the reviewer")
    review_notes: str | None = Field(default=None, description="Notes from the review")
    metadata: dict[str, Any] = Field(..., description="Diff metadata")
    created_at: datetime = Field(..., description="Diff creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "diff_789",
                "update_id": "upd_456",
                "program_id": "prog_123",
                "original_data": {"name": "Program Name"},
                "updated_data": {"name": "Updated Program Name"},
                "diff_content": {"name": {"old": "Program Name", "new": "Updated Program Name"}},
                "risk_score": {"value": 0.3, "category": "low"},
                "review_status": "pending",
                "reviewer_id": None,
                "review_notes": None,
                "metadata": {"fields_changed": 1},
                "created_at": "2025-10-21T10:15:00",
                "updated_at": "2025-10-21T10:15:00",
            }
        }


class DiffReviewRequest(BaseModel):
    """Model for reviewing a diff."""

    review_status: ReviewStatus = Field(..., description="Review decision")
    reviewer_id: str = Field(..., description="ID of the reviewer")
    review_notes: str | None = Field(default=None, description="Optional notes from the review")

    class Config:
        json_schema_extra = {
            "example": {
                "review_status": "approved",
                "reviewer_id": "user_123",
                "review_notes": "Changes look good, approved for publication",
            }
        }
