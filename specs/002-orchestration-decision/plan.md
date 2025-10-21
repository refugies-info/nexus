# Implementation Plan: Pipeline Orchestration & Update Handling

**Branch**: `002-orchestration-decision` | **Date**: 2025-10-21 | **Spec**: `/specs/002-orchestration-decision/spec.md`
**Input**: Feature specification from `/specs/002-orchestration-decision/spec.md`

## Summary

Implement lightweight Python orchestration for the Nexus AI pipeline with Supabase state management and smart update handling. The system processes French learning programs through 9 stages: ingestion → editorial policy validation → reconciliation (with Carif-Oref CSV) → enrichment → langage clair → translation → validation → publication. Editorial policy validation rejects non-compliant programs early; Carif-Oref reconciliation ensures data completeness by hourly CSV fetching and deterministic conflict resolution. Update handling preserves human work through smart catch-up and diff review. Architecture: n8n (orchestration) + FastAPI (business logic) + Supabase (state management).

## Technical Context

**Language/Version**: Python 3.11+ (FastAPI backend) + Node.js (n8n workflows)
**Primary Dependencies**: FastAPI, Pydantic, Supabase client, structlog, deepdiff, tenacity, n8n CLI
**Storage**: Supabase PostgreSQL with JSONB for workflow state, stage executions, information sheets, update events, update diffs
**Testing**: pytest (unit/integration/contract tests), TDD-first approach (CAR-016 to CAR-019)
**Target Platform**: Linux server (Supabase Cloud + FastAPI deployment)
**Project Type**: Polyglot monorepo (Python libs/ + Node.js packages/)
**Performance Goals**: 24-hour end-to-end latency per program (SC-001), <5 minute smart catch-up (SC-005), <1 hour Carif-Oref CSV latency (SC-016)
**Constraints**: 100 concurrent programs (SC-002), 99% uptime (SC-012), <5% false positive policy validation (SC-013), 90%+ Carif-Oref reconciliation success (SC-015)
**Scale/Scope**: ~100 source data updates per week, 15+ editorial policy categories, 9 pipeline stages, 4 user stories (P1-P4)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Validate compliance with Nexus Constitution (`.specify/memory/constitution.md`):

- [x] **Data Quality First**: Editorial policy validation (15+ categories) + Carif-Oref reconciliation with hourly CSV fetch + deterministic conflict resolution (FR-009b through FR-009q)
- [x] **Pipeline Modularity**: 9 independent stages with well-defined contracts (Pydantic models), isolated failures (FR-005), partial replay support (FR-006), CAR-001 through CAR-004
- [x] **Multilingual by Design**: 8-language support via langage clair → translation pipeline; translation quality validation in validation stage (FR-007)
- [x] **Editorial Compliance**: Editorial policy validation stage enforces Réfugiés.info compliance; quality checks in validation stage; manual review routing (FR-007, FR-009b through FR-009i)
- [x] **Integration Independence**: Supabase state management independent of Réfugiés.info; publication API contract to be designed (Principle V); n8n + FastAPI architecture
- [x] **Observability & Traceability**: Structured logging (CAR-005, CAR-006), data lineage tracking (CAR-007), metrics collection per stage (CAR-008), alerts for failures (CAR-009)
- [x] **Incremental Delivery**: MVP scope: 9-stage pipeline for French learning programs; 4 user stories prioritized P1-P4; each independently testable/deployable (CAR-010 through CAR-012)
- [x] **Technology Foundation**: Polyglot monorepo (Python libs/ + Node.js packages/); Python 3.11+ FastAPI; n8n for orchestration; Supabase PostgreSQL; uv + pnpm dependency management
- [x] **User-Centered Development (NON-NEGOTIABLE)**: Diff review interface for editorial team (US3); risk scoring tunable based feedback (CAR-014); review efficiency metrics (CAR-015); AI transparency in diff review
- [x] **Notebook Governance**: Notebooks/ directory planned; exploratory work for data quality analysis; security review for credentials before commit
- [x] **Langage Clair (NON-NEGOTIABLE)**: Langage clair stage in pipeline (stage 5); editorial review workflow for AI-generated content; feedback loop via diff review
- [x] **Culturally-Aware Translation (NON-NEGOTIABLE)**: Translation stage (stage 6) with cultural mediation; validation stage checks cultural appropriateness; editorial review for high-stakes content
- [x] **TDD Compliance (NON-NEGOTIABLE)**: All tasks include unit/integration/contract tests (CAR-016 through CAR-019); red-green-refactor cycle enforced in implementation phase
- [x] **GDPR Compliance (NON-NEGOTIABLE)**: Data minimization (only pipeline data retained); legal basis documented (legitimate interest); user rights via editorial review; DPAs with Supabase/translation APIs

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

**Polyglot Monorepo** (Constitution Principle VIII: Technology Foundation)

