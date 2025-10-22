# Tasks: Pipeline Orchestration & Update Handling

**Feature**: Pipeline Orchestration & Update Handling
**Branch**: `002-orchestration-decision`
**Created**: 2025-10-20
**Updated**: 2025-10-21 (8-stage pipeline with editorial policy validation)
**Status**: Ready for Implementation

## Overview

This document contains all actionable tasks for implementing the Nexus pipeline orchestration system. Tasks are organized by implementation phase and user story, with clear dependencies and independent test criteria for each story.

**Total Tasks**: 109 (T001-T108 + T040n, including editorial policy validation and Carif-Oref reconciliation tasks)

**Implementation Strategy**: MVP-first approach with incremental delivery
- **Phase 1 (Setup)**: Infrastructure and database schema
- **Phase 2 (Foundational)**: Core orchestration services and n8n integration
- **Phase 3 (US1)**: Process new programs through 8-stage pipeline (including editorial policy validation + Carif-Oref reconciliation)
- **Phase 4 (US2)**: Handle data updates efficiently
- **Phase 5 (US3)**: Review and approve update diffs
- **Phase 6 (US4)**: Monitor pipeline execution
- **Phase 7 (Polish)**: Observability, testing, and documentation

---

## Phase 1: Setup & Infrastructure

**Goal**: Initialize project structure, configure dependencies, and prepare development environment

**Independent Test Criteria**:
- [ ] Python environment configured with all dependencies
- [ ] Node.js environment configured with all dependencies
- [ ] Supabase local instance running with schema initialized
- [ ] FastAPI service starts without errors
- [ ] n8n instance accessible and ready for workflow import

### Tasks

- [X] T001 Create Python package structure for orchestration service at `apps/orchestration/` with `src/`, `tests/`, `pyproject.toml`
- [X] T002 Create Node.js tooling package at `packages/tooling/` with build scripts for n8n workflow management
- [X] T003 [P] Configure `apps/orchestration/pyproject.toml` with Python dependencies: FastAPI, Pydantic, Supabase client, structlog, pytest, deepdiff
- [X] T004 [P] Configure `package.json` with Node.js dependencies: n8n CLI tools, TypeScript, testing framework
- [X] T005 Install Supabase CLI following https://supabase.com/docs/guides/local-development/cli/getting-started (macOS: `brew install supabase/tap/supabase`)
- [X] T005b Create Supabase account at https://supabase.com if not already created (required for production deployment)
- [X] T005c Initialize Supabase project locally with `supabase init` and configure connection string in `.env`
- [X] T005d Add Supabase CLI as workspace dev dependency (npm/pnpm) for consistent versioning across team
- [X] T006 Create `.env.example` file documenting required environment variables (Supabase URL/key, Data Inclusion API URL, Vercel AI Gateway credentials)
- [X] T007 Create database migration script at `supabase/migrations/001_init_schema.sql` with all tables from data-model.md (workflow_runs, stage_executions, information_sheets, update_events, update_diffs, policy_validation_decisions, carif_oref_reconciliation_status)
- [X] T008 [P] Create Supabase initialization script at `scripts/init-supabase.sh` to apply migrations and seed test data
- [X] T009 Create FastAPI application entry point at `apps/orchestration/src/main.py` with health check endpoint and middleware configuration
- [X] T010 Create directory structure for FastAPI modules at `apps/orchestration/src/`: `api/`, `services/`, `models/`, `db/`, `utils/`
- [X] T011 [P] Create pytest configuration at `apps/orchestration/pytest.ini` with test discovery and coverage settings
- [X] T012 Create n8n workflows directory at `specs/002-orchestration-decision/workflows/` with README documenting workflow structure

---

## Phase 2: Foundational Services & Database Layer

**Goal**: Implement core database access layer, Supabase integration, and foundational services

**Independent Test Criteria**:
- [ ] Supabase client connects successfully and can perform CRUD operations
- [ ] All database repositories implement required methods with proper error handling
- [ ] Pydantic models validate request/response data correctly
- [ ] Service layer methods execute without database errors
- [ ] Unit tests for repositories and services pass with >80% coverage

### Tasks

