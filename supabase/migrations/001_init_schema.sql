-- Nexus Pipeline Orchestration Schema
-- Created: 2025-10-21
-- Purpose: Initialize database schema for workflow orchestration, state management, and update handling

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================================================
-- Core Tables
-- ============================================================================

-- workflow_runs: Tracks a single execution of the pipeline for a program
CREATE TABLE workflow_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    program_id TEXT NOT NULL,
    current_stage TEXT NOT NULL CHECK (current_stage IN (
        'ingestion', 'editorial_policy_validation', 'reconciliation', 'enrichment',
        'langage_clair', 'translation', 'validation', 'publication'
    )),
    status TEXT NOT NULL CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    UNIQUE(program_id)
);

CREATE INDEX idx_workflow_runs_program_id ON workflow_runs(program_id);
CREATE INDEX idx_workflow_runs_status ON workflow_runs(status);
CREATE INDEX idx_workflow_runs_created_at ON workflow_runs(created_at DESC);

-- stage_executions: Tracks execution of a single pipeline stage within a workflow run
CREATE TABLE stage_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_run_id UUID NOT NULL REFERENCES workflow_runs(id) ON DELETE CASCADE,
    stage_name TEXT NOT NULL CHECK (stage_name IN (
        'ingestion', 'editorial_policy_validation', 'reconciliation', 'enrichment',
        'langage_clair', 'translation', 'validation', 'publication'
    )),
    status TEXT NOT NULL CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    retry_count INTEGER NOT NULL DEFAULT 0 CHECK (retry_count >= 0),
    input_data JSONB NOT NULL,
    output_data JSONB,
    execution_metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    error_message TEXT
);

CREATE INDEX idx_stage_executions_workflow_run_id ON stage_executions(workflow_run_id);
CREATE INDEX idx_stage_executions_stage_status ON stage_executions(stage_name, status);

-- information_sheets: Progressive data enhancement through pipeline stages
CREATE TABLE information_sheets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    program_id TEXT NOT NULL UNIQUE,
    refugies_info_id TEXT,
    current_stage TEXT NOT NULL CHECK (current_stage IN (
        'ingestion', 'editorial_policy_validation', 'reconciliation', 'enrichment',
        'langage_clair', 'translation', 'validation', 'publication'
    )),
    status TEXT NOT NULL CHECK (status IN ('draft', 'in_review', 'approved', 'published')),
    ingested_data JSONB NOT NULL,
    reconciled_data JSONB,
    enriched_data JSONB,
    langage_clair_data JSONB,
    translated_data JSONB,
    validated_data JSONB,
    published_data JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_information_sheets_program_id ON information_sheets(program_id);
CREATE INDEX idx_information_sheets_current_stage ON information_sheets(current_stage);
CREATE INDEX idx_information_sheets_status ON information_sheets(status);

-- ============================================================================
-- Editorial Policy Validation Tables
-- ============================================================================

-- policy_validation_decisions: Tracks policy validation results with audit trail
CREATE TABLE policy_validation_decisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    program_id TEXT NOT NULL,
    policy_rule_id TEXT NOT NULL,
    decision TEXT NOT NULL CHECK (decision IN ('pass', 'reject', 'review')),
    reason TEXT,
    audit_trail JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT,
    FOREIGN KEY (program_id) REFERENCES information_sheets(program_id) ON DELETE CASCADE
);

CREATE INDEX idx_policy_validation_decisions_program_id ON policy_validation_decisions(program_id);
CREATE INDEX idx_policy_validation_decisions_decision ON policy_validation_decisions(decision);

-- ============================================================================
-- Carif-Oref Reconciliation Tables
-- ============================================================================

-- carif_oref_reconciliation_status: Tracks reconciliation status and conflicts
CREATE TABLE carif_oref_reconciliation_status (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    program_id TEXT NOT NULL UNIQUE,
    reconciliation_status TEXT NOT NULL CHECK (reconciliation_status IN (
        'fully_reconciled', 'partially_reconciled', 'data_conflict', 'reconciliation_failed'
    )),
    carif_oref_data JSONB,
    conflicts_detected JSONB DEFAULT '[]',
    last_fetch_at TIMESTAMPTZ,
    last_successful_fetch_at TIMESTAMPTZ,
    fetch_error_message TEXT,
    FOREIGN KEY (program_id) REFERENCES information_sheets(program_id) ON DELETE CASCADE
);

CREATE INDEX idx_carif_oref_reconciliation_status_program_id ON carif_oref_reconciliation_status(program_id);
CREATE INDEX idx_carif_oref_reconciliation_status_status ON carif_oref_reconciliation_status(reconciliation_status);

-- ============================================================================
-- Update Handling Tables
-- ============================================================================

