# Nexus Monorepo - Development Commands
# List all available commands by running: just

# List all available commands
default:
    @just --list

# Install all dependencies and setup development environment
install:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "🔍 Checking prerequisites..."
    command -v uv >/dev/null 2>&1 || { echo "❌ Error: uv not found. Install: curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }
    command -v pnpm >/dev/null 2>&1 || { echo "❌ Error: pnpm not found. Install: npm install -g pnpm"; exit 1; }
    echo "✓ Prerequisites found"
    echo ""
    echo "📦 Installing Python dependencies..."
    uv sync
    echo "✓ Python dependencies installed"
    echo ""
    echo "📦 Installing Node.js dependencies..."
    pnpm install
    echo "✓ Node.js dependencies installed"
    echo ""
    echo "🪝 Installing pre-commit hooks..."
    uv run pre-commit install
    echo "✓ Pre-commit hooks installed"
    echo ""
    echo "✅ Installation complete!"
    echo ""
    echo "Next steps:"
    echo "  - Run 'just lint' to check code quality"
    echo "  - Run 'just test' to run tests"
    echo "  - Run 'just' to see all available commands"

# Run linters (Python + Node.js)
lint:
    @echo "🔍 Linting Python code..."
    uv run ruff check .
    @echo "✓ Python linting complete"
    @echo ""
    @echo "🔍 Linting Node.js code..."
    pnpm biome check .
    @echo "✓ Node.js linting complete"

# Format code (Python + Node.js)
format:
    @echo "✨ Formatting Python code..."
    uv run ruff format .
    @echo "✓ Python formatting complete"
    @echo ""
    @echo "✨ Formatting Node.js code..."
    pnpm biome format --write .
    @echo "✓ Node.js formatting complete"

# Run all tests
test:
    @echo "🧪 Running all tests..."
    uv run pytest
    @echo "✓ Tests complete"

# Run tests for specific library
test-lib lib:
    @echo "🧪 Running tests for {{lib}}..."
    uv run pytest libs/{{lib}}/tests/
    @echo "✓ Tests complete for {{lib}}"

# Type check Python code
typecheck:
    @echo "🔍 Type checking Python code..."
    uv run mypy libs/
    @echo "✓ Type checking complete"

# Run pre-commit hooks on all files
pre-commit:
    @echo "🪝 Running pre-commit hooks..."
    uv run pre-commit run --all-files
    @echo "✓ Pre-commit hooks complete"

# Clean build artifacts and caches
clean:
    @echo "🧹 Cleaning build artifacts..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
    @echo "✓ Clean complete"
