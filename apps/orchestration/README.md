# Nexus Orchestration Service

FastAPI-based orchestration service for the Nexus AI pipeline. Manages workflow execution, state management, and data processing through multiple pipeline stages.

## Architecture

- **Framework**: FastAPI with async/await support
- **Database**: Supabase (PostgreSQL)
- **Orchestration**: n8n (workflow engine) + Python services (business logic)
- **Logging**: Structlog with JSON output
- **Testing**: pytest with in-memory SQLite for unit tests

## Quick Start

### Installation

```bash
uv sync --all-extras
```

### Running Tests

```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v -m unit

# With coverage
pytest tests/ --cov=src --cov-report=html
```

### Running the Service

```bash
uvicorn apps.orchestration.src.main:app --reload
```

## Project Structure

```
apps/orchestration/
├── src/
│   ├── api/              # FastAPI routes
│   ├── services/         # Business logic
│   ├── models/           # Pydantic models
│   ├── db/               # Database layer
│   │   ├── client.py     # Supabase client
│   │   └── repositories/ # Repository pattern
│   ├── utils/            # Utilities
│   ├── main.py           # Application entry point
│   └── config.py         # Configuration
├── tests/
│   ├── unit/             # Unit tests
│   ├── integration/       # Integration tests
│   ├── contract/         # API contract tests
│   ├── conftest.py       # Pytest fixtures
│   └── README.md         # Testing guide
├── pyproject.toml        # Project metadata
└── pytest.ini            # Pytest configuration
```

## Development

### Code Quality

```bash
# Format code
ruff format src/ tests/

# Check linting
ruff check src/ tests/

# Type checking
mypy src/
```

### Adding Tests

See `tests/README.md` for comprehensive testing guidelines.

## Key Features

- **Workflow Management**: Create, track, and manage pipeline execution workflows
- **Stage Execution**: Execute and monitor individual pipeline stages
- **Information Sheets**: Progressive data enhancement through pipeline stages
- **Update Handling**: Smart catch-up for data updates with diff review
- **Policy Validation**: Editorial policy compliance checking
- **Reconciliation**: Data reconciliation with Carif-Oref sources

## Functional Programming Approach

The orchestration service uses a functional programming paradigm for better:
- **Testability**: Pure functions are easier to test in isolation
- **Composition**: Functions can be combined more flexibly
- **Maintainability**: Explicit dependencies make code easier to reason about

### Key Functional Modules
- `workflow_functions.py`: Workflow lifecycle operations
- `stage_functions.py`: Stage execution management
- `stage_executor_functions.py`: Pipeline stage coordination
- `reconciliation_functions.py`: Data reconciliation logic

### Usage Example
```python
from services.workflow_functions import start_workflow
from services.stage_functions import execute_stage
from db.repositories.workflow import get_workflow_repository

# Initialize dependencies
workflow_repo = get_workflow_repository()

# Use functional version
workflow = await start_workflow(workflow_repo, request)
```

### Deprecated Class-Based Modules
The following class-based modules are deprecated:
- `workflow_service.py`
- `stage_service.py`
- `reconciliation_service.py`

New code should use the functional versions instead.

## Environment Variables

See `.env.example` in the project root for required environment variables.

## Documentation

- [Testing Guide](tests/README.md)
- [API Documentation](http://localhost:8000/docs) (when running)
- [Pipeline Specification](../../specs/002-orchestration-decision/)

## License

MIT
