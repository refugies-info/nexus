# Contributing to Nexus

Welcome to the Nexus AI Pipeline project! This guide will help you set up your development environment and understand our workflows.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.12+**: [Download](https://www.python.org/downloads/)
- **Node.js 22+**: [Download](https://nodejs.org/)
- **uv**: Python package manager
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **pnpm**: Node.js package manager
  ```bash
  npm install -g pnpm
  ```
- **just**: Command runner
  - macOS: `brew install just`
  - Linux: `cargo install just` or download from [releases](https://github.com/casey/just#installation)
  - Windows: `cargo install just` or `scoop install just`

## Quick Setup

```bash
# Clone the repository
git clone git@github.com:refugies-info/nexus.git
cd nexus

# Install everything (dependencies + pre-commit hooks)
just install

# Verify installation
just lint    # Should complete without errors
just test    # Should run (may have no tests initially)
```

## Development Workflow

### 1. Create a Feature Branch

Use the speckit workflow to create a feature branch and specification:

```bash
/speckit.specify "Your feature description"
```

This creates a numbered branch (e.g., `002-feature-name`) and initializes the specification.

### 2. Make Changes

Edit code in the appropriate library:

```bash
# Example: Working on ingestion
cd libs/ingestion/
# Edit files in src/
# Add tests in tests/
```

### 3. Test-Driven Development (TDD)

**TDD is mandatory** per the Nexus Constitution:

```bash
# 1. Write tests first (they should fail)
uv run pytest libs/ingestion/tests/unit/test_new_feature.py

# 2. Implement the feature

# 3. Tests should now pass
uv run pytest libs/ingestion/tests/unit/test_new_feature.py

# 4. Run all tests for the library
just test-lib ingestion
```

### 4. Lint and Format

```bash
# Format code
just format

# Check linting
just lint
```

### 5. Commit

Pre-commit hooks will automatically run when you commit:

```bash
git add .
git commit -m "feat(ingestion): add new feature"
```

If hooks fail, fix the issues and commit again.

## Project Structure

The Nexus monorepo uses an **independent library architecture**:

```
nexus/
├── libs/                  # Python packages (one per pipeline stage)
│   ├── common/            # Shared utilities
│   ├── ingestion/         # Data ingestion
│   ├── reconciliation/    # Data reconciliation
│   ├── enrichment/        # Data enrichment
│   ├── langage_clair/     # AI plain language transformation
│   ├── translation/       # Multilingual translation
│   ├── validation/        # Quality validation
│   └── publication/       # Publication to Réfugiés.info
├── packages/              # Node.js packages
│   └── tooling/           # Build scripts, dev tools
└── notebooks/             # Jupyter notebooks
```

Each library in `libs/` has:
- `src/` - Source code
- `tests/contract/` - Contract tests
- `tests/integration/` - Integration tests
- `tests/unit/` - Unit tests
- `pyproject.toml` - Package configuration

## Working with Python Libraries

### Adding Dependencies

Add dependencies to the specific library's `pyproject.toml`:

```toml
# libs/ingestion/pyproject.toml
[project]
dependencies = [
    "httpx>=0.27.0",
    "pydantic>=2.0.0",
]
```

Then sync:

```bash
uv sync
```

### Importing Across Libraries

Libraries can import from each other:

```python
# In libs/ingestion/src/nexus/ingestion/main.py
from nexus.common.utils import some_utility
```

### Running a Library

```bash
# Example: Run ingestion (once implemented)
uv run python -m nexus.ingestion
```

## Working with Notebooks

Notebooks are for exploratory work only:

```bash
# Start Jupyter Lab
jupyter lab notebooks/

# Create a new notebook
# Work on your analysis
# Commit (outputs are automatically stripped by pre-commit hooks)
```

**Important**: Never commit notebook outputs. The `nbstripout` pre-commit hook handles this automatically.

## Code Quality Standards

### Python

- **Linting**: ruff (replaces flake8, black, isort)
- **Type Checking**: mypy
- **Testing**: pytest with contract/integration/unit organization
- **Line Length**: 100 characters
- **Python Version**: 3.12+

### Node.js/TypeScript

- **Linting & Formatting**: biome
- **Line Length**: 100 characters
- **Node Version**: 22+

## Common Commands

```bash
# List all available commands
just

# Run linters (Python + Node.js)
just lint

# Format all code
just format

# Run all tests
just test

# Run tests for specific library
just test-lib ingestion

# Type check Python code
uv run mypy libs/

# Run Jupyter notebooks
jupyter lab notebooks/
```

## Troubleshooting

### "uv not found"

Install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### "pnpm not found"

Install pnpm:
```bash
npm install -g pnpm
```

### "just not found"

Install just:
- macOS: `brew install just`
- Linux/Windows: See [installation guide](https://github.com/casey/just#installation)

### Pre-commit hooks failing

Run the hooks manually to see detailed errors:
```bash
uv run pre-commit run --all-files
```

### Import errors between libraries

Make sure you've run `uv sync` after adding dependencies:
```bash
uv sync
```

### Tests not discovered

Ensure your test files follow the naming convention:
- Files: `test_*.py` or `*_test.py`
- Classes: `Test*`
- Functions: `test_*`

## Constitutional Principles

Please review the [Nexus Constitution](.specify/memory/constitution.md) to understand our core principles:

1. **Data Quality First**: Prioritize data accuracy and completeness
2. **Pipeline Modularity**: Each stage is independent and testable
3. **Multilingual by Design**: Support French, English, Arabic, Ukrainian, Russian, Dari, Pashto
4. **Editorial Compliance**: Respect Réfugiés.info editorial guidelines
5. **Integration Independence**: Minimize coupling to external systems
6. **Observability & Traceability**: Track all data transformations
7. **Incremental Delivery**: Ship working features regularly
8. **Technology Foundation**: Python 3.12+, Node.js 22+, polyglot monorepo
9. **User-Centered Development**: Always consider end-user impact (NON-NEGOTIABLE)
10. **Notebook Governance**: Notebooks for exploration only, never in production
11. **Langage Clair**: AI-powered plain language transformation (NON-NEGOTIABLE)
12. **Culturally-Aware Translation**: Context-aware multilingual translation (NON-NEGOTIABLE)
13. **TDD Compliance**: Write tests before implementation (NON-NEGOTIABLE)
14. **GDPR Compliance**: Protect personal data and privacy (NON-NEGOTIABLE)

## Getting Help

- **Documentation**: See `docs/` directory
- **Constitution**: `.specify/memory/constitution.md` - Project principles
- **Quickstart**: `specs/001-monorepo-setup/quickstart.md` - Quick reference
- **Issues**: [GitHub Issues](https://github.com/refugies-info/nexus/issues)

## Next Steps

1. Read the [Constitution](.specify/memory/constitution.md) to understand project principles
2. Review the [Quickstart Guide](specs/001-monorepo-setup/quickstart.md) for quick reference
3. Check existing specifications in `specs/` for examples
4. Start with a small feature to get familiar with the codebase

Happy coding! 🚀