- [X] T013 Create Supabase client wrapper at `apps/orchestration/src/db/client.py` with connection pooling and error handling
- [X] T014 Create base repository class at `apps/orchestration/src/db/repositories/base.py` with common CRUD operations
- [X] T015 [P] Create workflow repository at `apps/orchestration/src/db/repositories/workflow.py` with methods: create_workflow_run, get_workflow_run, update_workflow_status, list_workflow_runs
- [X] T016 [P] Create stage execution repository at `apps/orchestration/src/db/repositories/stage.py` with methods: create_stage_execution, get_stage_execution, update_stage_status, list_stage_executions
- [X] T017 [P] Create information sheet repository at `apps/orchestration/src/db/repositories/information_sheet.py` with methods: create_information_sheet, get_information_sheet, update_information_sheet, get_by_program_id
- [X] T018 [P] Create update event repository at `apps/orchestration/src/db/repositories/update.py` with methods: create_update_event, get_update_event, update_processing_status, list_pending_updates
- [X] T019 [P] Create update diff repository at `apps/orchestration/src/db/repositories/diff.py` with methods: create_diff, get_diff, update_review_status, list_pending_diffs
- [X] T020 Create Pydantic models at `apps/orchestration/src/models/workflow.py`: WorkflowRunRequest, WorkflowRunResponse, WorkflowStatus
- [X] T021 [P] Create Pydantic models at `apps/orchestration/src/models/stage.py`: StageExecutionRequest, StageExecutionResponse, StageStatus
- [X] T022 [P] Create Pydantic models at `apps/orchestration/src/models/update.py`: UpdateEventRequest, UpdateEventResponse, UpdateStrategy
- [X] T023 [P] Create Pydantic models at `apps/orchestration/src/models/diff.py`: DiffRequest, DiffResponse, RiskScore, ReviewStatus
- [X] T024 Create configuration management at `apps/orchestration/src/config.py` using Pydantic BaseSettings for environment variables
- [X] T025 Create structured logging setup at `apps/orchestration/src/utils/logging.py` with structlog configuration and correlation ID middleware
- [X] T026 Create error handling utilities at `apps/orchestration/src/utils/errors.py` with custom exception classes and error response formatting
- [X] T027 Create unit tests for repositories at `apps/orchestration/tests/unit/db/test_repositories.py` with mocked Supabase client
- [X] T028 Create unit tests for Pydantic models at `apps/orchestration/tests/unit/models/test_models.py` validating schema and constraints

---

## Phase 3: User Story 1 - Process New Programs Through Pipeline

**Goal**: Implement core pipeline orchestration to process new programs through all 8 stages sequentially, including editorial policy validation and Carif-Oref reconciliation

**Story**: As the Nexus system, I need to process new French learning programs from Data Inclusion through all pipeline stages (ingestion → editorial policy validation → reconciliation → enrichment → langage clair → translation → validation → publication) so that accurate, multilingual information sheets are published to Réfugiés.info, with non-compliant programs rejected early and data reconciled with Carif-Oref.

**Why P1**: Foundation for all pipeline functionality - without this, no information sheets can be generated. Editorial policy validation ensures compliance before processing; Carif-Oref reconciliation ensures data completeness.

**Independent Test Criteria**:
- [ ] New program can be submitted to pipeline via API
- [ ] Program progresses through all 8 stages sequentially (including editorial policy validation)
- [ ] Non-compliant programs are rejected at policy validation stage with audit trail
- [ ] Carif-Oref CSV data is fetched and reconciled (hourly fetch, deterministic conflict resolution)
- [ ] State is tracked in database at each stage completion
- [ ] Program reaches publication stage and information sheet is marked as published
- [ ] Multiple programs can be processed concurrently without interference
- [ ] Failed stages are retried automatically with exponential backoff
- [ ] Failed programs are routed to manual review queue
- [ ] Integration test validates complete end-to-end pipeline execution

### Tasks

