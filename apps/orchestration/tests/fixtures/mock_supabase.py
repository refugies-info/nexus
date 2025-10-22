"""Mock Supabase client for testing."""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession


class MockSupabaseQueryBuilder:
    """Mock Supabase query builder for method chaining."""

    def __init__(self, session: AsyncSession | None = None, table_name: str | None = None):
        """Initialize query builder.

        Args:
            session: SQLAlchemy async session
            table_name: Name of the table
        """
        self.session = session
        self.table_name = table_name
        self.data = {}
        self.filters = {}
        self._operation = None

    def insert(self, data: dict[str, Any]) -> "MockSupabaseQueryBuilder":
        """Mock insert operation."""
        self._operation = "insert"
        self.data = data
        return self

    def select(self, *args: str, **kwargs: Any) -> "MockSupabaseQueryBuilder":
        """Mock select operation."""
        self._operation = "select"
        return self

    def eq(self, field: str, value: Any) -> "MockSupabaseQueryBuilder":
        """Mock equality filter."""
        self.filters[field] = value
        return self

    def update(self, data: dict[str, Any]) -> "MockSupabaseQueryBuilder":
        """Mock update operation."""
        self._operation = "update"
        self.data = data
        return self

    def delete(self) -> "MockSupabaseQueryBuilder":
        """Mock delete operation."""
        self._operation = "delete"
        return self

    def range(self, start: int, end: int) -> "MockSupabaseQueryBuilder":
        """Mock range operation."""
        self._range_start = start
        self._range_end = end
        return self

    def limit(self, count: int) -> "MockSupabaseQueryBuilder":
        """Mock limit operation."""
        self._limit = count
        return self

    def execute(self) -> "MockSupabaseResponse":
        """Mock execute operation - returns mock response with data.

        Note: This is a simplified mock that returns the input data.
        For real database operations, use the session directly.
        """
        if self._operation == "insert":
            return MockSupabaseResponse([self.data])
        elif self._operation == "select":
            # For select, return empty list (mock doesn't store data)
            return MockSupabaseResponse([])
        elif self._operation == "update":
            return MockSupabaseResponse([self.data])
        elif self._operation == "delete":
            return MockSupabaseResponse([])
        return MockSupabaseResponse([])


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
        return MockSupabaseQueryBuilder(self.session, table_name)
