# Implementation Plan: Polyglot Monorepo Setup

**Branch**: `001-monorepo-setup` | **Date**: 2025-10-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-monorepo-setup/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Establish the foundational monorepo infrastructure for the Nexus AI pipeline project. This includes setting up independent Python libraries for each pipeline stage (ingestion, reconciliation, enrichment, langage_clair, translation, validation, publication) plus a common library for shared utilities. The setup includes Python 3.12+ with uv workspace management, Node.js 22+ with pnpm for tooling, comprehensive code quality tools (ruff, biome, pre-commit hooks), testing infrastructure (pytest with contract/integration/unit test organization), and a justfile for improved developer experience. This infrastructure enables independent development, testing, and deployment of pipeline stages per Constitutional Principle II (Pipeline Modularity).

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.12+, Node.js 22+  
**Primary Dependencies**: 
- Python: uv (package manager), ruff (linting/formatting), pytest (testing), mypy (type checking), pre-commit (git hooks), nbstripout (notebook cleaning)
- Node.js: pnpm (package manager), biome (linting/formatting), just (command runner)

**Storage**: N/A (infrastructure setup only)  
**Testing**: pytest with contract/integration/unit test organization per library  
**Target Platform**: Development environment (macOS, Linux, Windows with WSL)  
**Project Type**: Polyglot monorepo (Python libraries + Node.js tooling)  
**Performance Goals**: 
- `just install` completes in under 3 minutes
- `just lint` completes with zero configuration errors
- Pre-commit hooks execute without blocking developer workflow

**Constraints**: 
- Must support Python 3.12+ and Node.js 22+
- Must work on developer machines without Docker (local development first)
- justfile must fail fast with clear error messages for missing prerequisites
- Each pipeline stage library must be independently testable

**Scale/Scope**: 
- 8 independent Python libraries (7 pipeline stages + 1 common)
- Minimal initial dependencies (ruff, pytest, mypy, pre-commit, nbstripout)
- Foundation for future pipeline implementation (not included in this phase)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Validate compliance with Nexus Constitution (`.specify/memory/constitution.md`):

- [x] **Data Quality First**: N/A for infrastructure setup - will be addressed in pipeline implementation features
- [x] **Pipeline Modularity**: ✅ Directory structure supports independent libraries per stage with separate src/ and tests/ directories (FR-005, FR-007, CAR-001, CAR-002)
- [x] **Multilingual by Design**: N/A for infrastructure setup - will be addressed in translation feature
- [x] **Editorial Compliance**: N/A for infrastructure setup - will be addressed in validation feature
- [x] **Integration Independence**: N/A for infrastructure setup - will be addressed in publication feature
- [x] **Observability & Traceability**: N/A for infrastructure setup - will be addressed in pipeline implementation features
- [x] **Incremental Delivery**: ✅ MVP scope clearly defined (P1: Python setup, P2: Tooling, P3: Pre-commit hooks); infrastructure-only, no pipeline logic
- [x] **Technology Foundation**: ✅ Polyglot monorepo with Python 3.12+ in libs/, Node.js 22+ in packages/; uv and pnpm for dependency management; ruff and biome for code quality (CAR-003 through CAR-007)
- [x] **User-Centered Development (NON-NEGOTIABLE)**: ✅ N/A for infrastructure - primary stakeholders are developers; no end-user impact
- [x] **Notebook Governance**: ✅ notebooks/ directory created; nbstripout in pre-commit hooks; .gitignore excludes outputs (FR-003, FR-021, FR-032, CAR-008, CAR-009, CAR-010)
- [x] **Langage Clair (NON-NEGOTIABLE)**: N/A for infrastructure setup - will be addressed in langage_clair library implementation
- [x] **Culturally-Aware Translation (NON-NEGOTIABLE)**: N/A for infrastructure setup - will be addressed in translation library implementation
- [x] **TDD Compliance (NON-NEGOTIABLE)**: ✅ pytest configured; test directory structure supports contract/integration/unit tests; TDD workflow enabled (FR-008, FR-013, CAR-011, CAR-012)
- [x] **GDPR Compliance (NON-NEGOTIABLE)**: N/A for infrastructure setup - will be addressed in pipeline implementation features handling personal data

