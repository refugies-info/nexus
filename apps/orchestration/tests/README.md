# Orchestration Service Tests

## Test-Driven Development (TDD) Approach

This test suite follows TDD principles with comprehensive coverage of the repository layer using in-memory SQLite for fast, isolated testing.

## Test Structure

```
tests/
├── conftest.py                 # Shared fixtures and database setup
├── unit/
│   ├── test_workflow_repository.py
│   ├── test_stage_repository.py
│   ├── test_information_sheet_repository.py
│   ├── test_update_repository.py
│   └── test_diff_repository.py
├── integration/
│   └── (integration tests with real Supabase)
├── contract/
│   └── (API contract tests)
├── fixtures/
│   └── (test data factories)
└── benchmarks/
    └── (performance tests)
```

## Running Tests

### All tests
```bash
pytest tests/ -v
```

### Unit tests only
```bash
pytest tests/unit/ -v -m unit
```

### With coverage
```bash
pytest tests/ --cov=src --cov-report=html
```

### Specific test class
```bash
pytest tests/unit/test_workflow_repository.py::TestWorkflowRepositoryCreate -v
```

## Test Database

Tests use **SQLite in-memory** database for:
- **Speed**: No network latency, no container startup
- **Isolation**: Each test gets a fresh database
- **Simplicity**: No external dependencies
- **Reproducibility**: Deterministic test runs

The schema is created in `conftest.py` from SQL DDL matching the production PostgreSQL schema.

## Fixtures

### Database Fixtures
- `db_engine`: In-memory SQLite engine
- `db_session`: AsyncSession for database operations
- `event_loop`: Event loop for async tests

### Data Fixtures
- `sample_workflow_data`: Typical workflow run data
- `sample_information_sheet_data`: Information sheet data
- `sample_update_event_data`: Update event data

## Test Markers

```bash
@pytest.mark.unit          # Unit tests (default)
@pytest.mark.integration   # Integration tests (real Supabase)
@pytest.mark.contract      # API contract tests
@pytest.mark.slow          # Slow tests (benchmarks)
```

## Coverage Goals

- **Unit tests**: 90%+ coverage of repository layer
- **Integration tests**: Critical paths with real Supabase
- **Contract tests**: API endpoint validation

## Key Testing Patterns

### 1. Test Organization by Operation Type
```python
class TestWorkflowRepositoryCreate:
    """Tests for creating workflow runs."""
    async def test_create_workflow_run_with_minimal_data(self, ...):
        ...

class TestWorkflowRepositoryRead:
    """Tests for reading workflow runs."""
    async def test_get_workflow_run_by_id(self, ...):
        ...
```

### 2. Async Testing
```python
@pytest.mark.unit
async def test_something(self, workflow_repo: WorkflowRepository):
    result = await workflow_repo.create_workflow_run(...)
    assert result is not None
```

### 3. Exception Testing
```python
from sqlalchemy.exc import IntegrityError

with pytest.raises(IntegrityError):
    await workflow_repo.create_workflow_run(
        program_id=duplicate_id,
        source="data_inclusion",
    )
```

## Adding New Tests

1. **Create test file** in appropriate directory (`unit/`, `integration/`, etc.)
2. **Use fixtures** from `conftest.py` for database setup
3. **Follow naming convention**: `test_<operation>_<scenario>`
4. **Add docstrings** explaining what is being tested
5. **Mark with decorator**: `@pytest.mark.unit` or similar
6. **Run tests** before committing

Example:
```python
@pytest.mark.unit
class TestMyNewFeature:
    """Tests for my new feature."""

    async def test_happy_path(self, workflow_repo: WorkflowRepository):
        """Test the happy path."""
        result = await workflow_repo.my_new_method()
        assert result is not None

    async def test_error_case(self, workflow_repo: WorkflowRepository):
        """Test error handling."""
        with pytest.raises(ValueError):
            await workflow_repo.my_new_method(invalid_input)
```

## Continuous Integration

Tests are run on every commit via pre-commit hooks:
```bash
pytest tests/ --cov=src --cov-report=term-missing
```

Minimum coverage threshold: **80%**

## Debugging Tests

### Verbose output
```bash
pytest tests/unit/test_workflow_repository.py -vv
```

### Show print statements
```bash
pytest tests/unit/test_workflow_repository.py -s
```

### Drop into debugger on failure
```bash
pytest tests/unit/test_workflow_repository.py --pdb
```

### Run single test
```bash
pytest tests/unit/test_workflow_repository.py::TestWorkflowRepositoryCreate::test_create_workflow_run_with_minimal_data -v
```

## Notes

- Tests use `pytest-asyncio` for async/await support
- Database fixtures are function-scoped (fresh DB per test)
- Fixtures are defined in `conftest.py` for reusability
- All tests should be independent and order-agnostic
