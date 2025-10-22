"""Retry logic with exponential backoff using tenacity."""

import logging
from collections.abc import Callable
from typing import Any, TypeVar

from tenacity import (
    RetryError,
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])

# Retry configuration
INITIAL_DELAY_SECONDS = 1  # 1 second
MAX_DELAY_SECONDS = 300  # 5 minutes
MAX_RETRIES = 10


def retry_with_backoff(
    func: Callable[..., Any],
    *args: Any,
    max_retries: int = MAX_RETRIES,
    initial_delay: int = INITIAL_DELAY_SECONDS,
    max_delay: int = MAX_DELAY_SECONDS,
    exception_types: tuple[type[Exception], ...] = (Exception,),
    **kwargs: Any,
) -> Any:
    """Execute a function with exponential backoff retry logic.

    Args:
        func: Function to execute with retries
        *args: Positional arguments for the function
        max_retries: Maximum number of retry attempts (default: 10)
        initial_delay: Initial delay in seconds (default: 1)
        max_delay: Maximum delay in seconds (default: 300)
        exception_types: Tuple of exception types to retry on (default: all)
        **kwargs: Keyword arguments for the function

    Returns:
        Result from the function

    Raises:
        RetryError: If all retries are exhausted
        Original exception: If function succeeds after retries
    """
    try:
        for attempt in Retrying(
            retry=retry_if_exception_type(exception_types),
            stop=stop_after_attempt(max_retries),
            wait=wait_exponential(
                multiplier=1,
                min=initial_delay,
                max=max_delay,
            ),
        ):
            with attempt:
                logger.debug(
                    "Executing function with retry",
                    extra={
                        "function": func.__name__,
                        "attempt": attempt.retry_state.attempt_number,
                        "max_retries": max_retries,
                    },
                )
                return func(*args, **kwargs)
    except RetryError as e:
        logger.error(
            "Function failed after all retries",
            extra={
                "function": func.__name__,
                "max_retries": max_retries,
                "error": str(e.last_attempt.exception()),
            },
        )
        raise


async def async_retry_with_backoff(
    func: Callable[..., Any],
    *args: Any,
    max_retries: int = MAX_RETRIES,
    initial_delay: int = INITIAL_DELAY_SECONDS,
    max_delay: int = MAX_DELAY_SECONDS,
    exception_types: tuple[type[Exception], ...] = (Exception,),
    **kwargs: Any,
) -> Any:
    """Execute an async function with exponential backoff retry logic.

    Args:
        func: Async function to execute with retries
        *args: Positional arguments for the function
        max_retries: Maximum number of retry attempts (default: 10)
        initial_delay: Initial delay in seconds (default: 1)
        max_delay: Maximum delay in seconds (default: 300)
        exception_types: Tuple of exception types to retry on (default: all)
        **kwargs: Keyword arguments for the function

    Returns:
        Result from the async function

    Raises:
        RetryError: If all retries are exhausted
        Original exception: If function succeeds after retries
    """
    try:
        for attempt in Retrying(
            retry=retry_if_exception_type(exception_types),
            stop=stop_after_attempt(max_retries),
            wait=wait_exponential(
                multiplier=1,
                min=initial_delay,
                max=max_delay,
            ),
        ):
            with attempt:
                logger.debug(
                    "Executing async function with retry",
                    extra={
                        "function": func.__name__,
                        "attempt": attempt.retry_state.attempt_number,
                        "max_retries": max_retries,
                    },
                )
                return await func(*args, **kwargs)
    except RetryError as e:
        logger.error(
            "Async function failed after all retries",
            extra={
                "function": func.__name__,
                "max_retries": max_retries,
                "error": str(e.last_attempt.exception()),
            },
        )
        raise


def create_retry_decorator(
    max_retries: int = MAX_RETRIES,
    initial_delay: int = INITIAL_DELAY_SECONDS,
    max_delay: int = MAX_DELAY_SECONDS,
    exception_types: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[F], F]:
    """Create a retry decorator with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts (default: 10)
        initial_delay: Initial delay in seconds (default: 1)
        max_delay: Maximum delay in seconds (default: 300)
        exception_types: Tuple of exception types to retry on (default: all)

    Returns:
        Decorator function

    Example:
        @create_retry_decorator(max_retries=5)
        def my_function():
            # Function that might fail
            pass
    """

    def decorator(func: F) -> F:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return retry_with_backoff(
                func,
                *args,
                max_retries=max_retries,
                initial_delay=initial_delay,
                max_delay=max_delay,
                exception_types=exception_types,
                **kwargs,
            )

        return wrapper  # type: ignore

    return decorator


def create_async_retry_decorator(
    max_retries: int = MAX_RETRIES,
    initial_delay: int = INITIAL_DELAY_SECONDS,
    max_delay: int = MAX_DELAY_SECONDS,
    exception_types: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[F], F]:
    """Create an async retry decorator with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts (default: 10)
        initial_delay: Initial delay in seconds (default: 1)
        max_delay: Maximum delay in seconds (default: 300)
        exception_types: Tuple of exception types to retry on (default: all)

    Returns:
        Async decorator function

    Example:
        @create_async_retry_decorator(max_retries=5)
        async def my_async_function():
            # Async function that might fail
            pass
    """

    def decorator(func: F) -> F:
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await async_retry_with_backoff(
                func,
                *args,
                max_retries=max_retries,
                initial_delay=initial_delay,
                max_delay=max_delay,
                exception_types=exception_types,
                **kwargs,
            )

        return wrapper  # type: ignore

    return decorator
