from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class UpdateStrategy(str, Enum):
    """Strategy for handling data updates."""

    FULL_REPROCESS = "full_reprocess"
    SMART_CATCHUP = "smart_catchup"


class UpdateStatus(str, Enum):
    """Status of an update event."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class UpdateEventRequest(BaseModel):
    """Request model for creating an update event."""

    program_id: str = Field(..., description="ID of the program being updated")
    original_stage: str = Field(..., description="Stage the program was at when update detected")
    update_strategy: UpdateStrategy = Field(
        ..., description="Strategy to use for handling the update"
    )
    source_data: dict[str, Any] = Field(..., description="Updated source data")
    checksum: str = Field(..., description="Checksum of the updated data")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Optional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "program_id": "prog_123",
                "original_stage": "enrichment",
                "update_strategy": "smart_catchup",
                "source_data": {"name": "Updated Program Name"},
                "checksum": "abc123def456",
                "metadata": {"source": "data_inclusion_update"},
            }
        }


class UpdateEventResponse(BaseModel):
    """Response model for an update event."""

    id: str = Field(..., description="Unique update event ID")
    program_id: str = Field(..., description="ID of the program being updated")
    original_stage: str = Field(..., description="Stage the program was at when update detected")
    update_strategy: UpdateStrategy = Field(
        ..., description="Strategy used for handling the update"
    )
    source_data: dict[str, Any] = Field(..., description="Updated source data")
    checksum: str = Field(..., description="Checksum of the updated data")
    status: UpdateStatus = Field(..., description="Current update processing status")
    processing_result: dict[str, Any] | None = Field(
        default=None, description="Result from processing"
    )
    error_message: str | None = Field(
        default=None, description="Error message if processing failed"
    )
    metadata: dict[str, Any] = Field(..., description="Update event metadata")
    created_at: datetime = Field(..., description="Event creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "upd_456",
                "program_id": "prog_123",
                "original_stage": "enrichment",
                "update_strategy": "smart_catchup",
                "source_data": {"name": "Updated Program Name"},
                "checksum": "abc123def456",
                "status": "completed",
                "processing_result": {"diff_generated": True},
                "error_message": None,
                "metadata": {"source": "data_inclusion_update"},
                "created_at": "2025-10-21T10:10:00",
                "updated_at": "2025-10-21T10:15:00",
            }
        }


class UpdateProcessingStatus(BaseModel):
    """Model for updating update event processing status."""

    status: UpdateStatus = Field(..., description="New processing status")
    processing_result: dict[str, Any] | None = Field(
        default=None, description="Optional result from processing"
    )
    error_message: str | None = Field(default=None, description="Optional error message if failed")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "completed",
                "processing_result": {"diff_generated": True},
                "error_message": None,
            }
        }
