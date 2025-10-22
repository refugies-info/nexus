# Data Model: Pipeline Orchestration & Update Handling

**Feature**: Pipeline Orchestration & Update Handling
**Date**: 2025-10-20
**Database**: Supabase (PostgreSQL)

## Overview

This document defines the data model for pipeline orchestration state management. The model tracks workflow execution, stage progress, program data with progressive enhancement, update events, and diff review queue.

## Entity Relationship Diagram

```
┌─────────────────┐
│ workflow_runs   │
│─────────────────│
│ id (PK)         │
│ program_id      │◄────────┐
│ current_stage   │         │
│ status          │         │
│ created_at      │         │
│ updated_at      │         │
│ completed_at    │         │
│ error_message   │         │
└─────────────────┘         │
        │                   │
        │ 1:N               │
        ▼                   │
┌─────────────────┐         │
│ stage_executions│         │
│─────────────────│         │
│ id (PK)         │         │
│ workflow_run_id │         │
│ stage_name      │         │
│ status          │         │
│ retry_count     │         │
│ input_data      │         │
│ output_data     │         │
│ metadata        │         │
│ created_at      │         │
│ completed_at    │         │
│ error_message   │         │
└─────────────────┘         │
                            │
┌─────────────────┐         │
│ information_    │         │
│ sheets          │         │
│─────────────────│         │
│ id (PK)         │         │
│ program_id (UQ) │─────────┤
│ current_stage   │         │
│ status          │         │
│ ingested_data   │         │
│ reconciled_data │         │
│ enriched_data   │         │
│ langage_clair_  │         │
│   data          │         │
│ translated_data │         │
│ validated_data  │         │
│ published_data  │         │
│ created_at      │         │
│ updated_at      │         │
└─────────────────┘         │
        │                   │
        │ 1:N               │
        ▼                   │
┌─────────────────┐         │
│ update_events   │         │
│─────────────────│         │
│ id (PK)         │         │
│ program_id      │─────────┘
│ original_       │
│   checksum      │
│ updated_        │
│   checksum      │
│ original_stage  │
│ update_strategy │
│ processing_     │
│   status        │
│ created_at      │
│ completed_at    │
└─────────────────┘
        │
        │ 1:N
        ▼
┌─────────────────┐
│ update_diffs    │
│─────────────────│
│ id (PK)         │
│ program_id      │
│ update_event_id │
│ stage           │
│ original_data   │
│ updated_data    │
│ changes         │
│ risk_score      │
│ priority        │
│ review_status   │
│ reviewed_by     │
│ reviewed_at     │
│ created_at      │
└─────────────────┘
```

## Entities

### 1. workflow_runs

**Purpose**: Tracks a single execution of the pipeline for a program.

**Fields**:
- `id` (UUID, PRIMARY KEY): Unique identifier for the workflow run
- `program_id` (TEXT, NOT NULL): Data Inclusion unique ID (from spec clarifications)
- `current_stage` (TEXT, NOT NULL): Current pipeline stage
  - Values: `ingestion`, `editorial_policy_validation`, `reconciliation`, `enrichment`, `langage_clair`, `translation`, `validation`, `publication`
- `status` (TEXT, NOT NULL): Workflow execution status
  - Values: `pending`, `running`, `completed`, `failed`
- `created_at` (TIMESTAMPTZ, NOT NULL, DEFAULT NOW()): When workflow started
- `updated_at` (TIMESTAMPTZ, NOT NULL, DEFAULT NOW()): Last state update
- `completed_at` (TIMESTAMPTZ, NULLABLE): When workflow completed (success or failure)
- `error_message` (TEXT, NULLABLE): Error details if status is `failed`

**Indexes**:
- `idx_workflow_runs_program_id` ON `program_id`
- `idx_workflow_runs_status` ON `status`
- `idx_workflow_runs_current_stage` ON `current_stage`

**Constraints**:
- CHECK: `status` IN ('pending', 'running', 'completed', 'failed')
- CHECK: `current_stage` IN ('ingestion', 'reconciliation', 'enrichment', 'langage_clair', 'translation', 'validation', 'publication')

**Relationships**:
- 1:N with `stage_executions` (one workflow has many stage executions)

---

### 2. stage_executions

**Purpose**: Tracks execution of a single pipeline stage within a workflow run.

**Fields**:
- `id` (UUID, PRIMARY KEY): Unique identifier for the stage execution
- `workflow_run_id` (UUID, NOT NULL, FOREIGN KEY → workflow_runs.id): Parent workflow
- `stage_name` (TEXT, NOT NULL): Name of the stage
  - Values: `ingestion`, `editorial_policy_validation`, `reconciliation`, `enrichment`, `langage_clair`, `translation`, `validation`, `publication`
