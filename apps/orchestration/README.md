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

## Environment Variables

See `.env.example` in the project root for required environment variables.

## Documentation

- [Testing Guide](tests/README.md)
- [API Documentation](http://localhost:8000/docs) (when running)
- [Pipeline Specification](../../specs/002-orchestration-decision/)

## License

MIT