```
apps/orchestration/              # Python orchestration service (FastAPI + n8n integration)
├── src/
│   ├── api/                     # FastAPI endpoints
│   │   ├── workflows.py         # Workflow execution endpoints
│   │   ├── updates.py           # Update detection/routing endpoints
│   │   ├── diffs.py             # Diff review endpoints
│   │   └── monitoring.py        # Monitoring/metrics endpoints
│   ├── services/                # Business logic
│   │   ├── workflow_service.py
│   │   ├── stage_service.py
│   │   ├── policy_validator.py  # Editorial policy validation
│   │   ├── reconciliation_service.py  # Carif-Oref CSV reconciliation
│   │   ├── update_detector.py
│   │   ├── smart_catchup.py
│   │   ├── diff_generator.py
│   │   ├── risk_scorer.py
│   │   ├── metrics_service.py
│   │   └── alert_service.py
│   ├── models/                  # Pydantic models
│   │   ├── workflow.py
│   │   ├── stage.py
│   │   ├── update.py
│   │   ├── diff.py
│   │   └── policy.py
│   ├── db/                      # Database layer
│   │   ├── client.py            # Supabase client
│   │   └── repositories/        # Data access objects
│   │       ├── workflow_repository.py
│   │       ├── stage_repository.py
│   │       ├── update_repository.py
│   │       ├── diff_repository.py
│   │       └── policy_repository.py
│   ├── auth/                    # Authentication/authorization
│   │   ├── supabase_auth.py
│   │   └── rbac.py
│   ├── utils/                   # Utilities
│   │   ├── logging.py           # Structured logging (structlog)
│   │   ├── errors.py            # Custom exceptions
│   │   ├── retry.py             # Exponential backoff (tenacity)
│   │   ├── checksum.py          # SHA-256 checksums
│   │   └── state_machine.py     # Pipeline state machine
│   └── main.py                  # FastAPI app entry point
├── tests/
│   ├── unit/                    # Unit tests (mocked dependencies)
│   ├── integration/             # Integration tests (real Supabase)
│   ├── contract/                # API contract tests
│   ├── fixtures/                # Test data
│   ├── benchmarks/              # Performance tests
│   └── load/                    # Load testing
├── pyproject.toml               # Python dependencies (uv)
└── pytest.ini                   # pytest configuration

supabase/                        # Centralized Supabase configuration
├── migrations/
│   └── 001_init_schema.sql      # Database schema (workflow_runs, stage_executions, etc.)
└── config.toml

packages/tooling/               # Node.js tooling
├── src/
│   └── n8n-workflows/          # n8n workflow management scripts
├── package.json
└── tsconfig.json

specs/002-orchestration-decision/
├── workflows/                   # n8n workflow definitions
│   ├── pipeline-orchestration.json
│   ├── update-detection.json
│   ├── smart-catchup.json
│   ├── diff-generation.json
│   └── README.md
├── contracts/                   # API contracts (OpenAPI specs)
│   ├── workflows-api.yaml
│   ├── updates-api.yaml
│   ├── diffs-api.yaml
│   └── monitoring-api.yaml
├── data-model.md                # Database schema documentation
├── quickstart.md                # Getting started guide
└── research.md                  # Phase 0 research findings

notebooks/                       # Jupyter notebooks
├── exploratory/                 # Data quality analysis
├── production-informing/        # Performance benchmarks
└── learning/                    # Tutorials

.github/workflows/
├── orchestration-tests.yml      # CI/CD for tests
└── orchestration-deploy.yml     # Deployment pipeline
```

**Structure Decision**: Polyglot monorepo with Python-first pipeline (Constitution VIII). Orchestration logic in `apps/orchestration/` (FastAPI + n8n integration). Supabase migrations centralized in `supabase/`. n8n workflows in feature-specific `specs/002-orchestration-decision/workflows/`. Follows dsfr-kit convention: Python in `apps/`, Node.js in `packages/`.

## Complexity Tracking

**No Constitution violations.** All 12 principles satisfied:
- Data Quality First: Editorial policy validation + Carif-Oref reconciliation
- Pipeline Modularity: 9 independent stages with contracts
- Multilingual by Design: 8-language pipeline (langage clair → translation)
- Editorial Compliance: Policy validation + quality checks
- Integration Independence: Supabase + n8n + FastAPI architecture
- Observability & Traceability: Structured logging + metrics + data lineage
- Incremental Delivery: 4 user stories (P1-P4), each independently testable
- Technology Foundation: Python 3.11+ FastAPI + n8n + Supabase
- User-Centered Development: Diff review interface + editorial feedback loop
- Notebook Governance: Notebooks/ directory with security review
- Langage Clair: Stage 5 in pipeline with editorial review
- Culturally-Aware Translation: Stage 6 with cultural mediation
- TDD Compliance: All tasks include unit/integration/contract tests
- GDPR Compliance: Data minimization + legal basis + user rights

**Architectural Decisions**:
- **n8n + FastAPI hybrid**: Leverages existing n8n prototype for faster MVP while maintaining TDD-compliant Python services for complex logic
- **Hourly Carif-Oref fetch**: Balances <1 hour latency requirement (SC-016) with operational efficiency
- **Deterministic conflict resolution**: Prevents pipeline blocking on data conflicts while maintaining quality
- **Final decision audit trail**: Reduces storage overhead; full evaluation trace in structured logs