- [X] T029 [US1] Create workflow service at `apps/orchestration/src/services/workflow.py` with pure functions: start_workflow, get_workflow_status, update_workflow_stage, handle_stage_completion
- [X] T030 [US1] Create stage execution service at `apps/orchestration/src/services/stage.py` with pure functions: execute_stage, retry_stage, mark_stage_complete, handle_stage_failure
- [X] T031 [US1] Implement retry logic with exponential backoff at `apps/orchestration/src/utils/retry.py` using tenacity library (initial delay 1s, max delay 5min, max retries 10)
- [X] T032 [US1] Create workflow API endpoints at `apps/orchestration/src/api/workflows.py`: POST /workflows (start), GET /workflows/{id} (status), POST /workflows/{id}/status (update)
- [X] T033 [US1] Implement workflow state machine at `apps/orchestration/src/services/state_machine.py` with pure functions enforcing stage sequence: ingestion → editorial_policy_validation → reconciliation → enrichment → langage_clair → translation → validation → publication
- [X] T034 [US1] Create stage orchestrator at `apps/orchestration/src/services/orchestrator.py` with pure functions that call external stage services (placeholder for actual stage implementations)
- [X] T035 [US1] Implement error handling for stage failures at `apps/orchestration/src/services/error_handler.py` with retry logic and manual review routing
- [X] T036 [US1] Create unit tests for workflow service at `apps/orchestration/tests/unit/services/test_workflow_service.py` with mocked repositories
- [X] T037 [US1] Create unit tests for stage service at `apps/orchestration/tests/unit/services/test_stage_service.py` validating retry logic and state transitions
- [X] T038 [US1] Create integration tests for complete pipeline at `apps/orchestration/tests/integration/test_pipeline_execution.py` using test Supabase instance
- [X] T039 [US1] Create contract tests for workflow API at `apps/orchestration/tests/contract/test_workflow_api.py` validating request/response schemas
- [X] T040 [US1] Create editorial policy validator service at `apps/orchestration/src/services/policy.py` with pure functions: validate_program, check_policy_rules, generate_audit_trail, reject_program
- [X] T040b [US1] Create policy rule repository at `apps/orchestration/src/db/repositories/policy.py` with functions: get_policy_rules, get_rule_by_id, create_policy_decision, get_policy_decision
- [X] T040c [US1] Create Carif-Oref reconciliation service at `apps/orchestration/src/services/reconciliation.py` with pure functions: fetch_carif_oref_csv, match_programs, merge_data, detect_conflicts, resolve_conflicts
- [X] T040d [US1] Implement hourly CSV fetch scheduler at `apps/orchestration/src/services/carif_oref.py` using APScheduler for hourly Carif-Oref CSV updates
- [X] T040d-bis [US1] Create Data Inclusion connector service at `apps/orchestration/src/services/data_inclusion.py` with pure functions: fetch_program, fetch_programs, search_programs, get_program_by_id (mirrors carif_oref.py pattern)
- [X] T040e [US1] Create conflict resolution logic in `apps/orchestration/src/services/reconciliation.py` with pure functions implementing deterministic conflict resolution (prefer Carif-Oref if more recent, prefer Data Inclusion if more complete)
- [X] T040f [US1] Create policy validation API endpoint at `apps/orchestration/src/api/policies.py`: POST /policies/validate (validate program), GET /policies/decisions/{program_id} (get decision)
- [X] T040g [US1] Create reconciliation API endpoint at `apps/orchestration/src/api/reconciliation.py`: POST /reconciliation/process (reconcile), GET /reconciliation/status/{program_id} (status)
- [X] T040h [US1] Create unit tests for policy service at `apps/orchestration/tests/unit/services/test_policy.py` with various policy scenarios
- [X] T040i [US1] Create unit tests for reconciliation service at `apps/orchestration/tests/unit/services/test_reconciliation.py` validating data merging and conflict detection
- [X] T040j [US1] Create unit tests for reconciliation conflict resolution at `apps/orchestration/tests/unit/services/test_reconciliation.py` validating deterministic resolution
- [X] T040k [US1] Create integration tests for policy validation at `apps/orchestration/tests/integration/test_policy.py` with real policy scenarios
- [X] T040l [US1] Create integration tests for Carif-Oref reconciliation at `apps/orchestration/tests/integration/test_reconciliation.py` with CSV data
- [ ] T040m [US1] Create n8n workflow at `specs/002-orchestration-decision/workflows/pipeline-orchestration.json` that orchestrates 8-stage pipeline (including policy validation and reconciliation) with error handling and retry logic
- [ ] T040n [US1] Create policy rule versioning at `apps/orchestration/src/db/repositories/policy.py` with functions: get_rule_version, create_rule_version, track_applied_version, get_rules_by_version
- [ ] T041 [US1] Create n8n workflow documentation at `specs/002-orchestration-decision/workflows/README.md` explaining 8-stage pipeline flow (including policy validation and Carif-Oref reconciliation), error handling, and manual review routing
- [ ] T042 [US1] Create test data fixtures at `apps/orchestration/tests/fixtures/test_programs.json` with sample programs for testing
- [ ] T046 [US1] Create quickstart guide section in `specs/002-orchestration-decision/quickstart.md` for testing pipeline execution with curl examples

