# Checklist: Orchestration & Update Handling Requirements

**Purpose**: Unit tests for requirements quality in the Pipeline Orchestration & Update Handling feature
**Audience**: Author (self-review before PR)
**Scope**: Architecture + Update Handling + Implementation Readiness
**Emphasis**: Update handling correctness (routing, diff generation, risk scoring)

---

## Architecture Requirements

### CHK001: n8n + FastAPI Integration Pattern [Completeness]
Are the integration touchpoints between n8n and FastAPI clearly specified?
- [x] HTTP request node pattern documented (n8n → FastAPI endpoints)
- [x] Correlation ID propagation defined (linking n8n executions to Python logs)
- [x] Idempotency key strategy specified for retry safety
- [x] Response format contract defined (status codes, error handling)

**Reference**: [Research §1](../research.md#1-n8n-integration-architecture) | [OpenAPI Spec](../contracts/orchestration-api.yaml)

---

### CHK002: Supabase Schema Normalization [Clarity]
Is the normalized schema structure unambiguous and complete?
- [x] All five core tables defined with field types and constraints
- [x] Foreign key relationships explicitly documented (1:N cardinality)
- [x] JSONB column purposes and content structure specified (not just "flexible storage")
- [x] Enum values for status/stage fields exhaustively listed

**Reference**: [Data Model §1-5](../data-model.md#entities)

---

### CHK003: FastAPI Service Layer Pattern [Consistency]
Do the service, repository, and API layers follow consistent architectural principles?
- [x] Service layer encapsulates business logic (not database queries)
- [x] Repository layer abstracts Supabase access (enables mocking)
- [x] Pydantic models defined for all request/response types
- [x] Dependency injection pattern used consistently across endpoints

**Reference**: [Research §3](../research.md#3-fastapi-service-architecture) | [OpenAPI Schemas](../contracts/orchestration-api.yaml#L383) | [Tasks T020-T023](../tasks.md#phase-2-foundational-services--database-layer)

**Note**: Pydantic model schemas are formally defined in the OpenAPI contract. Implementation files (T020-T023) will be created during Phase 2 based on these specifications.

---

## Update Handling Strategy

### CHK004: Update Detection Mechanism [Completeness]
Is the checksum-based update detection fully specified?
- [x] Checksum calculation algorithm documented (SHA-256, field normalization)
- [x] Fields included in checksum explicitly listed (content fields)
- [x] Fields excluded from checksum justified (metadata fields: source, structure_id, lien_mobilisation)
- [x] Collision resistance and UTF-8 handling addressed

**Reference**: [Research §2 - Checksum Calculation Strategy](../research.md#checksum-calculation-strategy)

---

### CHK005: Update Routing Logic [Clarity]
Is the routing decision unambiguous for all pipeline stages?
- [x] Routing rules defined for each stage (ingestion → publication)
- [x] Decision criteria explicit: `original_stage` IN ('ingestion', 'reconciliation') → `full_reprocess`
- [x] Decision criteria explicit: `original_stage` IN ('enrichment', ..., 'validation') → `smart_catchup`
- [x] Edge case: What happens if update detected at publication stage? (Specified)

**Reference**: [Data Model §4 - original_stage Field Lifecycle](../data-model.md#original_stage-field-lifecycle) | [Published Record Updates](../PUBLISHED-RECORD-UPDATES.md)

**Publication Stage Handling**: Updates to published records route to smart_catchup (same as late-stage updates), process through full pipeline, generate diff, require human review (always, no auto-approval), and republish if approved. Leverages existing pipeline transformations for consistency.

---

### CHK006: Smart Catch-Up Orchestration [Completeness]
Is the AI-accelerated catch-up process fully specified?
- [x] Stages included in catch-up pipeline defined (ingestion through target stage)
- [x] "Fast mode" vs "normal mode" processing criteria specified (which stages use AI acceleration?)
- [x] Quality threshold differences between modes documented
- [x] Failure handling during catch-up specified (retry logic, fallback)

**Reference**: [UPDATE-HANDLING-SUMMARY §Smart Catch-Up](../UPDATE-HANDLING-SUMMARY.md#smart-catch-up)

---

### CHK007: Diff Generation Algorithm [Clarity]
Is the field-level diff classification unambiguous?
- [x] Change types exhaustively defined: addition, deletion, minor_edit, major_edit
- [x] Classification criteria specified for each type (e.g., Levenshtein distance threshold for minor vs major)
- [x] Critical fields list documented (title, description, eligibility, etc.)
- [ ] Structured diff output format specified (JSON schema or example)

**Reference**: [Research §4 - Diff Generation Algorithm](../research.md#4-diff-generation-algorithm) | [Data Model §5](../data-model.md#5-update_diffs) | [OpenAPI DiffResponse](../contracts/orchestration-api.yaml#L583)

**Gap**: High-level structure defined (additions/deletions/minor_edits/major_edits arrays) but detailed field-level schema missing. Needs specification during implementation (T060 - Diff Generation Service).

---

### CHK008: Risk Scoring Formula [Clarity]
Is the risk calculation deterministic and reproducible?
- [x] Risk score formula explicitly stated with weights
- [x] Weight justification provided (why deletion = 0.9, addition = 0.5, etc.)
- [x] Risk score range defined (0.0-1.0 confirmed)
- [x] Edge case: What if no changes detected? (Risk score = 0.0?)

**Reference**: [Research §4 - Risk Scoring Formula](../research.md#risk-scoring-formula)

---

### CHK009: Risk-Based Sampling Rules [Completeness]
Are the auto-approval thresholds and sampling rates fully specified?
- [x] High-risk threshold defined (>0.8 = always review, 100%)
- [x] Medium-risk threshold defined (0.5-0.8 = sample 20%)
- [x] Low-risk threshold defined (<0.5 = auto-approve, 0%)
- [x] Sampling method specified (random? deterministic? seeded?)
- [ ] Audit trail requirement for auto-approvals documented

**Reference**: [UPDATE-HANDLING-SUMMARY §Risk-Based Sampling](../UPDATE-HANDLING-SUMMARY.md#risk-based-sampling) | [Data Model §update_diffs](../data-model.md#5-update_diffs)

**Gap - Audit Trail for Auto-Approvals**: Current schema only tracks human reviews (`reviewed_by`, `reviewed_at`). Missing fields for auto-approvals:
- [ ] `approval_type` (human | system) - Distinguish human vs auto-approval
- [ ] `approval_reason` (risk_score_threshold | manual_override | etc.) - Why was it approved?
- [ ] `approved_at` (TIMESTAMPTZ) - When was it approved (separate from review_at)?
- [ ] `approval_metadata` (JSONB) - Algorithm version, thresholds used, risk score value
- [ ] `approved_by` (TEXT) - System identifier (e.g., "auto-approver-v1") for auto-approvals

**Rationale**: Compliance with CAR-005 (Observability) and GDPR audit trail requirements. Auto-approvals must be fully traceable and reversible for regulatory compliance and debugging.

**Implementation**: Extend `update_diffs` schema during Phase 2 (Task T064 - Auto-Approval Logic).

---

### CHK010: Diff Review Workflow [Completeness]
Is the human-in-the-loop approval process fully specified?
- [x] Review states exhaustively defined: pending, approved, rejected, edited
- [x] Approval actions specified: approve all, reject all, manual edit
- [x] Merge logic after approval specified (how are changes applied?)
- [ ] Conflict resolution if human edits conflict with pipeline state (partial implementation)

**Current Implementation**:
- Optimistic locking via `updated_at` timestamps
- Manual conflict resolution through `edited` state

**Gaps**:
- No formal merge strategies (theirs/ours/custom)
- No conflict resolution logging
- No conflict visualization in Streamlit UI
- No automatic retry workflow

**Implementation Task**: T092 (Phase 3 - Weeks 12-15)

**Reference**: [Data Model §update_diffs](../data-model.md#5-update_diffs)

---

## Data Model Validation

### CHK011: `information_sheets` Stage Progression [Consistency]
Are stage transitions and data preservation consistent?
- [x] Stage enum values consistent across all tables (workflow_runs, stage_executions, information_sheets, update_events)
- [x] Stage-specific JSONB columns (ingested_data, reconciled_data, enriched_data, etc.) align with stage enum
- [x] Data immutability rule: once stage-specific data is set, does it remain unchanged? (Specified or gap?)
- [x] `current_stage` vs `original_stage` distinction clear (mutable vs immutable)

**Reference**: [Data Model §3 - information_sheets](../data-model.md#3-information_sheets)

---

### CHK012: `update_events.original_stage` Immutability [Clarity]
Is the immutability constraint and its purpose unambiguous?
- [x] Immutability rule explicitly stated: "Once set, NEVER changes"
- [x] Purpose documented: "Snapshot at update detection time"
- [x] Contrast with `information_sheets.current_stage` (mutable) clearly explained
- [x] Audit trail use case documented (why historical record matters)

**Reference**: [Data Model §4 - original_stage Field Lifecycle](../data-model.md#original_stage-field-lifecycle)

---

### CHK013: Validation Rules Completeness [Completeness]
Are all data integrity constraints specified?
- [x] Checksum constraint: `updated_checksum` ≠ `original_checksum` (specified)
- [x] Risk score constraint: 0.0 ≤ `risk_score` ≤ 1.0 (specified)
- [x] Priority constraint: `priority` matches risk_score ranges (specified)
- [x] Review audit constraint: `reviewed_by` and `reviewed_at` both NULL or both NOT NULL (specified)
- [x] Stage progression constraint: `current_stage` can only advance, never regress (specified or gap?)

**Reference**: [Data Model §Validation Rules](../data-model.md#validation-rules)

---

## API & Contract Specifications

### CHK014: Orchestration API Endpoints [Completeness]
Are all required endpoints specified in the OpenAPI contract?
- [x] Workflow execution endpoint: POST /api/workflows/execute
- [x] Workflow status endpoint: GET /api/workflows/{workflow_id}/status
- [x] Diff listing endpoint: GET /api/diffs (with filtering by status, priority)
- [x] Diff approval endpoints: POST /api/diffs/{diff_id}/approve, reject
- [x] Request/response schemas defined for each endpoint

**Reference**: [Quickstart §Key Endpoints](../quickstart.md#key-endpoints)

---

### CHK015: Error Handling Contract [Clarity]
Are error responses and retry behavior specified?
- [x] HTTP status codes documented for success (200/201) and failures (4xx/5xx)
- [x] Error response format specified (error code, message, details)
- [x] Transient error classification defined (which errors trigger retries?)
- [x] Max retry attempts and backoff strategy specified (exponential backoff, max 10 retries)

**Reference**: [Research §7 - Error Handling & Retry Strategy](../research.md#7-error-handling--retry-strategy)

---

## Implementation Readiness

### CHK016: Quickstart Prerequisites [Completeness]
Are all setup steps and dependencies clearly documented?
- [x] Python version requirement specified (3.12+)
- [x] Node.js version requirement specified (22+)
- [x] Docker requirement for n8n and Supabase documented
- [x] Environment variables (.env) fully documented with examples

**Reference**: [Quickstart §Prerequisites](../quickstart.md#prerequisites)

---

### CHK017: Database Schema Migration Path [Completeness]
Is the schema deployment strategy fully specified?
- [x] Phase 1 tables documented (workflow_runs, stage_executions, information_sheets)
- [x] Phase 2 tables documented (update_events, update_diffs)
- [x] Migration order specified (dependencies between phases)
- [x] Rollback strategy documented (if needed)

**Reference**: [Data Model §Migration Strategy](../data-model.md#migration-strategy) | [Rollback Strategy](../ROLLBACK-STRATEGY.md)

**Strategy**: Forward-only migrations + Point-in-Time Recovery (PITR)
- Simple Supabase CLI migrations (immutable, sequential)
- PITR enabled for production (7-day retention, seconds granularity)
- Daily backups as secondary safety net
- RTO: 5-30 min | RPO: Seconds

---

### CHK018: Observability & Monitoring [Completeness]
Are logging, metrics, and debugging requirements specified?
- [x] Correlation ID propagation documented (n8n → Python services → logs)
- [x] Structured logging format specified (JSON with timestamp, level, correlation_id, etc.)
- [x] Key metrics defined (workflow success rate, update processing time, diff review time)
- [x] Dashboard requirements specified (operator dashboard, editorial dashboard)

**Reference**: [Research §8 - Observability & Monitoring](../research.md#8-observability--monitoring)

---

### CHK019: n8n Workflow Export & Version Control [Completeness]
Is the workflow management strategy fully specified?
- [x] Workflow export format documented (JSON)
- [x] Workflow organization structure defined (pipeline-orchestration.json, update-handler.json, etc.)
- [x] Git version control strategy documented
- [x] CI/CD deployment process specified (validation, deployment, smoke tests)

**Reference**: [Research §6 - n8n Workflow Export & Version Control](../research.md#6-n8n-workflow-export--version-control)

---

## Ambiguities & Gaps

### CHK020: Unresolved Questions [Ambiguities & Conflicts]
Are there any underspecified areas that could cause implementation confusion?
- [x] **Clarification**: Race condition handling specified - if program updated during stage processing, that stage workflow must be canceled
- [x] **Deferral**: Fast/normal mode quality thresholds require experimentation - deferred to Phase 2 optimization
- [x] **SLA**: Maximum 24-hour latency for update detection → diff generation (P50: 10-15 min, P95: 1-2 hours, P99: 24 hours)
- [x] **Policy**: Human edits to diffs supersede subsequent pipeline results; downstream stages may require re-execution if inputs changed; audit trail required for all human edits (edited_by, edited_at, original_value, new_value)
- [x] **Clarification**: Streamlit diff review UI included in Phase 1 MVP (simple version for early iteration); enhanced UI with advanced features deferred to Phase 2

**Status**: All 5 items clarified. Ambiguities resolved. Ready for implementation.

---

## Summary

**Total Items**: 20 (CHK001-CHK020)
**Categories**:
- Architecture Requirements: 3 items
- Update Handling Strategy: 7 items
- Data Model Validation: 3 items
- API & Contract Specifications: 2 items
- Implementation Readiness: 4 items
- Ambiguities & Gaps: 1 item

**Next Steps**:
1. Address any gaps identified in CHK020
2. Verify all references are accurate (spot-check 3-5 random references)
3. Use this checklist during PR review to validate requirements quality
4. Update checklist if new ambiguities emerge during implementation
