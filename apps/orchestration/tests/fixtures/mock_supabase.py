"""Mock Supabase client for testing."""

from typing import Any


class MockSupabaseQueryBuilder:
    """Mock Supabase query builder for method chaining."""

    def __init__(self, data: dict[str, Any] | None = None):
        """Initialize query builder.

        Args:
            data: Data to return from execute()
        """
        self.data = data or {}
        self.filters = {}

    def insert(self, data: dict[str, Any]) -> "MockSupabaseQueryBuilder":
        """Mock insert operation."""
        self.data = data
        return self

    def select(self, *args: str, **kwargs: Any) -> "MockSupabaseQueryBuilder":
        """Mock select operation."""
        return self

    def eq(self, field: str, value: Any) -> "MockSupabaseQueryBuilder":
        """Mock equality filter."""
        self.filters[field] = value
        return self

    def update(self, data: dict[str, Any]) -> "MockSupabaseQueryBuilder":
        """Mock update operation."""
        self.data = data
        return self

    def delete(self) -> "MockSupabaseQueryBuilder":
        """Mock delete operation."""
        return self

    def range(self, start: int, end: int) -> "MockSupabaseQueryBuilder":
        """Mock range operation."""
        return self

    def limit(self, count: int) -> "MockSupabaseQueryBuilder":
        """Mock limit operation."""
        return self

    async def execute(self) -> "MockSupabaseResponse":
        """Mock execute operation."""
        return MockSupabaseResponse([self.data] if self.data else [])


class MockSupabaseResponse:
    """Mock Supabase response object."""

    def __init__(self, data: list[dict[str, Any]] | None = None):
        """Initialize response.

        Args:
            data: Response data
        """
        self.data = data or []
        self.count = len(self.data)


class MockSupabaseClient:
    """Mock Supabase client for testing."""

    def __init__(self, session: Any | None = None):
        """Initialize mock client.

        Args:
            session: Optional SQLAlchemy session (for future integration)
        """
        self.session = session

    def table(self, table_name: str) -> MockSupabaseQueryBuilder:
        """Get a table reference.

        Args:
            table_name: Name of the table

        Returns:
            Query builder for method chaining
        """
        return MockSupabaseQueryBuilder()
