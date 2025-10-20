# Quickstart: Nexus Monorepo Development

**Last Updated**: 2025-10-20
**For**: Developers setting up the Nexus monorepo for the first time

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

That's it! You're ready to develop.

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

## Development Workflow

### 1. Create a Feature Branch

```bash
# Use speckit to create feature branch and spec
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

### 3. Run Tests (TDD)

**Test-Driven Development is mandatory** per the constitution:

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

## Getting Help

- **Documentation**: See `docs/` directory
- **Constitution**: `.specify/memory/constitution.md` - Project principles
- **Contributing**: `CONTRIBUTING.md` - Development guidelines
- **Issues**: [GitHub Issues](https://github.com/refugies-info/nexus/issues)

## Next Steps

1. Read the [Constitution](.specify/memory/constitution.md) to understand project principles
2. Review the [Contributing Guide](../../CONTRIBUTING.md) for detailed workflows
3. Check existing specifications in `specs/` for examples
4. Start with a small feature to get familiar with the codebase

Happy coding! 🚀