- `status` (TEXT, NOT NULL): Stage execution status
  - Values: `pending`, `running`, `completed`, `failed`
- `retry_count` (INTEGER, NOT NULL, DEFAULT 0): Number of retry attempts
- `input_data` (JSONB, NOT NULL): Input data for the stage
- `output_data` (JSONB, NULLABLE): Output data from the stage (NULL if not completed)
- `execution_metadata` (JSONB, NOT NULL, DEFAULT '{}'): Stage-specific metadata
  - Examples: `{"processing_time_ms": 1234, "ai_model": "gpt-4", "api_calls": 3}`
- `created_at` (TIMESTAMPTZ, NOT NULL, DEFAULT NOW()): When stage started
- `completed_at` (TIMESTAMPTZ, NULLABLE): When stage completed
- `error_message` (TEXT, NULLABLE): Error details if status is `failed`

**Indexes**:
- `idx_stage_executions_workflow_run_id` ON `workflow_run_id`
- `idx_stage_executions_stage_status` ON `stage_name`, `status`

**Constraints**:
- CHECK: `status` IN ('pending', 'running', 'completed', 'failed')
- CHECK: `stage_name` IN ('ingestion', 'editorial_policy_validation', 'reconciliation', 'enrichment', 'langage_clair', 'translation', 'validation', 'publication')
- CHECK: `retry_count` >= 0
- FOREIGN KEY: `workflow_run_id` REFERENCES `workflow_runs(id)` ON DELETE CASCADE

**Relationships**:
- N:1 with `workflow_runs` (many stage executions belong to one workflow)

---

### 3. information_sheets

**Purpose**: Stores program data with progressive enhancement as it moves through pipeline stages.

**Fields**:
- `id` (UUID, PRIMARY KEY): Unique identifier for the information sheet
- `program_id` (TEXT, UNIQUE, NOT NULL): Data Inclusion unique ID
- `refugies_info_id` (TEXT, NULLABLE): MongoDB ObjectId from Réfugiés.info system (populated after publication)
- `current_stage` (TEXT, NOT NULL): Current stage of the program
  - Values: `ingestion`, `editorial_policy_validation`, `reconciliation`, `enrichment`, `langage_clair`, `translation`, `validation`, `publication`
- `status` (TEXT, NOT NULL): Publication status
  - Values: `draft`, `in_review`, `approved`, `published`
- `ingested_data` (JSONB, NOT NULL): Raw data from Data Inclusion API
- `reconciled_data` (JSONB, NULLABLE): Data after reconciliation with Carif-Oref CSV (hourly fetch, deterministic conflict resolution)
- `enriched_data` (JSONB, NULLABLE): Data after enrichment (web scraping, metadata)
- `langage_clair_data` (JSONB, NULLABLE): Data after AI plain language transformation
- `translated_data` (JSONB, NULLABLE): Data after multilingual translation
- `validated_data` (JSONB, NULLABLE): Data after quality validation
- `published_data` (JSONB, NULLABLE): Final data published to Réfugiés.info
- `created_at` (TIMESTAMPTZ, NOT NULL, DEFAULT NOW()): When program first ingested
- `updated_at` (TIMESTAMPTZ, NOT NULL, DEFAULT NOW()): Last data update

**Indexes**:
- `idx_information_sheets_program_id` UNIQUE ON `program_id`
- `idx_information_sheets_refugies_info_id` ON `refugies_info_id` (for lookups from Réfugiés.info system)
- `idx_information_sheets_status` ON `status`
- `idx_information_sheets_current_stage` ON `current_stage`

**Constraints**:
- CHECK: `status` IN ('draft', 'in_review', 'approved', 'published')
- CHECK: `current_stage` IN ('ingestion', 'reconciliation', 'enrichment', 'langage_clair', 'translation', 'validation', 'publication')
- UNIQUE: `program_id`

**Relationships**:
- 1:N with `update_events` (one information sheet can have many updates)

---

### 4. update_events

**Purpose**: Tracks detection of source data updates and routing strategy.

**Fields**:
- `id` (UUID, PRIMARY KEY): Unique identifier for the update event
- `program_id` (TEXT, NOT NULL): Data Inclusion unique ID
- `original_checksum` (TEXT, NOT NULL): SHA-256 hash of original Data Inclusion service JSON (64-character hex string)
- `updated_checksum` (TEXT, NOT NULL): SHA-256 hash of updated Data Inclusion service JSON (64-character hex string)
- `original_stage` (TEXT, NOT NULL): Stage of original program when update detected
  - Values: `ingestion`, `editorial_policy_validation`, `reconciliation`, `enrichment`, `langage_clair`, `translation`, `validation`, `publication`