---

## Phase 4: User Story 2 - Handle Data Updates Efficiently

**Goal**: Implement update detection, smart catch-up processing, and update routing based on program stage

**Story**: As the Nexus system, I need to detect when source data is updated and process updates efficiently without discarding human work (manual enrichment, editorial review) so that information sheets stay current while preserving editorial effort.

**Why P2**: ~100 updates per week require efficient handling. Without this, either information sheets become stale or editorial team wastes effort re-reviewing unchanged content.

**Independent Test Criteria**:
- [ ] Updates are detected via checksum comparison
- [ ] Early-stage programs (ingestion, editorial_policy_validation, reconciliation) trigger full reprocess
- [ ] Late-stage programs (enrichment+) trigger smart catch-up
- [ ] Smart catch-up processes update to original stage in <5 minutes
- [ ] Original program data is preserved during update processing
- [ ] Update events are created and tracked in database
- [ ] Multiple rapid updates are processed sequentially
- [ ] Integration test validates update detection and routing

### Tasks

- [ ] T046 [US2] Create checksum calculation utility at `apps/orchestration/src/utils/checksum.py` implementing SHA-256 hash of Data Inclusion service JSON (excluding metadata fields)
- [ ] T047 [US2] Create update detector service at `apps/orchestration/src/services/update_detector.py` with methods: detect_updates, compare_checksums, determine_update_strategy
- [ ] T048 [US2] Implement update routing logic at `apps/orchestration/src/services/update_router.py` determining full_reprocess vs smart_catchup based on original_stage
- [ ] T049 [US2] Create smart catch-up orchestrator at `apps/orchestration/src/services/smart_catchup.py` that processes updates through pipeline stages until reaching original stage
- [ ] T050 [US2] Create update API endpoints at `apps/orchestration/src/api/updates.py`: POST /updates/detect (detect), POST /updates/{id}/smart-catchup (execute)
- [ ] T051 [US2] Implement update event creation and tracking at `apps/orchestration/src/services/update_service.py` with methods: create_update_event, get_update_event, update_processing_status
- [ ] T052 [US2] Create unit tests for checksum calculation at `apps/orchestration/tests/unit/utils/test_checksum.py` with various Data Inclusion service JSON samples
- [ ] T053 [US2] Create unit tests for update detector at `apps/orchestration/tests/unit/services/test_update_detector.py` validating checksum comparison and strategy determination
- [ ] T054 [US2] Create unit tests for smart catch-up at `apps/orchestration/tests/unit/services/test_smart_catchup.py` validating stage progression and data preservation
- [ ] T055 [US2] Create integration tests for update handling at `apps/orchestration/tests/integration/test_update_handling.py` with real update scenarios
- [ ] T056 [US2] Create contract tests for update API at `apps/orchestration/tests/contract/test_update_api.py` validating request/response schemas
- [ ] T057 [US2] Create n8n workflow at `specs/002-orchestration-decision/workflows/update-detection.json` that detects updates and routes to appropriate handler
- [ ] T058 [US2] Create n8n workflow at `specs/002-orchestration-decision/workflows/smart-catchup.json` that executes smart catch-up processing
- [ ] T059 [US2] Create test data for updates at `apps/orchestration/tests/fixtures/test_updates.json` with various update scenarios (early stage, late stage, rapid updates)

