# Research: Polyglot Monorepo Setup

**Feature**: 001-monorepo-setup
**Date**: 2025-10-20
**Purpose**: Research tool configurations and best practices for Python/Node.js monorepo infrastructure

## Research Topics

### 1. uv Workspace Configuration

**Decision**: Use uv workspaces to manage multiple Python packages in the monorepo

**Rationale**:
- uv 0.4+ supports workspace management similar to Cargo workspaces
- Enables shared dependency resolution across all libs/ packages
- Faster than traditional pip/poetry for large monorepos
- Built-in support for editable installs across workspace members
- Aligns with Constitutional Principle VIII (Technology Foundation)

**Configuration Approach**:
```toml
# Root pyproject.toml
[tool.uv.workspace]
members = [
    "libs/common",
    "libs/ingestion",
    "libs/reconciliation",
    "libs/enrichment",
    "libs/langage_clair",
    "libs/translation",
    "libs/validation",
    "libs/publication",
]

[tool.uv]
dev-dependencies = [
    "ruff>=0.6.0",
    "pytest>=8.0.0",
    "mypy>=1.11.0",
    "pre-commit>=3.8.0",
    "nbstripout>=0.7.0",
]
```

**Alternatives Considered**:
- **Poetry workspaces**: Less mature, slower dependency resolution
- **pip + requirements.txt**: No workspace support, manual dependency management
- **Hatch**: Good alternative but uv is faster and simpler for our use case

---

### 2. pytest Configuration for Multi-Library Testing

**Decision**: Configure pytest at root level with test discovery across all libs/ packages

**Rationale**:
- Single `pytest` command can run tests across all libraries
- Supports test categorization (contract/integration/unit) via directory structure
- Can run tests for specific library: `pytest libs/ingestion/tests/`
- Enables test coverage reporting across entire monorepo

**Configuration Approach**:
```toml
# Root pyproject.toml
[tool.pytest.ini_options]
testpaths = ["libs"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-ra",
    "--strict-markers",
    "--strict-config",
    "--showlocals",
]
markers = [
    "contract: Contract tests validating API contracts",
    "integration: Integration tests across components",
    "unit: Unit tests for isolated functions",
]
```

**Alternatives Considered**:
- **Separate pytest configs per library**: More complex, harder to run all tests
- **tox**: Overkill for initial setup, can add later if needed

---

### 3. ruff Configuration for Monorepo

**Decision**: Single ruff configuration at root level applying to all Python code

**Rationale**:
- Consistent code style across all libraries
- Fast linting and formatting (10-100x faster than flake8/black)
- Replaces multiple tools (flake8, black, isort, pyupgrade)
- Built-in support for monorepo structures

**Configuration Approach**:
```toml
# Root pyproject.toml
[tool.ruff]
target-version = "py312"
line-length = 100
src = ["libs"]

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
]
ignore = []

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101"]  # Allow assert in tests
```

**Alternatives Considered**:
- **black + flake8 + isort**: Multiple tools, slower, more configuration
- **pylint**: Too strict and slow for initial setup

---

### 4. Pre-commit Hooks Configuration

**Decision**: Use pre-commit framework with ruff, nbstripout, and standard hooks

**Rationale**:
- Automated code quality enforcement before commits
- Prevents committing notebook outputs (security/privacy)
- Fast execution with ruff
- Easy to add more hooks later

**Configuration Approach**:
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/kynan/nbstripout
    rev: 0.7.1
    hooks:
      - id: nbstripout

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

**Alternatives Considered**:
- **Git hooks without pre-commit**: Manual setup, harder to share across team
- **CI-only checks**: Too late in the workflow, wastes CI time

---

### 5. justfile Command Runner Configuration

**Decision**: Use just for common development commands with fail-fast error handling

**Rationale**:
- Cross-platform (works on macOS, Linux, Windows)
- Simple syntax, easier than Makefiles
- Built-in error handling and command chaining
- Self-documenting with `just` command listing all recipes

**Configuration Approach**:
```justfile
# justfile
# List all available commands
default:
    @just --list

# Install all dependencies and setup development environment
install:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "Installing dependencies..."
    command -v uv >/dev/null 2>&1 || { echo "Error: uv not found. Install: curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }
    command -v pnpm >/dev/null 2>&1 || { echo "Error: pnpm not found. Install: npm install -g pnpm"; exit 1; }
    uv sync
    pnpm install
    uv run pre-commit install
    echo "✓ Installation complete"

# Run linters (Python + Node.js)
lint:
    uv run ruff check .
    pnpm biome check .

# Format code (Python + Node.js)
format:
    uv run ruff format .
    pnpm biome format --write .

# Run all tests
test:
    uv run pytest

# Run tests for specific library
test-lib lib:
    uv run pytest libs/{{lib}}/tests/
```

**Alternatives Considered**:
- **Make**: Less readable, platform-specific issues
- **npm scripts**: Only works for Node.js, not Python
- **Shell scripts**: Less discoverable, no built-in help

---

### 6. pnpm Workspace Configuration

**Decision**: Use pnpm workspaces for Node.js tooling packages

**Rationale**:
- Efficient disk space usage (content-addressable storage)
- Strict dependency resolution (no phantom dependencies)
- Fast installation
- Good monorepo support

**Configuration Approach**:
```yaml
# pnpm-workspace.yaml
packages:
  - 'packages/*'
```

```json
// Root package.json
{
  "name": "nexus-monorepo",
  "private": true,
  "engines": {
    "node": ">=22.0.0",
    "pnpm": ">=9.0.0"
  },
  "devDependencies": {
    "@biomejs/biome": "^1.9.0"
  }
}
```

**Alternatives Considered**:
- **npm workspaces**: Slower, less efficient
- **yarn workspaces**: Good but pnpm is faster and more strict

---

### 7. biome Configuration for Node.js

**Decision**: Use biome for JavaScript/TypeScript linting and formatting

**Rationale**:
- Single tool for linting + formatting (like ruff for Python)
- Very fast (written in Rust)
- Good defaults, minimal configuration needed
- Growing ecosystem

**Configuration Approach**:
```json
// biome.json
{
  "$schema": "https://biomejs.dev/schemas/1.9.0/schema.json",
  "organizeImports": {
    "enabled": true
  },
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true
    }
  },
  "formatter": {
    "enabled": true,
    "indentStyle": "space",
    "indentWidth": 2,
    "lineWidth": 100
  }
}
```

**Alternatives Considered**:
- **ESLint + Prettier**: Two tools, slower, more configuration
- **deno fmt**: Requires Deno runtime

---

## Summary

All research topics resolved. Ready to proceed to Phase 1 (Design & Contracts).

**Key Decisions**:
1. uv workspaces for Python package management
2. pytest with root-level configuration
3. ruff for Python linting/formatting
4. Pre-commit hooks with ruff + nbstripout
5. just for command runner with fail-fast error handling
6. pnpm workspaces for Node.js packages
7. biome for JavaScript/TypeScript linting/formatting

**No blockers** - All tools are mature and well-documented.