- `update_strategy` (TEXT, NOT NULL): How update will be processed
  - Values: `full_reprocess` (early stages), `smart_catchup` (late stages)
- `processing_status` (TEXT, NOT NULL): Update processing status
  - Values: `pending`, `processing`, `completed`, `failed`
- `created_at` (TIMESTAMPTZ, NOT NULL, DEFAULT NOW()): When update detected
- `completed_at` (TIMESTAMPTZ, NULLABLE): When update processing completed

**Checksum Calculation**:
Checksums are SHA-256 hashes of the complete Data Inclusion service JSON (excluding metadata fields: `source`, `structure_id`, `lien_mobilisation`). The JSON is normalized (keys sorted) before hashing to ensure consistency. This captures all content changes including name, description, location, contact information, schedule, eligibility criteria, etc.

**`original_stage` Field Lifecycle**:
- **Population**: When an update is detected, this field is populated by copying the current value of `information_sheets.current_stage` for the program
- **Purpose**: Snapshot the pipeline stage at the moment the update was detected
- **Immutability**: Once set, this field NEVER changes - it's a historical record
- **Usage**: Determines update routing strategy:
  - If `original_stage` IN ('ingestion', 'reconciliation') → `update_strategy` = 'full_reprocess'
  - If `original_stage` IN ('enrichment', 'langage_clair', 'translation', 'validation', 'publication') → `update_strategy` = 'smart_catchup'
- **Contrast with `information_sheets.current_stage`**: The information sheet's `current_stage` continues to advance as the program progresses, while `update_events.original_stage` remains frozen as a historical marker

**Indexes**:
- `idx_update_events_program_id` ON `program_id`
- `idx_update_events_processing_status` ON `processing_status`
- `idx_update_events_created_at` ON `created_at` DESC

**Constraints**:
- CHECK: `original_stage` IN ('ingestion', 'editorial_policy_validation', 'reconciliation', 'enrichment', 'langage_clair', 'translation', 'validation', 'publication')
- CHECK: `update_strategy` IN ('full_reprocess', 'smart_catchup')
- CHECK: `processing_status` IN ('pending', 'processing', 'completed', 'failed')

**Relationships**:
- N:1 with `information_sheets` (many updates for one program)
- 1:N with `update_diffs` (one update event can generate multiple diffs)

---

### 5. update_diffs

**Purpose**: Stores diffs awaiting editorial review with risk scoring and approval workflow.

**Fields**:
- `id` (UUID, PRIMARY KEY): Unique identifier for the diff
- `program_id` (TEXT, NOT NULL): Data Inclusion unique ID
- `update_event_id` (UUID, NOT NULL, FOREIGN KEY → update_events.id): Parent update event
- `stage` (TEXT, NOT NULL): Stage where diff was generated
  - Values: `enrichment`, `langage_clair`, `translation`, `validation`
- `original_data` (JSONB, NOT NULL): Original program data (with human work)
- `updated_data` (JSONB, NOT NULL): Updated program data (AI catch-up)
- `changes` (JSONB, NOT NULL): Structured diff with change classification
  - Format: `{"additions": [...], "deletions": [...], "minor_edits": [...], "major_edits": [...]}`
- `risk_score` (FLOAT, NOT NULL): Calculated risk score (0.0-1.0)
- `priority` (TEXT, NOT NULL): Review priority based on risk score
  - Values: `low` (<0.5), `medium` (0.5-0.8), `high` (>0.8)
- `review_status` (TEXT, NOT NULL): Editorial review status
  - Values: `pending`, `approved`, `rejected`, `edited`
- `reviewed_by` (UUID, NULLABLE): Supabase Auth user ID of reviewer
- `reviewed_at` (TIMESTAMPTZ, NULLABLE): When diff was reviewed
- `created_at` (TIMESTAMPTZ, NOT NULL, DEFAULT NOW()): When diff was generated

**Indexes**:
- `idx_update_diffs_program_id` ON `program_id`
- `idx_update_diffs_review_status` ON `review_status`
- `idx_update_diffs_priority` ON `priority`
- `idx_update_diffs_created_at` ON `created_at` DESC

**Constraints**:
- CHECK: `stage` IN ('enrichment', 'langage_clair', 'translation', 'validation')
- CHECK: `risk_score` >= 0.0 AND `risk_score` <= 1.0
- CHECK: `priority` IN ('low', 'medium', 'high')
- CHECK: `review_status` IN ('pending', 'approved', 'rejected', 'edited')
- FOREIGN KEY: `update_event_id` REFERENCES `update_events(id)` ON DELETE CASCADE

