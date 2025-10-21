"""Pytest configuration and shared fixtures for orchestration tests."""

import asyncio
from collections.abc import AsyncGenerator
from typing import Any

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from .fixtures.mock_supabase import MockSupabaseClient


@pytest_asyncio.fixture
async def db_engine():
    """Create an in-memory SQLite database for testing.

    Uses SQLite with async support for fast, isolated tests.
    In production, this would be PostgreSQL via Supabase.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        echo=False,
    )

    # Create tables from schema
    async with engine.begin() as conn:
        await conn.run_sync(_create_test_schema)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session for each test."""
    async_session = AsyncSession(db_engine, expire_on_commit=False)

    yield async_session

    await async_session.close()


def _create_test_schema(conn):
    """Create test database schema using raw SQL.

    Simplified schema for testing - SQLite doesn't support all PostgreSQL features.
    """
    # workflow_runs table
    conn.execute(
        text("""
        CREATE TABLE IF NOT EXISTS workflow_runs (
            id TEXT PRIMARY KEY,
            program_id TEXT NOT NULL UNIQUE,
            current_stage TEXT NOT NULL,
            status TEXT NOT NULL,
            source TEXT,
            metadata TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            completed_at TEXT,
            error_message TEXT
        )
    """)
    )

    # stage_executions table
    conn.execute(
        text("""
        CREATE TABLE IF NOT EXISTS stage_executions (
            id TEXT PRIMARY KEY,
            workflow_run_id TEXT NOT NULL,
            stage_name TEXT NOT NULL,
            status TEXT NOT NULL,
            retry_count INTEGER DEFAULT 0,
            input_data TEXT,
            output_data TEXT,
            execution_metadata TEXT,
            created_at TEXT NOT NULL,
            completed_at TEXT,
            error_message TEXT,
            FOREIGN KEY (workflow_run_id) REFERENCES workflow_runs(id)
        )
    """)
    )

    # information_sheets table
    conn.execute(
        text("""
        CREATE TABLE IF NOT EXISTS information_sheets (
            id TEXT PRIMARY KEY,
            program_id TEXT NOT NULL UNIQUE,
            refugies_info_id TEXT,
            current_stage TEXT NOT NULL,
            status TEXT NOT NULL,
            ingested_data TEXT,
            reconciled_data TEXT,
            enriched_data TEXT,
            langage_clair_data TEXT,
            translated_data TEXT,
            validated_data TEXT,
            published_data TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    )

    # update_events table
    conn.execute(
        text("""
        CREATE TABLE IF NOT EXISTS update_events (
            id TEXT PRIMARY KEY,
            program_id TEXT NOT NULL,
            original_checksum TEXT NOT NULL,
            updated_checksum TEXT NOT NULL,
            original_stage TEXT NOT NULL,
            update_strategy TEXT NOT NULL,
            processing_status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            completed_at TEXT
        )
    """)
    )

    # update_diffs table
    conn.execute(
        text("""
        CREATE TABLE IF NOT EXISTS update_diffs (
            id TEXT PRIMARY KEY,
            program_id TEXT NOT NULL,
            update_event_id TEXT NOT NULL,
            original_data TEXT,
            updated_data TEXT,
            diff_content TEXT,
            risk_score REAL NOT NULL,
            priority TEXT NOT NULL,
            review_status TEXT NOT NULL,
            reviewed_by TEXT,
            reviewed_at TEXT,
            approval_type TEXT,
            approval_reason TEXT,
            approved_at TEXT,
            approved_by TEXT,
            approval_metadata TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (update_event_id) REFERENCES update_events(id)
        )
    """)
    )

    # policy_validation_decisions table
    conn.execute(
        text("""
        CREATE TABLE IF NOT EXISTS policy_validation_decisions (
            id TEXT PRIMARY KEY,
            program_id TEXT NOT NULL,
            policy_rule_id TEXT NOT NULL,
            decision TEXT NOT NULL,
            reason TEXT,
            audit_trail TEXT,
            created_at TEXT NOT NULL,
            created_by TEXT,
            FOREIGN KEY (program_id) REFERENCES information_sheets(program_id)
        )
    """)
    )

    # carif_oref_reconciliation_status table
    conn.execute(
        text("""
        CREATE TABLE IF NOT EXISTS carif_oref_reconciliation_status (
            id TEXT PRIMARY KEY,
            program_id TEXT NOT NULL UNIQUE,
            reconciliation_status TEXT NOT NULL,
            carif_oref_data TEXT,
            conflicts_detected TEXT,
            last_fetch_at TEXT,
            last_successful_fetch_at TEXT,
            fetch_error_message TEXT,
            FOREIGN KEY (program_id) REFERENCES information_sheets(program_id)
        )
    """)
    )

    conn.commit()


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_workflow_data() -> dict[str, Any]:
    """Sample workflow run data for testing."""
    return {
        "program_id": "prog_001",
        "source": "data_inclusion",
        "initial_stage": "ingestion",
        "metadata": {"source_url": "https://example.com"},
    }


@pytest.fixture
def sample_information_sheet_data() -> dict[str, Any]:
    """Sample information sheet data for testing."""
    return {
        "program_id": "prog_001",
        "current_stage": "ingestion",
        "status": "draft",
        "ingested_data": {
            "name": "Test Program",
            "description": "A test program",
        },
    }


@pytest.fixture
def sample_update_event_data() -> dict[str, Any]:
    """Sample update event data for testing."""
    return {
        "program_id": "prog_001",
        "original_checksum": "abc123",
        "updated_checksum": "def456",
        "original_stage": "enrichment",
        "update_strategy": "smart_catchup",
    }


@pytest.fixture
def mock_supabase_client(db_session: AsyncSession) -> MockSupabaseClient:
    """Create a mock Supabase client for testing."""
    return MockSupabaseClient(db_session)


class MockPolicyRepository:
    """Mock policy repository for testing."""

    async def create_policy_decision(
        self,
        program_id: str,
        decision: str,
        reason: str,
        violations: list[dict],
    ) -> dict:
        """Mock create policy decision."""
        return {
            "program_id": program_id,
            "decision": decision,
            "reason": reason,
            "violations": violations,
        }


@pytest.fixture
def mock_policy_repo() -> MockPolicyRepository:
    """Create a mock policy repository for testing."""
    return MockPolicyRepository()


class MockReconciliationRepository:
    """Mock reconciliation repository for testing."""

    def __init__(self, csv_data: list[dict] | None = None):
        """Initialize with optional CSV data."""
        self.csv_data = csv_data or []

    async def get_latest_csv(self) -> list[dict]:
        """Mock get latest CSV."""
        return self.csv_data

    async def create_reconciliation_status(
        self,
        program_id: str,
        status: str,
        carif_oref_data: dict | None = None,
        conflicts: list[dict] | None = None,
    ) -> dict:
        """Mock create reconciliation status."""
        return {
            "program_id": program_id,
            "status": status,
            "carif_oref_data": carif_oref_data,
            "conflicts": conflicts or [],
        }


@pytest.fixture
def mock_reconciliation_repo() -> MockReconciliationRepository:
    """Create a mock reconciliation repository for testing."""
    return MockReconciliationRepository()
