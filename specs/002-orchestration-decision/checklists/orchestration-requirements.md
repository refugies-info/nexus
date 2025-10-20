# Checklist: Orchestration & Update Handling Requirements

**Purpose**: Unit tests for requirements quality in the Pipeline Orchestration & Update Handling feature
**Audience**: Author (self-review before PR)
**Scope**: Architecture + Update Handling + Implementation Readiness
**Emphasis**: Update handling correctness (routing, diff generation, risk scoring)

---

## Architecture Requirements

### CHK001: n8n + FastAPI Integration Pattern [Completeness]
Are the integration touchpoints between n8n and FastAPI clearly specified?
- [ ] HTTP request node pattern documented (n8n → FastAPI endpoints)
- [ ] Correlation ID propagation defined (linking n8n executions to Python logs)
- [ ] Idempotency key strategy specified for retry safety
- [ ] Response format contract defined (status codes, error handling)

**Reference**: [Research §1](../research.md#1-n8n-integration-architecture)

---

### CHK002: Supabase Schema Normalization [Clarity]
Is the normalized schema structure unambiguous and complete?
- [ ] All five core tables defined with field types and constraints
- [ ] Foreign key relationships explicitly documented (1:N cardinality)
- [ ] JSONB column purposes and content structure specified (not just "flexible storage")
- [ ] Enum values for status/stage fields exhaustively listed

**Reference**: [Data Model §1-5](../data-model.md#entities)

---

### CHK003: FastAPI Service Layer Pattern [Consistency]
Do the service, repository, and API layers follow consistent architectural principles?
- [ ] Service layer encapsulates business logic (not database queries)
- [ ] Repository layer abstracts Supabase access (enables mocking)
- [ ] Pydantic models defined for all request/response types
- [ ] Dependency injection pattern used consistently across endpoints

**Reference**: [Research §3](../research.md#3-fastapi-service-architecture)

---

## Update Handling Strategy

### CHK004: Update Detection Mechanism [Completeness]
Is the checksum-based update detection fully specified?
- [ ] Checksum calculation algorithm documented (SHA-256, field normalization)
- [ ] Fields included in checksum explicitly listed (content fields)
- [ ] Fields excluded from checksum justified (metadata fields: source, structure_id, lien_mobilisation)
- [ ] Collision resistance and UTF-8 handling addressed

**Reference**: [Research §2 - Checksum Calculation Strategy](../research.md#checksum-calculation-strategy)

---

### CHK005: Update Routing Logic [Clarity]
Is the routing decision unambiguous for all pipeline stages?
- [ ] Routing rules defined for each stage (ingestion → publication)
- [ ] Decision criteria explicit: `original_stage` IN ('ingestion', 'reconciliation') → `full_reprocess`
- [ ] Decision criteria explicit: `original_stage` IN ('enrichment', ..., 'validation') → `smart_catchup`
- [ ] Edge case: What happens if update detected at publication stage? (Specified or gap?)

**Reference**: [Data Model §4 - original_stage Field Lifecycle](../data-model.md#original_stage-field-lifecycle)

---

### CHK006: Smart Catch-Up Orchestration [Completeness]
Is the AI-accelerated catch-up process fully specified?
- [ ] Stages included in catch-up pipeline defined (ingestion through target stage)
- [ ] "Fast mode" vs "normal mode" processing criteria specified (which stages use AI acceleration?)
- [ ] Quality threshold differences between modes documented
- [ ] Failure handling during catch-up specified (retry logic, fallback)

**Reference**: [UPDATE-HANDLING-SUMMARY §Smart Catch-Up](../UPDATE-HANDLING-SUMMARY.md#smart-catch-up)

---

### CHK007: Diff Generation Algorithm [Clarity]
Is the field-level diff classification unambiguous?
- [ ] Change types exhaustively defined: addition, deletion, minor_edit, major_edit
- [ ] Classification criteria specified for each type (e.g., Levenshtein distance threshold for minor vs major)
- [ ] Critical fields list documented (title, description, eligibility, etc.)
- [ ] Structured diff output format specified (JSON schema or example)

**Reference**: [Research §4 - Diff Generation Algorithm](../research.md#4-diff-generation-algorithm)

---

### CHK008: Risk Scoring Formula [Clarity]
Is the risk calculation deterministic and reproducible?
- [ ] Risk score formula explicitly stated with weights
- [ ] Weight justification provided (why deletion = 0.9, addition = 0.5, etc.)
- [ ] Risk score range defined (0.0-1.0 confirmed)
- [ ] Edge case: What if no changes detected? (Risk score = 0.0?)

**Reference**: [Research §4 - Risk Scoring Formula](../research.md#risk-scoring-formula)

---

### CHK009: Risk-Based Sampling Rules [Completeness]
Are the auto-approval thresholds and sampling rates fully specified?
- [ ] High-risk threshold defined (>0.8 = always review, 100%)
- [ ] Medium-risk threshold defined (0.5-0.8 = sample 20%)
- [ ] Low-risk threshold defined (<0.5 = auto-approve, 0%)
- [ ] Sampling method specified (random? deterministic? seeded?)
- [ ] Audit trail requirement for auto-approvals documented

**Reference**: [UPDATE-HANDLING-SUMMARY §Risk-Based Sampling](../UPDATE-HANDLING-SUMMARY.md#risk-based-sampling)

---

### CHK010: Diff Review Workflow [Completeness]
Is the human-in-the-loop approval process fully specified?
- [ ] Review states exhaustively defined: pending, approved, rejected, edited
- [ ] Approval actions specified: approve all, reject all, manual edit
- [ ] Merge logic after approval specified (how are changes applied?)
- [ ] Conflict resolution if human edits conflict with pipeline state (specified or gap?)

**Reference**: [Data Model §update_diffs](../data-model.md#5-update_diffs)

---

## Data Model Validation

### CHK011: `information_sheets` Stage Progression [Consistency]
Are stage transitions and data preservation consistent?
- [ ] Stage enum values consistent across all tables (workflow_runs, stage_executions, information_sheets, update_events)
- [ ] Stage-specific JSONB columns (ingested_data, reconciled_data, enriched_data, etc.) align with stage enum
- [ ] Data immutability rule: once stage-specific data is set, does it remain unchanged? (Specified or gap?)
- [ ] `current_stage` vs `original_stage` distinction clear (mutable vs immutable)

**Reference**: [Data Model §3 - information_sheets](../data-model.md#3-information_sheets)

---

### CHK012: `update_events.original_stage` Immutability [Clarity]
Is the immutability constraint and its purpose unambiguous?
- [ ] Immutability rule explicitly stated: "Once set, NEVER changes"
- [ ] Purpose documented: "Snapshot at update detection time"
- [ ] Contrast with `information_sheets.current_stage` (mutable) clearly explained
- [ ] Audit trail use case documented (why historical record matters)

**Reference**: [Data Model §4 - original_stage Field Lifecycle](../data-model.md#original_stage-field-lifecycle)

---

### CHK013: Validation Rules Completeness [Completeness]
Are all data integrity constraints specified?
- [ ] Checksum constraint: `updated_checksum` ≠ `original_checksum` (specified)
- [ ] Risk score constraint: 0.0 ≤ `risk_score` ≤ 1.0 (specified)
- [ ] Priority constraint: `priority` matches risk_score ranges (specified)
- [ ] Review audit constraint: `reviewed_by` and `reviewed_at` both NULL or both NOT NULL (specified)
- [ ] Stage progression constraint: `current_stage` can only advance, never regress (specified or gap?)

**Reference**: [Data Model §Validation Rules](../data-model.md#validation-rules)

---

## API & Contract Specifications

### CHK014: Orchestration API Endpoints [Completeness]
Are all required endpoints specified in the OpenAPI contract?
- [ ] Workflow execution endpoint: POST /api/workflows/execute
- [ ] Workflow status endpoint: GET /api/workflows/{workflow_id}/status
- [ ] Diff listing endpoint: GET /api/diffs (with filtering by status, priority)
- [ ] Diff approval endpoints: POST /api/diffs/{diff_id}/approve, reject
- [ ] Request/response schemas defined for each endpoint

**Reference**: [Quickstart §Key Endpoints](../quickstart.md#key-endpoints)

---

### CHK015: Error Handling Contract [Clarity]
Are error responses and retry behavior specified?
- [ ] HTTP status codes documented for success (200/201) and failures (4xx/5xx)
- [ ] Error response format specified (error code, message, details)
- [ ] Transient error classification defined (which errors trigger retries?)
- [ ] Max retry attempts and backoff strategy specified (exponential backoff, max 10 retries)

**Reference**: [Research §7 - Error Handling & Retry Strategy](../research.md#7-error-handling--retry-strategy)

---

## Implementation Readiness

### CHK016: Quickstart Prerequisites [Completeness]
Are all setup steps and dependencies clearly documented?
- [ ] Python version requirement specified (3.12+)
- [ ] Node.js version requirement specified (22+)
- [ ] Docker requirement for n8n and Supabase documented
- [ ] Environment variables (.env) fully documented with examples

**Reference**: [Quickstart §Prerequisites](../quickstart.md#prerequisites)

---

### CHK017: Database Schema Migration Path [Completeness]
Is the schema deployment strategy fully specified?
- [ ] Phase 1 tables documented (workflow_runs, stage_executions, information_sheets)
- [ ] Phase 2 tables documented (update_events, update_diffs)
- [ ] Migration order specified (dependencies between phases)
- [ ] Rollback strategy documented (if needed)

**Reference**: [Data Model §Migration Strategy](../data-model.md#migration-strategy)

---

### CHK018: Observability & Monitoring [Completeness]
Are logging, metrics, and debugging requirements specified?
- [ ] Correlation ID propagation documented (n8n → Python services → logs)
- [ ] Structured logging format specified (JSON with timestamp, level, correlation_id, etc.)
- [ ] Key metrics defined (workflow success rate, update processing time, diff review time)
- [ ] Dashboard requirements specified (operator dashboard, editorial dashboard)

**Reference**: [Research §8 - Observability & Monitoring](../research.md#8-observability--monitoring)

---

### CHK019: n8n Workflow Export & Version Control [Completeness]
Is the workflow management strategy fully specified?
- [ ] Workflow export format documented (JSON)
- [ ] Workflow organization structure defined (pipeline-orchestration.json, update-handler.json, etc.)
- [ ] Git version control strategy documented
- [ ] CI/CD deployment process specified (validation, deployment, smoke tests)

**Reference**: [Research §6 - n8n Workflow Export & Version Control](../research.md#6-n8n-workflow-export--version-control)

---

## Ambiguities & Gaps

### CHK020: Unresolved Questions [Ambiguities & Conflicts]
Are there any underspecified areas that could cause implementation confusion?
- [ ] **Clarification**: Race condition handling specified - if program updated during stage processing, that stage workflow must be canceled
- [ ] **Deferral**: Fast/normal mode quality thresholds require experimentation - deferred to Phase 2 optimization
- [ ] **SLA**: Maximum 24-hour latency for update detection → diff generation (P50: 10-15 min, P95: 1-2 hours, P99: 24 hours)
- [ ] **Policy**: Human edits to diffs supersede subsequent pipeline results; downstream stages may require re-execution if inputs changed; audit trail required for all human edits (edited_by, edited_at, original_value, new_value)
- [ ] **Clarification**: Streamlit diff review UI included in Phase 1 MVP (simple version for early iteration); enhanced UI with advanced features deferred to Phase 2

**Status**: ✅ All 5 items clarified. Ambiguities resolved. Ready for implementation.

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
