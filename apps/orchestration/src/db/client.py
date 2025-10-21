import logging
from contextlib import asynccontextmanager

from supabase import Client, create_client
from supabase.lib.client_options import ClientOptions

logger = logging.getLogger(__name__)


class SupabaseClientWrapper:
    """Wrapper around Supabase client with connection pooling and error handling."""

    _instance: "SupabaseClientWrapper | None" = None
    _client: Client | None = None

    def __new__(cls) -> "SupabaseClientWrapper":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, url: str, key: str, pool_size: int = 10, pool_timeout: int = 30):
        """Initialize Supabase client with connection pooling.

        Args:
            url: Supabase project URL
            key: Supabase API key
            pool_size: Maximum number of connections in pool
            pool_timeout: Connection timeout in seconds
        """
        if self._client is None:
            try:
                options = ClientOptions(
                    postgrest_client_timeout=pool_timeout,
                    storage_client_timeout=pool_timeout,
                )
                self._client = create_client(url, key, options=options)
                logger.info(
                    "Supabase client initialized",
                    extra={
                        "url": url,
                        "pool_size": pool_size,
                        "pool_timeout": pool_timeout,
                    },
                )
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                raise

    @property
    def client(self) -> Client:
        """Get the Supabase client instance."""
        if self._client is None:
            raise RuntimeError("Supabase client not initialized")
        return self._client

    async def health_check(self) -> bool:
        """Check if Supabase connection is healthy.

        Returns:
            True if connection is healthy, False otherwise
        """
        try:
            self._client.table("information_sheets").select("id").limit(1).execute()
            logger.debug("Supabase health check passed")
            return True
        except Exception as e:
            logger.error(f"Supabase health check failed: {e}")
            return False

    @asynccontextmanager
    async def transaction(self):
        """Context manager for database transactions.

        Yields:
            Supabase client for use within transaction
        """
        try:
            yield self._client
            logger.debug("Transaction completed successfully")
        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            raise

    def close(self) -> None:
        """Close the Supabase client connection."""
        if self._client is not None:
            try:
                self._client = None
                logger.info("Supabase client closed")
            except Exception as e:
                logger.error(f"Error closing Supabase client: {e}")


def get_supabase_client(
    url: str, key: str, pool_size: int = 10, pool_timeout: int = 30
) -> SupabaseClientWrapper:
    """Get or create a Supabase client instance (singleton).

    Args:
        url: Supabase project URL
        key: Supabase API key
        pool_size: Maximum number of connections in pool
        pool_timeout: Connection timeout in seconds

    Returns:
        SupabaseClientWrapper instance
    """
    return SupabaseClientWrapper(url, key, pool_size, pool_timeout)
