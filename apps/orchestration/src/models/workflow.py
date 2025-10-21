from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class WorkflowStatus(str, Enum):
    """Workflow execution status."""

    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class WorkflowRunRequest(BaseModel):
    """Request model for creating a workflow run."""

    program_id: str = Field(..., description="ID of the program being processed")
    source: str = Field(..., description="Source of the program (e.g., 'data_inclusion')")
    initial_stage: str = Field(default="ingestion", description="Starting stage of the workflow")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Optional metadata about the workflow"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "program_id": "prog_123",
                "source": "data_inclusion",
                "initial_stage": "ingestion",
                "metadata": {"batch_id": "batch_001"},
            }
        }


class WorkflowRunResponse(BaseModel):
    """Response model for a workflow run."""

    id: str = Field(..., description="Unique workflow run ID")
    program_id: str = Field(..., description="ID of the program being processed")
    source: str = Field(..., description="Source of the program")
    current_stage: str = Field(..., description="Current processing stage")
    status: WorkflowStatus = Field(..., description="Current workflow status")
    metadata: dict[str, Any] = Field(..., description="Workflow metadata")
    created_at: datetime = Field(..., description="Workflow creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    error_message: str | None = Field(default=None, description="Error message if workflow failed")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "wf_abc123",
                "program_id": "prog_123",
                "source": "data_inclusion",
                "current_stage": "enrichment",
                "status": "running",
                "metadata": {"batch_id": "batch_001"},
                "created_at": "2025-10-21T10:00:00",
                "updated_at": "2025-10-21T10:05:00",
                "error_message": None,
            }
        }


class WorkflowStatusUpdate(BaseModel):
    """Model for updating workflow status."""

    status: WorkflowStatus = Field(..., description="New workflow status")
    current_stage: str | None = Field(default=None, description="Optional new current stage")
    error_message: str | None = Field(default=None, description="Optional error message if failed")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "completed",
                "current_stage": "publication",
                "error_message": None,
            }
        }