**Relationships**:
- N:1 with `update_events` (many diffs for one update event)

---

## Data Flow

### New Program Processing

1. **Ingestion**: Create `workflow_run` (status=`pending`) and `information_sheet` (status=`draft`)
2. **Stage Execution**: For each stage, create `stage_execution` (status=`running`)
3. **Stage Completion**: Update `stage_execution` (status=`completed`, output_data), update `information_sheet` with stage-specific data
4. **Workflow Completion**: Update `workflow_run` (status=`completed`), update `information_sheet` (status=`published`)

### Update Detection & Smart Catch-Up

1. **Update Detection**: Create `update_event` (update_strategy=`smart_catchup` if original_stage is late stage)
2. **Smart Catch-Up**: Process update through stages until reaching original_stage
3. **Diff Generation**: Create `update_diff` with structured changes and risk_score
4. **Editorial Review**: Editor approves/rejects/edits diff, update `update_diff` (review_status, reviewed_by, reviewed_at)
5. **Merge**: If approved, update `information_sheet` with merged data, continue pipeline

---

## Validation Rules

### workflow_runs
- `program_id` must match Data Inclusion schema format
- `completed_at` must be >= `created_at`
- `error_message` must be NULL if status is not `failed`

### stage_executions
- `completed_at` must be >= `created_at`
- `output_data` must be NULL if status is not `completed`
- `retry_count` must be <= 10 (max retries from spec)

### information_sheets
- `program_id` must be unique across all sheets
- `refugies_info_id` must be NULL until status is `published`
- `refugies_info_id` must be a valid MongoDB ObjectId format (24-character hex string)
- Stage-specific data (e.g., `reconciled_data`) must be NULL if `current_stage` hasn't reached that stage yet
- `updated_at` must be >= `created_at`

### update_events
- `updated_checksum` must be different from `original_checksum`
- `completed_at` must be >= `created_at`
- `update_strategy` must be `full_reprocess` if `original_stage` is `ingestion`, `editorial_policy_validation`, or `reconciliation`
- `update_strategy` must be `smart_catchup` if `original_stage` is `enrichment`, `langage_clair`, `translation`, `validation`, or `publication`

### update_diffs
- `risk_score` must match `priority`: low (<0.5), medium (0.5-0.8), high (>0.8)
- `reviewed_by` and `reviewed_at` must be NULL if `review_status` is `pending`
- `reviewed_by` and `reviewed_at` must be NOT NULL if `review_status` is `approved`, `rejected`, or `edited`

---

## Migration Strategy

### **Phase 1: Core Tables**
- Create `workflow_runs`, `stage_executions`, `information_sheets`
- Add indexes and constraints
- Seed with test data
- Add `editorial_policy_validation` stage to stage enums
- Add `policy_validation_decisions` table (program_id, rule_applied, decision, reason, audit_trail)

### **Phase 2: Update Handling**
- Create `update_events`, `update_diffs`
- Add foreign key relationships
- Add indexes and constraints
- Add `carif_oref_reconciliation_status` table (program_id, reconciliation_status, carif_oref_data, conflicts_detected, last_fetch_at)

### Phase 3: Optimization
- Add materialized views for dashboards (if needed)
- Add database functions for common queries
- Tune indexes based on query patterns

---

## Security & Access Control

### Row-Level Security (RLS)

**workflow_runs, stage_executions, information_sheets**:
- Read: All authenticated users
- Write: Service role only (Python services)

**update_events**:
- Read: All authenticated users
- Write: Service role only (Python services)

**update_diffs**:
- Read: All authenticated users (editorial team)
- Write: Service role only (Python services)
- Update `review_status`, `reviewed_by`, `reviewed_at`: Authenticated users (editorial team)

### Supabase Auth Integration

- Editorial team users managed via Supabase Auth
- RBAC enforced at API level (FastAPI checks JWT)
- Audit trail: `reviewed_by` tracks which editor reviewed each diff

---

## Summary

Data model supports:
- ✅ Complete workflow state tracking (workflow_runs, stage_executions)
- ✅ Editorial policy validation (policy_validation_decisions with audit trail)
- ✅ Carif-Oref reconciliation (hourly CSV fetch, deterministic conflict resolution)
- ✅ Progressive data enhancement (information_sheets with stage-specific JSONB columns)
- ✅ Update detection and routing (update_events with strategy)
- ✅ Diff review workflow (update_diffs with risk scoring and approval)
- ✅ Observability (timestamps, metadata, error messages)
- ✅ GDPR compliance (no PII in orchestration layer, audit trail)

Ready to proceed to contract generation.
