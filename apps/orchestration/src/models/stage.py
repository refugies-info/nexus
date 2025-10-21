from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class StageStatus(str, Enum):
    """Stage execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class StageExecutionRequest(BaseModel):
    """Request model for creating a stage execution."""

    workflow_id: str = Field(..., description="ID of the parent workflow")
    stage_name: str = Field(..., description="Name of the stage")
    program_id: str = Field(..., description="ID of the program being processed")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Optional metadata about the stage execution"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "workflow_id": "wf_abc123",
                "stage_name": "enrichment",
                "program_id": "prog_123",
                "metadata": {"enrichment_model": "v2.1"},
            }
        }


class StageExecutionResponse(BaseModel):
    """Response model for a stage execution."""

    id: str = Field(..., description="Unique stage execution ID")
    workflow_id: str = Field(..., description="ID of the parent workflow")
    stage_name: str = Field(..., description="Name of the stage")
    program_id: str = Field(..., description="ID of the program being processed")
    status: StageStatus = Field(..., description="Current stage status")
    attempt: int = Field(..., description="Current attempt number")
    result: dict[str, Any] | None = Field(
        default=None, description="Result data from stage execution"
    )
    error_message: str | None = Field(default=None, description="Error message if stage failed")
    metadata: dict[str, Any] = Field(..., description="Stage execution metadata")
    created_at: datetime = Field(..., description="Stage creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "stage_xyz789",
                "workflow_id": "wf_abc123",
                "stage_name": "enrichment",
                "program_id": "prog_123",
                "status": "completed",
                "attempt": 1,
                "result": {"enriched_fields": 15},
                "error_message": None,
                "metadata": {"enrichment_model": "v2.1"},
                "created_at": "2025-10-21T10:01:00",
                "updated_at": "2025-10-21T10:02:00",
            }
        }


class StageStatusUpdate(BaseModel):
    """Model for updating stage execution status."""

    status: StageStatus = Field(..., description="New stage status")
    result: dict[str, Any] | None = Field(
        default=None, description="Optional result data from stage"
    )
    error_message: str | None = Field(default=None, description="Optional error message if failed")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "completed",
                "result": {"enriched_fields": 15},
                "error_message": None,
            }
        }
