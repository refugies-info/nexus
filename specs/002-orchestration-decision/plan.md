# Implementation Plan: Pipeline Orchestration & Update Handling

**Branch**: `002-orchestration-decision` | **Date**: 2025-10-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-orchestration-decision/spec.md`
**Linear**: [RI-910](https://linear.app/refugiesinfo/issue/RI-910)

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement hybrid orchestration infrastructure using n8n for workflow orchestration + Python services for complex business logic. The system processes French learning programs through a 7-stage pipeline (ingestion → reconciliation → enrichment → langage clair → translation → validation → publication) with smart update handling that preserves human-in-the-loop work through AI-accelerated catch-up and diff review.

**Key Technical Decisions**:
- **Orchestration**: n8n workflows (leverage existing prototype)
- **Business Logic**: Python FastAPI services (TDD-compliant, testable)
- **State Management**: Supabase (PostgreSQL + real-time + auth)
- **Update Strategy**: Smart catch-up with risk-based sampling (~100 updates/week)
- **Diff Review**: Streamlit UI with Supabase Auth + RBAC

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11+ (pipeline services), n8n (workflow orchestration)
**Primary Dependencies**: FastAPI, Supabase (supabase-py), n8n, Streamlit, pydantic, mypy, pytest
**Storage**: Supabase (managed PostgreSQL) for state management (workflow_runs, stage_executions, information_sheets, update_events, update_diffs)
**Testing**: pytest (unit, integration, contract tests), TDD approach (tests-first)
**Target Platform**: Linux server (Docker containers), n8n self-hosted or cloud
**Project Type**: Hybrid (n8n workflows + Python microservices)
**Performance Goals**:
  - Process 100 concurrent programs without degradation
  - End-to-end pipeline completion within 24 hours
  - Smart catch-up processes updates in <5 minutes
  - Detect 100% of updates within 1 hour
**Constraints**:
  - 99% uptime for pipeline processing
  - Retry failed stages with exponential backoff (up to 24 hours for API failures)
  - Editorial review workload <1 hour/week (risk-based sampling)
**Scale/Scope**:
  - ~Hundreds of French learning programs
  - ~100 source data updates per week
  - 7 pipeline stages per program
  - 8 target languages for translation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Validate compliance with Nexus Constitution (`.specify/memory/constitution.md`):

- [X] **Data Quality First**: State management schema tracks data quality at each stage; validation hooks planned for stage transitions
- [X] **Pipeline Modularity**: n8n workflows call independent Python services; each service has clear input/output contracts; stages are independently testable
- [N/A] **Multilingual by Design**: Not applicable - orchestration infrastructure only; translation stage will be implemented separately
- [X] **Editorial Compliance**: Diff review interface with manual approval workflow; editorial team controls high-risk updates
- [N/A] **Integration Independence**: Not applicable - orchestration infrastructure only; integration contracts defined in separate stage features
- [X] **Observability & Traceability**: Supabase tracks complete workflow state; n8n provides execution logs; Python services emit structured logs; data lineage tracked via workflow_runs and stage_executions tables
- [X] **Incremental Delivery**: 4 prioritized user stories (P1-P4); Phase 1 (basic orchestration), Phase 2 (update handling), Phase 3 (diff review), Phase 4 (monitoring)
- [X] **Technology Foundation**: Monorepo structure already established (spec 001); Python services in libs/, n8n workflows exported to version control
- [X] **User-Centered Development (NON-NEGOTIABLE)**: Diff review UI validated with editorial team (CAR-013); risk scoring thresholds iteratively adjusted based on feedback (CAR-014); metrics tracked for optimization (CAR-015)
- [N/A] **Notebook Governance**: Not applicable - no notebooks in orchestration infrastructure
- [N/A] **Langage Clair (NON-NEGOTIABLE)**: Not applicable - orchestration infrastructure only; langage clair stage will be implemented separately
- [N/A] **Culturally-Aware Translation (NON-NEGOTIABLE)**: Not applicable - orchestration infrastructure only; translation stage will be implemented separately
- [X] **TDD Compliance (NON-NEGOTIABLE)**: All Python services developed test-first (CAR-016); unit tests for isolated behavior (CAR-017); integration tests for end-to-end pipeline (CAR-018); contract tests for diff generation (CAR-019)
- [X] **GDPR Compliance (NON-NEGOTIABLE)**: Supabase Auth for editorial team access; RBAC restricts access; audit trail tracks who reviewed what; no PII in orchestration layer (program IDs only)

*If any principle cannot be satisfied, document justification in Complexity Tracking section.*

## Project Structure

### Documentation (this feature)

```
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```
# Polyglot Monorepo (established in spec 001-monorepo-setup)
# This feature adds orchestration infrastructure to existing monorepo

libs/                           # Python packages
├── orchestration/              # ⭐ NEW: Orchestration library (this feature)
│   ├── src/
│   │   └── orchestration/
│   │       ├── __init__.py
│   │       ├── models/         # Pydantic models for state management
│   │       │   ├── workflow.py
│   │       │   ├── stage.py
│   │       │   ├── update.py
│   │       │   └── diff.py
│   │       ├── services/       # Business logic services
│   │       │   ├── update_detector.py
│   │       │   ├── smart_catchup.py
│   │       │   ├── diff_generator.py
│   │       │   └── risk_scorer.py
│   │       ├── db/             # Supabase client and queries
│   │       │   ├── client.py
│   │       │   ├── workflow_repo.py
│   │       │   ├── update_repo.py
│   │       │   └── diff_repo.py
│   │       └── config.py       # Configuration management
│   ├── tests/
│   │   ├── integration/        # End-to-end pipeline tests
│   │   │   ├── test_pipeline_execution.py
│   │   │   ├── test_update_handling.py
│   │   │   └── test_diff_review.py
│   │   └── unit/               # Unit tests for services
│   │       ├── test_update_detector.py
│   │       ├── test_smart_catchup.py
│   │       ├── test_diff_generator.py
│   │       └── test_risk_scorer.py
│   ├── pyproject.toml          # uv dependency management
│   ├── pytest.ini
│   └── README.md
│
├── pipeline/                   # Pipeline stages (separate features)
│   └── [to be implemented in separate specs]
│
└── shared/                     # Shared utilities
    └── [existing from spec 001]

apps/                           # Python applications
├── orchestration-api/          # ⭐ NEW: FastAPI service for n8n integration (this feature)
│   ├── src/
│   │   └── orchestration_api/
│   │       ├── __init__.py
│   │       ├── main.py         # FastAPI app entry point
│   │       ├── routers/        # API route handlers
│   │       │   ├── workflows.py
│   │       │   ├── updates.py
│   │       │   └── diffs.py
│   │       ├── dependencies.py # FastAPI dependencies (auth, db)
│   │       └── config.py       # App-specific configuration
│   ├── tests/
│   │   └── contract/           # Contract tests for n8n ↔ Python integration
│   │       ├── test_workflow_api.py
│   │       ├── test_update_api.py
│   │       └── test_diff_api.py
│   ├── pyproject.toml          # Dependencies: orchestration lib, FastAPI
│   ├── Dockerfile              # Container for deployment
│   └── README.md
│
└── diff-review-ui/             # ⭐ NEW: Streamlit diff review interface (this feature)
    ├── src/
    │   └── diff_review_ui/
    │       ├── app.py          # Streamlit app entry point
    │       ├── components/
    │       │   ├── diff_viewer.py
    │       │   └── approval_controls.py
    │       └── auth.py         # Supabase Auth integration
    ├── tests/
    │   └── test_ui_components.py
    ├── pyproject.toml          # Dependencies: orchestration lib, Streamlit
    ├── Dockerfile              # Container for deployment
    └── README.md

workflows/                      # ⭐ NEW: n8n workflow exports (this feature)
├── pipeline-orchestration.json # Main 7-stage pipeline workflow
├── update-detection.json       # Update detection and routing
├── smart-catchup.json          # AI-accelerated catch-up workflow
└── README.md                   # n8n workflow documentation

supabase/                       # ⭐ NEW: Supabase schema (this feature)
├── migrations/
│   ├── 001_create_workflow_tables.sql
│   ├── 002_create_update_tables.sql
│   └── 003_create_diff_tables.sql
├── seed.sql                    # Test data for development
└── README.md

# Monorepo root files (existing)
├── pyproject.toml              # Root Python workspace config
├── package.json                # Root Node.js workspace config
├── .github/
│   └── workflows/              # CI/CD pipelines
└── docs/                       # Shared documentation
```