---

## Phase 5: User Story 3 - Review and Approve Update Diffs

**Goal**: Implement diff generation, risk scoring, and editorial review workflow

**Story**: As a Réfugiés.info editor, I need to review diffs between original and updated information sheets so that I can approve changes without re-reviewing the entire content.

**Why P3**: Enables editorial team to manage updates efficiently. Builds on P2 by adding human oversight for high-risk changes.

**Independent Test Criteria**:
- [ ] Diffs are generated comparing original and updated data
- [ ] Changes are classified by type (addition, deletion, minor edit, major edit)
- [ ] Risk scores are calculated based on change characteristics
- [ ] Low-risk updates (<0.5) are auto-approved without review
- [ ] High-risk updates (>0.8) are flagged for mandatory review
- [ ] Medium-risk updates (0.5-0.8) are sampled for review (20% sampling rate)
- [ ] Editors can view diffs sorted by priority (high-risk first)
- [ ] Editors can approve, reject, or manually edit diffs
- [ ] Review actions are tracked with reviewer ID and timestamp
- [ ] Concurrent edits are prevented via optimistic locking
- [ ] Integration test validates complete diff review workflow

### Tasks

- [ ] T060 [US3] Create diff generation service at `apps/orchestration/src/services/diff_generator.py` using deepdiff library for field-level comparison
- [ ] T061 [US3] Implement change classification at `apps/orchestration/src/services/change_classifier.py` with methods: classify_addition, classify_deletion, classify_edit, determine_edit_type
- [ ] T062 [US3] Create risk scoring algorithm at `apps/orchestration/src/services/risk_scorer.py` implementing weighted scoring: deletions (0.9), major_edits_critical (0.8), major_edits_normal (0.6), additions (0.5), minor_edits (0.2)
- [ ] T063 [US3] Implement priority assignment at `apps/orchestration/src/services/priority_assigner.py` mapping risk scores to priorities: low (<0.5), medium (0.5-0.8), high (>0.8)
- [ ] T064 [US3] Create auto-approval logic at `apps/orchestration/src/services/auto_approver.py` for low-risk diffs (<0.5)
- [ ] T065 [US3] Create sampling logic at `apps/orchestration/src/services/sampling_service.py` for medium-risk diffs (0.5-0.8) with configurable sampling rate (default 20%)
- [ ] T066 [US3] Create diff API endpoints at `apps/orchestration/src/api/diffs.py`: GET /diffs (list), GET /diffs/{id} (get), POST /diffs/{id}/approve (approve), POST /diffs/{id}/reject (reject), POST /diffs/{id}/edit (edit)
- [ ] T067 [US3] Implement optimistic locking at `apps/orchestration/src/db/repositories/diff_repository.py` to prevent concurrent edits
- [ ] T068 [US3] Create Supabase Auth integration at `apps/orchestration/src/auth/supabase_auth.py` for editorial team authentication
- [ ] T069 [US3] Implement RBAC at `apps/orchestration/src/auth/rbac.py` restricting diff review interface access to authorized editors
- [ ] T070 [US3] Create unit tests for diff generation at `apps/orchestration/tests/unit/services/test_diff_generator.py` with various data samples
- [ ] T071 [US3] Create unit tests for risk scoring at `apps/orchestration/tests/unit/services/test_risk_scorer.py` validating score calculations
- [ ] T072 [US3] Create unit tests for auto-approval at `apps/orchestration/tests/unit/services/test_auto_approver.py` validating low-risk detection
- [ ] T073 [US3] Create unit tests for sampling at `apps/orchestration/tests/unit/services/test_sampling_service.py` validating sampling logic
- [ ] T074 [US3] Create integration tests for diff review workflow at `apps/orchestration/tests/integration/test_diff_review.py` with real editorial scenarios
- [ ] T075 [US3] Create contract tests for diff API at `apps/orchestration/tests/contract/test_diff_api.py` validating request/response schemas
- [ ] T076 [US3] Create Streamlit diff review UI at `apps/diff-review/app.py` with authentication, diff queue, side-by-side viewer, approval controls
- [ ] T077 [US3] Create Streamlit components at `apps/diff-review/components/` for diff viewer, approval controls, audit trail
- [ ] T078 [US3] Create Streamlit configuration at `apps/diff-review/.streamlit/config.toml` with theme and layout settings
- [ ] T079 [US3] Create Streamlit tests at `apps/diff-review/tests/test_app.py` validating UI functionality
- [ ] T080 [US3] Create n8n workflow at `specs/002-orchestration-decision/workflows/diff-generation.json` that generates diffs and routes to review queue

