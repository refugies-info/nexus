# Feature Specification: Polyglot Monorepo Setup

**Feature Branch**: `001-monorepo-setup`  
**Created**: 2025-10-20  
**Status**: Draft  
**Input**: User description: "Setup polyglot monorepo structure with Python (libs/) and Node.js (packages/) following constitutional principles"  
**Linear Issue**: [RI-909](https://linear.app/refugiesinfo/issue/RI-909/setup-polyglot-monorepo-structure)

## Clarifications

### Session 2025-10-20

- Q: What Python dependencies should be included in initial `pyproject.toml`? → A: Minimal core dependencies only (ruff, pytest, mypy, pre-commit, nbstripout) - pipeline-specific dependencies will be added incrementally as features are developed
- Q: How should test types (contract, integration, unit) be organized? → A: Separate test types by directory (contract/, integration/, unit/) within each library's tests/ folder
- Q: How should justfile handle missing prerequisites (uv, pnpm, just)? → A: Fail fast with clear error messages and installation instructions when prerequisites are missing
- Q: How should pipeline stages be organized in the libs/ directory? → A: Each pipeline stage will be a separate library in libs/ (e.g., libs/ingestion/, libs/reconciliation/, libs/enrichment/) to enable independent development, testing, and deployment
- Q: How should shared code (utilities, types, constants) be organized? → A: Create libs/common/ for shared utilities and types used across pipeline stages

## User Research *(mandatory for Nexus)*

**User Research Conducted**:
- **Not applicable** - This is an infrastructure/tooling feature that does not directly affect end users (refugees/immigrants)
- Primary stakeholders are developers working on the Nexus pipeline
- Developer experience requirements derived from constitutional principles (Principle VIII: Technology Foundation)

**AI Transparency Testing** (if applicable):
- **Not applicable** - No AI components or user-facing features in this infrastructure setup

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### Developer Story 1 - Python Package Management (Priority: P1)

As a developer, I need to set up Python package management with uv so that I can install dependencies and manage the Python workspace efficiently.

**Why this priority**: Foundation for all Python development - without this, no Python code can be written or tested. This is the absolute minimum to start development.

**Independent Test**: Can be fully tested by running `uv sync` and verifying that Python dependencies are installed correctly. Delivers immediate value by enabling Python development.

**Acceptance Scenarios**:

1. **Given** a fresh clone of the repository, **When** I run `just install`, **Then** all Python and Node.js dependencies are installed
2. **Given** a fresh clone of the repository, **When** I run `uv sync`, **Then** all Python dependencies are installed in a virtual environment
3. **Given** the Python workspace is configured, **When** I add a new dependency to `pyproject.toml`, **Then** `uv sync` installs it correctly
4. **Given** the monorepo structure, **When** I run `uv run python -c "import libs.common"`, **Then** Python can resolve imports from the libs/ workspace packages

---

### Developer Story 2 - Directory Structure & Tooling (Priority: P2)

As a developer, I need the complete monorepo directory structure with linting and formatting tools so that I can write quality code following project standards.

**Why this priority**: Establishes code quality standards and complete workspace structure. Builds on P1 by adding quality gates and Node.js tooling.

**Independent Test**: Can be tested by running linters (`uv run ruff check`, `pnpm biome check`) and verifying directory structure exists. Delivers value by enforcing code quality.

**Acceptance Scenarios**:

1. **Given** the monorepo structure, **When** I run `just lint`, **Then** both Python and Node.js code are linted according to project standards
2. **Given** the justfile is configured, **When** I run `just format`, **Then** both Python and Node.js code are formatted automatically
3. **Given** the directory structure, **When** I navigate to `libs/`, **Then** I see separate library directories for each pipeline stage (ingestion/, reconciliation/, enrichment/, langage_clair/, translation/, validation/, publication/) plus common/
4. **Given** the directory structure, **When** I navigate to `packages/tooling/`, **Then** I see Node.js tooling packages
5. **Given** the directory structure, **When** I navigate to `notebooks/`, **Then** I see the Jupyter notebooks directory

---

### Developer Story 3 - Pre-commit Hooks & Testing (Priority: P3)

As a developer, I need pre-commit hooks and testing infrastructure so that code quality is automatically enforced and I can write tests.

**Why this priority**: Automates quality enforcement and enables TDD. Builds on P1 and P2 by adding automation and testing capabilities.

**Independent Test**: Can be tested by making a commit and verifying hooks run, and by running `just test`. Delivers value by preventing quality issues from being committed.

**Acceptance Scenarios**:

1. **Given** pre-commit hooks are installed, **When** I commit code, **Then** ruff linting and formatting checks run automatically
2. **Given** pre-commit hooks are configured, **When** I commit a Jupyter notebook, **Then** nbstripout removes outputs before commit
3. **Given** pytest is configured, **When** I run `just test`, **Then** the test suite executes successfully (even with zero tests initially)
4. **Given** the testing infrastructure, **When** I create a test file in `libs/ingestion/tests/unit/`, **Then** pytest discovers and runs it

---

### Edge Cases

- **Empty repository**: What happens when setting up the monorepo structure in a repository that only has README and constitution?
- **Existing files**: How does the setup handle existing files that might conflict with the new structure?
- **Missing tools**: What happens if uv or pnpm are not installed on the developer's machine?
- **Python version mismatch**: How does the system handle if the developer has Python < 3.12?
- **Notebook outputs**: What happens if a developer commits a notebook with outputs before pre-commit hooks are installed?

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

#### Directory Structure
- **FR-001**: Repository MUST have a `libs/` directory for Python packages
- **FR-002**: Repository MUST have a `packages/` directory for Node.js packages
- **FR-003**: Repository MUST have a `notebooks/` directory for Jupyter notebooks
- **FR-004**: Repository MUST have a `docs/` directory for documentation
- **FR-005**: `libs/` MUST contain separate library directories for each pipeline stage: `ingestion/`, `reconciliation/`, `enrichment/`, `langage_clair/`, `translation/`, `validation/`, `publication/`
- **FR-006**: `libs/` MUST contain a `common/` library for shared utilities and types used across pipeline stages
- **FR-007**: Each pipeline stage library MUST have a `src/` directory for source code and a `tests/` directory for tests
- **FR-008**: Each library's `tests/` directory MUST be organized into subdirectories by test type: `contract/`, `integration/`, `unit/`

#### Python Configuration
- **FR-009**: Repository MUST have a `pyproject.toml` file configuring the Python workspace
- **FR-010**: `pyproject.toml` MUST specify Python 3.12+ as the minimum version
- **FR-011**: `pyproject.toml` MUST configure uv as the package manager
- **FR-012**: `pyproject.toml` MUST configure ruff for linting and formatting
- **FR-013**: `pyproject.toml` MUST configure pytest as the testing framework
- **FR-014**: `pyproject.toml` MUST configure mypy for type checking
- **FR-015**: `pyproject.toml` MUST include only minimal core dependencies initially: ruff, pytest, mypy, pre-commit, nbstripout
- **FR-016**: Python packages MUST be installable via `uv sync`
- **FR-017**: Each pipeline stage library MUST be configured as a separate package in the uv workspace

#### Node.js Configuration
- **FR-018**: Repository MUST have a `package.json` file at the root
- **FR-019**: Repository MUST have a `pnpm-workspace.yaml` file defining the monorepo workspaces
- **FR-020**: `package.json` MUST specify Node.js 22+ as the minimum version
- **FR-021**: Node.js packages MUST use pnpm as the package manager
- **FR-022**: Node.js tooling MUST use biome for linting and formatting

#### Code Quality Tools
- **FR-023**: Repository MUST have a `.pre-commit-config.yaml` file
- **FR-024**: Pre-commit hooks MUST include ruff for Python linting and formatting
- **FR-025**: Pre-commit hooks MUST include nbstripout for Jupyter notebook output removal
- **FR-026**: Pre-commit hooks MUST include trailing whitespace removal
- **FR-027**: Pre-commit hooks MUST include end-of-file fixer
- **FR-028**: Developers MUST be able to install pre-commit hooks via `uv run pre-commit install`

#### Git Configuration
- **FR-029**: Repository MUST have a `.gitignore` file excluding build artifacts, virtual environments, and notebook outputs
- **FR-030**: `.gitignore` MUST exclude Python cache directories (`__pycache__/`, `*.pyc`, `.pytest_cache/`)
- **FR-031**: `.gitignore` MUST exclude Node.js directories (`node_modules/`, `.pnpm-store/`)
- **FR-032**: `.gitignore` MUST exclude Jupyter notebook checkpoints (`.ipynb_checkpoints/`)
- **FR-033**: `.gitignore` MUST exclude environment files (`.env`, `.env.local`)

#### Task Runner
- **FR-034**: Repository MUST have a `justfile` providing common development commands
- **FR-035**: `justfile` MUST include commands for installing dependencies (e.g., `just install`)
- **FR-036**: `justfile` MUST include commands for running linters and formatters (e.g., `just lint`, `just format`)
- **FR-037**: `justfile` MUST include commands for running tests (e.g., `just test`)
- **FR-038**: `justfile` MUST include commands for setting up pre-commit hooks (e.g., `just setup`)
- **FR-039**: `justfile` MUST include a default recipe that lists all available commands
- **FR-040**: `justfile` MUST support both Python and Node.js tooling commands
- **FR-041**: `justfile` MUST fail fast with clear error messages and installation instructions when prerequisites (uv, pnpm, just) are missing

#### Documentation
- **FR-042**: Repository MUST have a `CONTRIBUTING.md` file with development setup instructions
- **FR-043**: `CONTRIBUTING.md` MUST document how to install just and use the justfile
- **FR-044**: `CONTRIBUTING.md` MUST document how to install dependencies (uv and pnpm)
- **FR-045**: `CONTRIBUTING.md` MUST document available just commands
- **FR-046**: `CONTRIBUTING.md` MUST document the monorepo structure and conventions
- **FR-047**: `CONTRIBUTING.md` MUST document the independent library structure for pipeline stages

### Constitution-Aligned Requirements

#### Principle II: Pipeline Modularity
- **CAR-001**: Directory structure MUST support independent pipeline stages as per Constitution Principle II
- **CAR-002**: Each pipeline stage MUST be independently testable with its own `tests/` directory

#### Principle VIII: Technology Foundation
- **CAR-003**: Monorepo MUST follow polyglot architecture with Python in `libs/` and Node.js in `packages/` (Constitution Principle VIII)
- **CAR-004**: Python MUST be the primary language for pipeline implementation
- **CAR-005**: Node.js MAY be used for developer tooling and build scripts
- **CAR-006**: Dependency management MUST use uv for Python and pnpm for Node.js
- **CAR-007**: Code quality tools MUST include ruff for Python and biome for Node.js

#### Principle X: Notebook Governance
- **CAR-008**: Repository MUST have a `notebooks/` directory for Jupyter notebooks (Constitution Principle X)
- **CAR-009**: Pre-commit hooks MUST include nbstripout to remove notebook outputs before commit
- **CAR-010**: `.gitignore` MUST exclude notebook checkpoints and outputs

#### Testing Discipline (Principle: Testing Discipline)
- **CAR-011**: Testing infrastructure MUST support TDD with pytest (Constitution: Testing Discipline)
- **CAR-012**: Test directory structure MUST enable contract, integration, and unit tests

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: Developers can clone the repository and run `just install` to install all dependencies in under 3 minutes
- **SC-002**: Running `just lint` completes successfully with zero configuration errors
- **SC-003**: Running `just test` executes successfully (even with zero tests initially)
- **SC-004**: Pre-commit hooks execute successfully on every commit, preventing quality issues from being committed
- **SC-005**: All required directories (`libs/`, `packages/`, `notebooks/`, `docs/`) exist and are properly structured
- **SC-006**: Running `just` (default recipe) lists all available commands with descriptions
- **SC-007**: Documentation in `CONTRIBUTING.md` enables a new developer to set up the environment in under 10 minutes
- **SC-008**: 100% of constitutional requirements (CAR-001 through CAR-012) are satisfied by the monorepo structure

## Assumptions

- Developers have Python 3.12+ and Node.js 22+ installed on their machines
- Developers have just (command runner) installed or will install it as part of setup
- Developers have basic familiarity with Python and Node.js package managers
- Developers have Git installed and configured
- The repository will be hosted on GitHub (for CI/CD integration in future)
- Initial setup will create empty directory structures; actual pipeline implementation will come in subsequent features

## Out of Scope

- Actual pipeline stage implementation (ingestion, translation, etc.) - this is infrastructure only
- CI/CD pipeline configuration (GitHub Actions, etc.)
- Deployment configuration
- Database setup or configuration
- API implementation
- Docker or containerization setup
- Production environment configuration