**Structure Decision**: Hybrid architecture with four components:

1. **Orchestration Library** (`libs/orchestration/`): Shared Python library with business logic (update detection, smart catch-up, diff generation, risk scoring), data models, and database repositories. Follows monorepo convention established in spec 001.

2. **FastAPI Service** (`apps/orchestration-api/`): REST API for n8n integration. Exposes endpoints for workflow execution, update handling, and diff management. Depends on `libs/orchestration/`.

3. **Streamlit UI** (`apps/diff-review-ui/`): Web interface for editorial team to review and approve diffs. Depends on `libs/orchestration/`.

4. **n8n Workflows** (`workflows/`): Visual workflow definitions exported as JSON for version control. n8n orchestrates the 7-stage pipeline by calling FastAPI endpoints.

5. **Supabase Schema** (`supabase/`): PostgreSQL migrations for state management tables (workflow_runs, stage_executions, information_sheets, update_events, update_diffs).

This structure enables:
- **Separation of concerns**: Library (business logic) vs Apps (API/UI)
- **TDD compliance**: Library code is unit-testable, apps have contract tests
- **Reusability**: Both FastAPI and Streamlit apps depend on shared library
- **Visual workflows**: n8n provides editorial team visibility
- **Portability**: Library can work with any orchestrator
- **Version control**: n8n workflows tracked as JSON in Git

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