---

## Phase 6: User Story 4 - Monitor Pipeline Execution

**Goal**: Implement monitoring dashboard, metrics collection, and operational visibility

**Story**: As a Nexus operator, I need to monitor pipeline execution status and identify failures so that I can ensure information sheets are being processed and published successfully.

**Why P4**: Operational visibility is important but not blocking for MVP. Can initially rely on database queries and logs.

**Independent Test Criteria**:
- [ ] Operators can view current status of all programs (stage, success/failure, processing time)
- [ ] Failed programs display error messages and input data
- [ ] Performance metrics are collected per stage (processing time, throughput, error rates)
- [ ] Operators can trigger manual retry of failed programs
- [ ] Monitoring dashboard displays real-time metrics
- [ ] Alerts are generated for pipeline failures and SLA violations

### Tasks

- [ ] T081 [US4] Create metrics collection service at `apps/orchestration/src/services/metrics_service.py` with methods: record_workflow_metric, record_stage_metric, get_metrics
- [ ] T082 [US4] Create monitoring API endpoints at `apps/orchestration/src/api/monitoring.py`: GET /metrics (get metrics), GET /workflows/failed (list failed), POST /workflows/{id}/retry (manual retry)
- [ ] T083 [US4] Create monitoring dashboard at `apps/monitoring/app.py` using Streamlit displaying workflow status, metrics, failed programs
- [ ] T084 [US4] Create dashboard components at `apps/monitoring/components/` for status table, metrics charts, error details
- [ ] T085 [US4] Create alert service at `apps/orchestration/src/services/alert_service.py` for pipeline failures and SLA violations
- [ ] T086 [US4] Create unit tests for metrics service at `apps/orchestration/tests/unit/services/test_metrics_service.py`
- [ ] T087 [US4] Create integration tests for monitoring at `apps/orchestration/tests/integration/test_monitoring.py`
- [ ] T088 [US4] Create contract tests for monitoring API at `apps/orchestration/tests/contract/test_monitoring_api.py`

---

## Phase 7: Polish & Cross-Cutting Concerns

**Goal**: Complete testing, documentation, observability, and production readiness

**Independent Test Criteria**:
- [ ] All unit tests pass with >80% code coverage
- [ ] All integration tests pass with real Supabase instance
- [ ] All contract tests validate API schemas
- [ ] Structured logging is configured and working
- [ ] Error handling is comprehensive and tested
- [ ] Documentation is complete and accurate
- [ ] CI/CD pipeline is configured

### Tasks

- [ ] T089 Create comprehensive test suite documentation at `apps/orchestration/docs/testing.md` with testing strategy and examples
- [ ] T090 [P] Create structured logging configuration at `apps/orchestration/src/utils/logging.py` with JSON output and correlation IDs
- [ ] T091 [P] Create error handling middleware at `apps/orchestration/src/middleware/error_handler.py` with proper HTTP status codes and error responses
- [ ] T092 [P] Create request logging middleware at `apps/orchestration/src/middleware/request_logger.py` with correlation ID tracking
- [ ] T093 Create API documentation at `apps/orchestration/docs/api.md` with endpoint descriptions and examples
- [ ] T094 Create deployment guide at `docs/deployment.md` with production setup instructions
- [ ] T095 Create troubleshooting guide at `docs/troubleshooting.md` with common issues and solutions
- [ ] T096 Create architecture documentation at `docs/architecture.md` explaining system design and component interactions
- [ ] T097 [P] Create GitHub Actions CI/CD workflow at `.github/workflows/orchestration-tests.yml` running tests on pull requests
- [ ] T098 [P] Create GitHub Actions deployment workflow at `.github/workflows/orchestration-deploy.yml` for production deployment
- [ ] T099 Create pre-commit hooks configuration at `.pre-commit-config.yaml` for code quality checks
- [ ] T100 Create code coverage reporting at `apps/orchestration/coverage.ini` with coverage thresholds
- [ ] T101 Create performance benchmarks at `apps/orchestration/tests/benchmarks/test_performance.py` validating <5min smart catch-up
- [ ] T102 Create load testing script at `apps/orchestration/tests/load/load_test.py` validating 100 concurrent programs
- [ ] T103 Create end-to-end test scenario at `apps/orchestration/tests/e2e/test_complete_workflow.py` validating entire system
- [ ] T104 Create production readiness checklist at `docs/production-readiness.md` with deployment verification steps
- [ ] T105 Create monitoring setup guide at `docs/monitoring-setup.md` with metrics and alerting configuration
- [ ] T106 Create n8n deployment guide at `docs/n8n-deployment.md` with workflow import and configuration steps
- [ ] T107 Create Streamlit deployment guide at `docs/streamlit-deployment.md` for diff review and monitoring UIs
- [ ] T108 Update main README.md with orchestration feature overview and quick links to documentation