-- update_events: Tracks detection of source data updates and routing strategy
CREATE TABLE update_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    program_id TEXT NOT NULL,
    original_checksum TEXT NOT NULL,
    updated_checksum TEXT NOT NULL,
    original_stage TEXT NOT NULL CHECK (original_stage IN (
        'ingestion', 'editorial_policy_validation', 'reconciliation', 'enrichment',
        'langage_clair', 'translation', 'validation', 'publication'
    )),
    update_strategy TEXT NOT NULL CHECK (update_strategy IN ('full_reprocess', 'smart_catchup')),
    processing_status TEXT NOT NULL CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    CHECK (updated_checksum != original_checksum)
);

CREATE INDEX idx_update_events_program_id ON update_events(program_id);
CREATE INDEX idx_update_events_processing_status ON update_events(processing_status);
CREATE INDEX idx_update_events_created_at ON update_events(created_at DESC);

-- update_diffs: Stores diffs awaiting editorial review with risk scoring
CREATE TABLE update_diffs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    program_id TEXT NOT NULL,
    update_event_id UUID NOT NULL REFERENCES update_events(id) ON DELETE CASCADE,
    original_data JSONB NOT NULL,
    updated_data JSONB NOT NULL,
    diff_content JSONB NOT NULL,
    risk_score NUMERIC(3,2) NOT NULL CHECK (risk_score >= 0.0 AND risk_score <= 1.0),
    priority TEXT NOT NULL CHECK (priority IN ('low', 'medium', 'high')),
    review_status TEXT NOT NULL CHECK (review_status IN ('pending', 'approved', 'rejected', 'edited')),
    reviewed_by TEXT,
    reviewed_at TIMESTAMPTZ,
    approval_type TEXT CHECK (approval_type IN ('human', 'system')),
    approval_reason TEXT,
    approved_at TIMESTAMPTZ,
    approved_by TEXT,
    approval_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (
        (review_status = 'pending' AND reviewed_by IS NULL AND reviewed_at IS NULL) OR
        (review_status IN ('approved', 'rejected', 'edited') AND reviewed_by IS NOT NULL AND reviewed_at IS NOT NULL)
    ),
    CHECK (
        (priority = 'low' AND risk_score < 0.5) OR
        (priority = 'medium' AND risk_score >= 0.5 AND risk_score <= 0.8) OR
        (priority = 'high' AND risk_score > 0.8)
    )
);

CREATE INDEX idx_update_diffs_program_id ON update_diffs(program_id);
CREATE INDEX idx_update_diffs_update_event_id ON update_diffs(update_event_id);
CREATE INDEX idx_update_diffs_review_status ON update_diffs(review_status);
CREATE INDEX idx_update_diffs_priority ON update_diffs(priority);
CREATE INDEX idx_update_diffs_created_at ON update_diffs(created_at DESC);

-- ============================================================================
-- Triggers for Automatic Timestamp Updates
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_workflow_runs_updated_at
BEFORE UPDATE ON workflow_runs
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_information_sheets_updated_at
BEFORE UPDATE ON information_sheets
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_update_diffs_updated_at
BEFORE UPDATE ON update_diffs
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Views for Common Queries
-- ============================================================================

-- View: Current pipeline status for all programs
CREATE VIEW v_pipeline_status AS
SELECT
    ws.program_id,
    ws.current_stage,
    ws.status,
    COUNT(se.id) as stage_count,
    MAX(se.completed_at) as last_stage_completed_at,
    ws.created_at,
    ws.updated_at
FROM workflow_runs ws
LEFT JOIN stage_executions se ON ws.id = se.workflow_run_id
GROUP BY ws.id, ws.program_id, ws.current_stage, ws.status, ws.created_at, ws.updated_at;

-- View: Pending diffs requiring review
CREATE VIEW v_pending_diffs AS
SELECT
    ud.id,
    ud.program_id,
    ud.risk_score,
    ud.priority,
    ud.review_status,
    ue.update_strategy,
    ud.created_at,
    ROW_NUMBER() OVER (ORDER BY ud.priority DESC, ud.risk_score DESC, ud.created_at ASC) as review_order
FROM update_diffs ud
JOIN update_events ue ON ud.update_event_id = ue.id
WHERE ud.review_status = 'pending'
ORDER BY ud.priority DESC, ud.risk_score DESC, ud.created_at ASC;

-- ============================================================================
-- Row-Level Security (Optional - Enable if needed)
-- ============================================================================

-- ALTER TABLE workflow_runs ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE stage_executions ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE information_sheets ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE update_events ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE update_diffs ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE policy_validation_decisions ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE carif_oref_reconciliation_status ENABLE ROW LEVEL SECURITY;