*If any principle cannot be satisfied, document justification in Complexity Tracking section.*

## Project Structure

### Documentation (this feature)

```
specs/001-monorepo-setup/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (in progress)
├── research.md          # Phase 0: Tool configuration research
├── quickstart.md        # Phase 1: Developer onboarding guide
└── tasks.md             # Phase 2: Implementation tasks (via /speckit.tasks)
```

**Note**: No data-model.md or contracts/ needed for infrastructure setup.

### Source Code (repository root)

**Polyglot Monorepo Structure** (Constitution Principle VIII: Technology Foundation)

Each pipeline stage is an independent Python library enabling separate development, testing, and deployment:

```
nexus/
├── libs/                           # Python packages (independent libraries)
│   ├── common/                     # Shared utilities and types
│   │   ├── src/
│   │   │   └── nexus/
│   │   │       └── common/
│   │   │           └── __init__.py
│   │   ├── tests/
│   │   │   ├── contract/
│   │   │   ├── integration/
│   │   │   └── unit/
│   │   └── pyproject.toml
│   │
│   ├── ingestion/                  # Data ingestion stage
│   │   ├── src/
│   │   │   └── nexus/
│   │   │       └── ingestion/
│   │   │           └── __init__.py
│   │   ├── tests/
│   │   │   ├── contract/
│   │   │   ├── integration/
│   │   │   └── unit/
│   │   └── pyproject.toml
│   │
│   ├── reconciliation/             # Data reconciliation stage
│   │   ├── src/
│   │   │   └── nexus/
│   │   │       └── reconciliation/
│   │   ├── tests/
│   │   └── pyproject.toml
│   │
│   ├── enrichment/                 # Data enrichment stage
│   │   ├── src/
│   │   │   └── nexus/
│   │   │       └── enrichment/
│   │   ├── tests/
│   │   └── pyproject.toml
│   │
│   ├── langage_clair/              # ⭐ AI plain language transformation
│   │   ├── src/
│   │   │   └── nexus/
│   │   │       └── langage_clair/
│   │   ├── tests/
│   │   └── pyproject.toml
│   │
│   ├── translation/                # Multilingual translation stage
│   │   ├── src/
│   │   │   └── nexus/
│   │   │       └── translation/
│   │   ├── tests/
│   │   └── pyproject.toml
│   │
│   ├── validation/                 # Quality validation stage
│   │   ├── src/
│   │   │   └── nexus/
│   │   │       └── validation/
│   │   ├── tests/
│   │   └── pyproject.toml
│   │
│   └── publication/                # Publication to Réfugiés.info
│       ├── src/
│       │   └── nexus/
│       │       └── publication/
│       ├── tests/
│       └── pyproject.toml

packages/                  # Node.js packages
└── tooling/               # Build scripts, dev tools
    ├── src/
    ├── package.json
    └── tsconfig.json

notebooks/                 # Jupyter notebooks (exploratory work)

# Monorepo root files
├── pyproject.toml         # Root Python workspace config (uv workspaces)
├── package.json           # Root Node.js workspace config (pnpm workspaces)
├── pnpm-workspace.yaml    # pnpm workspace configuration
├── justfile               # Command runner for common dev tasks
├── .pre-commit-config.yaml # Pre-commit hooks configuration
├── .gitignore             # Git ignore patterns
├── CONTRIBUTING.md        # Developer onboarding guide
└── docs/                  # Shared documentation
```

**Structure Decision**: Independent library architecture chosen to enable true modularity per Constitutional Principle II. Each pipeline stage (ingestion, reconciliation, enrichment, langage_clair, translation, validation, publication) is a separate Python package with its own `pyproject.toml`, allowing independent development, testing, and deployment. The `libs/common/` library provides shared utilities and types. This structure supports the uv workspace feature for managing multiple interdependent packages in a single repository.

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

**No violations** - All applicable constitutional principles are satisfied for this infrastructure setup feature.