---

## Note on AI Processing Tasks

**Tasks T109-T121 (AI Prompts for Enrichment, Langage Clair, Translation)** are out of scope for the 002-orchestration-decision feature and should be implemented as part of separate feature branches:
- `004-enrichment-ai` (enrichment service implementation)
- `005-langage-clair-ai` (langage clair service implementation)
- `006-translation-ai` (translation service implementation)

The orchestration feature (002) provides the infrastructure and pipeline framework; AI service implementations are separate features that will integrate with the orchestration layer via the stage executor pattern (T034).

These tasks are included here for reference but should not be implemented as part of 002-orchestration-decision.

---

## Dependency Graph

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational)
    ↓
Phase 3 (US1: Pipeline Processing) ← Can start after Phase 2
    ↓
Phase 4 (US2: Update Handling) ← Depends on Phase 3 (needs workflow infrastructure)
    ↓
Phase 5 (US3: Diff Review) ← Depends on Phase 4 (needs update events)
    ↓
Phase 6 (US4: Monitoring) ← Can start after Phase 3 (independent of US2/US3)
    ↓
Phase 7 (Polish) ← Depends on all previous phases
```

## Parallel Execution Opportunities

**Within Phase 1**:
- T003-T004: Configure dependencies (Python + Node.js in parallel)
- T007, T010: Create scripts and configs (independent)

**Within Phase 2**:
- T014-T018: Create repositories (independent, can parallelize)
- T020-T022: Create Pydantic models (independent, can parallelize)

**Within Phase 3**:
- T035-T036: Create unit tests (independent)
- T039-T040: Create n8n workflows and documentation (can start after T028-T034)

**Within Phase 4**:
- T052-T054: Create unit tests (independent)
- T057-T058: Create n8n workflows (can parallelize)

**Within Phase 5**:
- T070-T073: Create unit tests (independent)
- T076-T078: Create Streamlit UI (can parallelize with services)

**Within Phase 7**:
- T090-T092: Create middleware (independent)
- T097-T098: Create CI/CD workflows (independent)

**Within AI Prompts Phase**:
- T110, T112, T114, T116, T118: Create tests (independent, can parallelize)
- T111, T113, T115: Create services (can parallelize after T109)

## MVP Scope Recommendation

**Minimum Viable Product** (Weeks 1-4):
- Phase 1: Setup & Infrastructure (1 week)
- Phase 2: Foundational Services (1 week)
- Phase 3: User Story 1 - Process new programs (2 weeks)

**Result**: System can process new programs through all 8 pipeline stages (ingestion → editorial policy validation → reconciliation → enrichment → langage clair → translation → validation → publication) with state tracking and error handling.

**Phase 2 MVP** (Weeks 5-8):
- Phase 4: User Story 2 - Handle updates (2 weeks)
- Phase 5: User Story 3 - Diff review (2 weeks)

**Result**: System can detect updates, process them efficiently, and route to editorial review.

**Phase 3 MVP** (Weeks 9-10):
- Phase 6: User Story 4 - Monitoring (1 week)
- Phase 7: Polish & Testing (1 week)

**Result**: Complete, production-ready system with operational visibility.

---

## Success Criteria Mapping

| Success Criterion | Related Tasks | Validation Method |
|-------------------|---------------|-------------------|
| SC-001: Process program through 7 stages in <24h | T028-T042 | Integration test in T037 |
| SC-002: Handle 100 concurrent programs | T028-T037 | Load test in T102 |
| SC-003: 95% transient error recovery | T030, T035-T036 | Unit tests in T035-T036 |
| SC-004: Detect 100% of updates via checksum | T046-T053 | Unit tests in T052 |
| SC-005: Smart catch-up in <5 minutes | T049, T055 | Integration test in T055 |
| SC-006: <1 hour/week editorial review (20% sampling) | T065, T073 | Unit tests in T073 |
| SC-007: High-risk flags with 100% accuracy | T062, T071 | Unit tests in T071 |
| SC-008: Low-risk auto-approval <5% false positive | T064, T072 | Unit tests in T072 |
| SC-009: Review diff in <3 minutes | T076-T079 | Streamlit tests in T079 |
| SC-010: Track complete data lineage | T090, T095 | Documentation in T095 |
| SC-011: Diagnose failures in <5 minutes | T081-T087 | Integration test in T087 |
| SC-012: 99% uptime | T097-T098, T104 | Production monitoring |

---

## Implementation Notes

### TDD Compliance (CAR-016 to CAR-019)

All tasks follow test-driven development:
- Unit tests written before service implementation
- Integration tests validate end-to-end flows
- Contract tests ensure API compatibility
- Coverage threshold: >80% for all modules

### Constitution Alignment

**Principle II (Pipeline Modularity - CAR-001 to CAR-004)**:
- Each service is independently testable (T035-T036, T052-T054, etc.)
- Well-defined contracts via Pydantic models (T019-T022)
- Error isolation prevents cascading failures (T034)
- Partial replay supported via stage executor (T033)

**Principle VI (Observability - CAR-005 to CAR-009)**:
- Structured logging configured (T090)
- Data lineage tracked via workflow_runs and stage_executions
- Performance metrics collected (T081)
- Alerts for failures and SLA violations (T085)

**Principle VII (Incremental Delivery - CAR-010 to CAR-012)**:
- Orchestration independent of stage implementations (T028-T042)
- Update handling delivered incrementally (Phase 4)
- Each user story independently testable (T037, T055, T074, T087)

**Principle IX (User-Centered Development - CAR-013 to CAR-015)**:
- Diff review UI designed for editorial team (T076-T079)
- Risk scoring tunable based on feedback (T062)
- Metrics track review efficiency (T081)

### Database Migrations

All database changes tracked in `supabase/migrations/` (centralized Supabase directory):
- `001_init_schema.sql`: Initial schema with all tables
- Future migrations follow sequential numbering
- Use Supabase CLI for migration management: `supabase migration new <name>`

### Configuration Management

Environment variables managed via `.env` file:
- Supabase credentials
- Data Inclusion API URL
- Vercel AI Gateway credentials
- Feature flags for gradual rollout

### Error Handling Strategy

Comprehensive error handling across all layers:
- Repository layer: Database errors wrapped in custom exceptions
- Service layer: Business logic errors with context
- API layer: HTTP errors with proper status codes
- Retry logic: Exponential backoff for transient errors

### Testing Strategy

Three-tier testing approach:
- **Unit tests**: Service logic with mocked dependencies
- **Integration tests**: End-to-end flows with test Supabase
- **Contract tests**: API schemas validated against OpenAPI spec

---

## Getting Started

1. **Start with Phase 1**: Set up project structure and dependencies
2. **Complete Phase 2**: Implement database layer and foundational services
3. **Implement Phase 3**: Build core pipeline orchestration (MVP)
4. **Extend with Phase 4-5**: Add update handling and diff review
5. **Add Phase 6**: Implement monitoring for operational visibility
6. **Polish with Phase 7**: Complete testing, documentation, and deployment

Each phase is independently deployable and testable. Teams can work in parallel on different phases after Phase 2 is complete.
