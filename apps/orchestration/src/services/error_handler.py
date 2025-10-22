"""Error handling for stage failures with retry logic and manual review routing."""

import logging
from typing import Any

from db.repositories.workflow import WorkflowRepository
from services.stage import (
    handle_stage_failure,
)
from utils.errors import PipelineError
from utils.retry import async_retry_with_backoff


logger = logging.getLogger(__name__)


class ErrorHandler:
    """Handles stage failures with retry logic and manual review routing."""

    def __init__(
        self,
        workflow_repo: WorkflowRepository,
        max_retries: int = 10,
        initial_delay: int = 1,
        max_delay: int = 300,
    ):
        """Initialize error handler.

        Args:
            workflow_repo: WorkflowRepository instance
            max_retries: Maximum retry attempts (default: 10)
            initial_delay: Initial retry delay in seconds (default: 1)
            max_delay: Maximum retry delay in seconds (default: 300)
        """
        self.workflow_repo = workflow_repo
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay

    async def handle_stage_failure(
        self,
        stage_id: str,
        workflow_id: str,
        error_message: str,
        attempt: int = 1,
    ) -> dict[str, Any]:
        """Handle a stage failure with retry logic.

        Args:
            stage_id: ID of the failed stage
            workflow_id: ID of the parent workflow
            error_message: Error message from the failure
            attempt: Current attempt number

        Returns:
            Dictionary with retry decision and status

        Raises:
            PipelineError: If error handling fails
        """
        try:
            logger.error(
                "Handling stage failure",
                extra={
                    "stage_id": stage_id,
                    "workflow_id": workflow_id,
                    "attempt": attempt,
                    "error": error_message,
                },
            )

            # Mark stage as failed
            await handle_stage_failure(stage_id, error_message)

            # Determine if we should retry
            should_retry = attempt < self.max_retries
            retry_decision = {
                "stage_id": stage_id,
                "workflow_id": workflow_id,
                "attempt": attempt,
                "max_retries": self.max_retries,
                "should_retry": should_retry,
                "error_message": error_message,
            }

            if should_retry:
                logger.info(
                    "Stage failure will be retried",
                    extra={
                        "stage_id": stage_id,
                        "attempt": attempt,
                        "next_attempt": attempt + 1,
                    },
                )
                retry_decision["action"] = "retry"
            else:
                logger.error(
                    "Max retries exceeded, routing to manual review",
                    extra={
                        "stage_id": stage_id,
                        "workflow_id": workflow_id,
                        "max_retries": self.max_retries,
                    },
                )
                retry_decision["action"] = "manual_review"
                await self._route_to_manual_review(workflow_id, error_message)

            return retry_decision
        except Exception as e:
            logger.error(
                "Failed to handle stage failure",
                extra={
                    "error": str(e),
                    "stage_id": stage_id,
                    "workflow_id": workflow_id,
                },
            )
            raise PipelineError(f"Failed to handle stage failure: {str(e)}") from e

    async def retry_stage_with_backoff(
        self,
        stage_id: str,
        stage_executor_func: Any,
        *args: Any,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Retry a stage execution with exponential backoff.

        Args:
            stage_id: ID of the stage to retry
            stage_executor_func: Async function to execute the stage
            *args: Positional arguments for the executor function
            **kwargs: Keyword arguments for the executor function

        Returns:
            Result from successful stage execution

        Raises:
            PipelineError: If all retries are exhausted
        """
        try:
            logger.info(
                "Retrying stage with exponential backoff",
                extra={
                    "stage_id": stage_id,
                    "max_retries": self.max_retries,
                },
            )

            result = await async_retry_with_backoff(
                stage_executor_func,
                *args,
                max_retries=self.max_retries,
                initial_delay=self.initial_delay,
                max_delay=self.max_delay,
                exception_types=(Exception,),
                **kwargs,
            )

            logger.info(
                "Stage retry succeeded",
                extra={"stage_id": stage_id},
            )

            return result
        except Exception as e:
            logger.error(
                "Stage retry failed after all attempts",
                extra={
                    "error": str(e),
                    "stage_id": stage_id,
                    "max_retries": self.max_retries,
                },
            )
            raise PipelineError(f"Stage retry failed: {str(e)}") from e

    async def _route_to_manual_review(
        self,
        workflow_id: str,
        error_message: str,
    ) -> None:
        """Route a failed workflow to manual review queue.

        Args:
            workflow_id: ID of the failed workflow
            error_message: Error message for context

        Raises:
            PipelineError: If routing fails
        """
        try:
            logger.info(
                "Routing workflow to manual review",
                extra={
                    "workflow_id": workflow_id,
                    "error": error_message,
                },
            )

            # Mark workflow as failed
            await self.workflow_repo.mark_workflow_failed(
                workflow_id,
                f"Manual review required: {error_message}",
            )

            logger.info(
                "Workflow routed to manual review",
                extra={"workflow_id": workflow_id},
            )
        except Exception as e:
            logger.error(
                "Failed to route workflow to manual review",
                extra={
                    "error": str(e),
                    "workflow_id": workflow_id,
                },
            )
            raise PipelineError(f"Failed to route to manual review: {str(e)}") from e

    async def handle_workflow_failure(
        self,
        workflow_id: str,
        error_message: str,
    ) -> None:
        """Handle a complete workflow failure.

        Args:
            workflow_id: ID of the failed workflow
            error_message: Error message describing the failure

        Raises:
            PipelineError: If handling fails
        """
        try:
            logger.error(
                "Handling workflow failure",
                extra={
                    "workflow_id": workflow_id,
                    "error": error_message,
                },
            )

            # Mark workflow as failed
            await self.workflow_repo.mark_workflow_failed(
                workflow_id,
                error_message,
            )

            # Route to manual review
            await self._route_to_manual_review(workflow_id, error_message)

            logger.error(
                "Workflow failure handled and routed to manual review",
                extra={"workflow_id": workflow_id},
            )
        except Exception as e:
            logger.error(
                "Failed to handle workflow failure",
                extra={
                    "error": str(e),
                    "workflow_id": workflow_id,
                },
            )
            raise PipelineError(f"Failed to handle workflow failure: {str(e)}") from e

    def get_error_handler_config(self) -> dict[str, Any]:
        """Get current error handler configuration.

        Returns:
            Dictionary with error handler settings
        """
        return {
            "max_retries": self.max_retries,
            "initial_delay_seconds": self.initial_delay,
            "max_delay_seconds": self.max_delay,
            "retry_strategy": "exponential_backoff",
        }
