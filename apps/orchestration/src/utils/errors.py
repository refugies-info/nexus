from enum import Enum
from typing import Any

from pydantic import BaseModel


class ErrorCode(str, Enum):
    """Application error codes."""

    # Validation errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_REQUEST = "INVALID_REQUEST"

    # Database errors
    DATABASE_ERROR = "DATABASE_ERROR"
    RECORD_NOT_FOUND = "RECORD_NOT_FOUND"
    DUPLICATE_RECORD = "DUPLICATE_RECORD"

    # Pipeline errors
    PIPELINE_ERROR = "PIPELINE_ERROR"
    STAGE_FAILED = "STAGE_FAILED"
    WORKFLOW_NOT_FOUND = "WORKFLOW_NOT_FOUND"

    # Update errors
    UPDATE_ERROR = "UPDATE_ERROR"
    DIFF_GENERATION_ERROR = "DIFF_GENERATION_ERROR"

    # External API errors
    EXTERNAL_API_ERROR = "EXTERNAL_API_ERROR"
    DATA_INCLUSION_ERROR = "DATA_INCLUSION_ERROR"
    CARIF_OREF_ERROR = "CARIF_OREF_ERROR"

    # Internal errors
    INTERNAL_ERROR = "INTERNAL_ERROR"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error_code: ErrorCode
    message: str
    details: dict[str, Any] | None = None
    request_id: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "error_code": "RECORD_NOT_FOUND",
                "message": "Workflow not found",
                "details": {"workflow_id": "wf_123"},
                "request_id": "req_abc123",
            }
        }


class ApplicationError(Exception):
    """Base application error."""

    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        details: dict[str, Any] | None = None,
        status_code: int = 500,
    ):
        """Initialize application exception.

        Args:
            error_code: Error code enum
            message: Error message
            details: Optional error details
            status_code: HTTP status code
        """
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)

    def to_response(self, request_id: str | None = None) -> ErrorResponse:
        """Convert exception to error response.

        Args:
            request_id: Optional request ID for tracking

        Returns:
            ErrorResponse instance
        """
        return ErrorResponse(
            error_code=self.error_code,
            message=self.message,
            details=self.details if self.details else None,
            request_id=request_id,
        )


class ValidationError(ApplicationError):
    """Validation error exception."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            error_code=ErrorCode.VALIDATION_ERROR,
            message=message,
            details=details,
            status_code=400,
        )


class RecordNotFoundError(ApplicationError):
    """Record not found exception."""

    def __init__(self, record_type: str, record_id: str):
        super().__init__(
            error_code=ErrorCode.RECORD_NOT_FOUND,
            message=f"{record_type} not found",
            details={"record_type": record_type, "record_id": record_id},
            status_code=404,
        )


class DuplicateRecordError(ApplicationError):
    """Duplicate record exception."""

    def __init__(self, record_type: str, details: dict[str, Any] | None = None):
        super().__init__(
            error_code=ErrorCode.DUPLICATE_RECORD,
            message=f"Duplicate {record_type}",
            details=details,
            status_code=409,
        )


class DatabaseError(ApplicationError):
    """Database operation error exception."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            error_code=ErrorCode.DATABASE_ERROR,
            message=message,
            details=details,
            status_code=500,
        )


class PipelineError(ApplicationError):
    """Pipeline execution error exception."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            error_code=ErrorCode.PIPELINE_ERROR,
            message=message,
            details=details,
            status_code=500,
        )


class StageFailedError(ApplicationError):
    """Stage execution failed exception."""

    def __init__(self, stage_name: str, error_message: str, details: dict[str, Any] | None = None):
        super().__init__(
            error_code=ErrorCode.STAGE_FAILED,
            message=f"Stage '{stage_name}' failed: {error_message}",
            details=details or {"stage_name": stage_name},
            status_code=500,
        )


class UpdateError(ApplicationError):
    """Update processing error exception."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            error_code=ErrorCode.UPDATE_ERROR,
            message=message,
            details=details,
            status_code=500,
        )


class DiffGenerationError(ApplicationError):
    """Diff generation error exception."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            error_code=ErrorCode.DIFF_GENERATION_ERROR,
            message=message,
            details=details,
            status_code=500,
        )


class ExternalAPIError(ApplicationError):
    """External API error exception."""

    def __init__(self, api_name: str, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            error_code=ErrorCode.EXTERNAL_API_ERROR,
            message=f"{api_name} error: {message}",
            details=details or {"api_name": api_name},
            status_code=502,
        )


class ConfigurationError(ApplicationError):
    """Configuration error exception."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            error_code=ErrorCode.CONFIGURATION_ERROR,
            message=message,
            details=details,
            status_code=500,
        )


def format_error_response(
    error: Exception, request_id: str | None = None
) -> tuple[ErrorResponse, int]:
    """Format an exception into an error response.

    Args:
        error: Exception to format
        request_id: Optional request ID for tracking

    Returns:
        Tuple of (ErrorResponse, HTTP status code)
    """
    if isinstance(error, ApplicationError):
        return error.to_response(request_id), error.status_code
    else:
        # Generic internal error
        app_error = ApplicationError(
            error_code=ErrorCode.INTERNAL_ERROR,
            message=str(error),
            status_code=500,
        )
        return app_error.to_response(request_id), 500
