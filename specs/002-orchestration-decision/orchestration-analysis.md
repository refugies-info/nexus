# Orchestration Decision Analysis: Nexus AI Pipeline

**Date**: 2025-10-20
**Purpose**: Evaluate orchestration approaches for the Nexus data pipeline and establish Supabase as state management database
**Context**: Monorepo setup complete (spec 001), ready to design pipeline orchestration architecture

---

## Executive Summary

**Recommendation**: **Lightweight Pythonic Approach** with **Supabase for state management**

**Key Decision Factors**:
- **Scale**: Processing ~hundreds of French learning programs, not millions of records
- **Complexity**: 7-stage linear pipeline with well-defined dependencies
- **Team**: Small team prioritizing velocity and simplicity over enterprise features
- **Infrastructure**: Supabase provides managed PostgreSQL + real-time + auth out of the box
- **Constitutional Alignment**: Principle VII (Incremental Delivery) favors starting simple

**Trade-off**: Sacrifice enterprise orchestration features (complex DAGs, distributed execution, extensive UI) for development velocity, operational simplicity, and lower infrastructure overhead.

---

## Pipeline Architecture Context

### Nexus Pipeline Stages (Constitutional Principle II: Pipeline Modularity)

```
Data Inclusion / Carif Oref API
    ↓
[1. Ingestion] → Raw data validation & storage
    ↓
[2. Reconciliation] → Cross-reference with Carif Oref, resolve conflicts
    ↓
[3. Enrichment] → Web scraping for missing data, add metadata
    ↓
[4. Langage Clair] → AI transformation to plain French (Principle XI)
    ↓
[5. Translation] → Multilingual translation with cultural mediation (Principles III, XII)
    ↓
[6. Validation] → Quality checks, editorial compliance (Principle IV)
    ↓
[7. Publication] → Push to Réfugiés.info API (Principle V)
```

### Orchestration Requirements

#### Functional Requirements
- **Sequential Execution**: Stages must execute in order (langage_clair before translation, etc.)
- **State Persistence**: Track which programs are at which stage, handle partial failures
- **Retry Logic**: Retry failed stages (API timeouts, rate limits, transient errors)
- **Observability**: Log every transformation, track data lineage (Principle VI)
- **Partial Replay**: Re-run specific stages without full pipeline restart
- **Incremental Processing**: Process new/updated programs without reprocessing all data
- **Manual Intervention**: Support human review queues (editorial validation, quality issues)
- **Update Handling**: Efficiently process updates to raw data (~100/week) without discarding human work

#### Non-Functional Requirements
- **Simplicity**: Small team needs maintainable, debuggable code
- **Development Velocity**: Fast iteration on pipeline logic, not orchestration infrastructure
- **Cost**: Minimize infrastructure and operational overhead
- **Testability**: Each stage independently testable (Principle II, TDD)
- **Scalability**: Handle hundreds of programs, not millions (Carif Oref French learning scope)

#### Out of Scope (for MVP)
- Complex DAG dependencies (pipeline is linear)
- Distributed execution across multiple workers
- Real-time streaming (batch processing is sufficient)
- Multi-tenant orchestration
- Advanced scheduling (cron-like triggers sufficient)

---

## Option 1: Industry-Standard Orchestrators

### 1A. Apache Airflow

**Overview**: Battle-tested workflow orchestration platform, industry standard for data pipelines.

**Pros**:
- ✅ Mature ecosystem, extensive documentation
- ✅ Rich UI for monitoring, debugging, and manual interventions
- ✅ Built-in retry logic, error handling, alerting
- ✅ Large community, many integrations
- ✅ Supports complex DAGs (future-proofing)

**Cons**:
- ❌ **Heavy infrastructure**: Requires PostgreSQL/MySQL, Redis, web server, scheduler, workers
- ❌ **Operational complexity**: Managing Airflow itself becomes a project
- ❌ **Steep learning curve**: DAG syntax, operators, hooks, sensors
- ❌ **Overkill for linear pipeline**: Most features unused (complex DAGs, distributed execution)
- ❌ **Slow iteration**: Changes require DAG redeployment, scheduler restart
- ❌ **Testing friction**: Airflow DAGs harder to unit test than plain Python

**Verdict**: **Not Recommended** - Too heavy for a small team and linear pipeline. Infrastructure overhead outweighs benefits.

---

### 1B. Prefect

**Overview**: Modern workflow orchestration, "Airflow done right" with Python-first API.

**Pros**:
- ✅ Python-native API (decorators, type hints)
- ✅ Easier to test than Airflow (flows are just Python functions)
- ✅ Cloud-hosted option (Prefect Cloud) reduces infrastructure burden
- ✅ Good observability and UI
- ✅ Hybrid execution model (local dev, cloud prod)

**Cons**:
- ❌ **Still requires infrastructure**: Self-hosted needs PostgreSQL, API server, agents
- ❌ **Vendor lock-in risk**: Cloud option ties to Prefect's pricing and availability
- ❌ **Learning curve**: Prefect-specific concepts (flows, tasks, deployments)
- ❌ **Overkill for linear pipeline**: Most features unused
- ❌ **Cost**: Prefect Cloud pricing for production workloads

**Verdict**: **Not Recommended** - Better than Airflow but still too complex for our needs. Cloud option introduces vendor dependency.

---

### 1C. Dagster

**Overview**: Data orchestration platform focused on data assets and observability.

**Pros**:
- ✅ Asset-centric model aligns with data pipeline thinking
- ✅ Strong type system and data validation
- ✅ Excellent observability and lineage tracking
- ✅ Good testing story (assets are testable functions)
- ✅ Modern UI and developer experience

**Cons**:
- ❌ **Infrastructure overhead**: Requires PostgreSQL, web server, daemon
- ❌ **Conceptual complexity**: Assets, ops, graphs, resources
- ❌ **Overkill for linear pipeline**: Asset-centric model better for complex data platforms
- ❌ **Smaller community**: Less mature than Airflow, fewer integrations

**Verdict**: **Not Recommended** - Best-in-class for complex data platforms, but too heavy for a 7-stage linear pipeline.

---

### 1D. Temporal

**Overview**: Durable execution platform for long-running workflows and microservices orchestration.

**Pros**:
- ✅ Excellent for long-running, stateful workflows
- ✅ Built-in retry, timeout, and failure handling
- ✅ Strong consistency guarantees
- ✅ Good for microservices orchestration

**Cons**:
- ❌ **Infrastructure overhead**: Requires Temporal server, PostgreSQL, Elasticsearch (optional)
- ❌ **Conceptual complexity**: Workflows, activities, signals, queries
- ❌ **Overkill for batch pipeline**: Designed for long-running, event-driven workflows
- ❌ **Learning curve**: Temporal-specific patterns and best practices
- ❌ **Not data-pipeline-focused**: Better for microservices than ETL

**Verdict**: **Not Recommended** - Excellent for microservices orchestration, but not optimized for data pipelines.

---

## Option 2: Lightweight Pythonic Approach

### 2A. Custom Orchestration + Lightweight Libraries

**Overview**: Build minimal orchestration layer using plain Python + lightweight libraries for specific needs.

**Architecture**:
```python
# Orchestration Core (custom)
class PipelineOrchestrator:
    """Manages pipeline execution, state, and error handling."""

    def __init__(self, supabase_client, logger):
        self.db = supabase_client
        self.logger = logger

    async def run_pipeline(self, program_id: str):
        """Execute full pipeline for a program."""
        stages = [
            IngestionStage(),
            ReconciliationStage(),
            EnrichmentStage(),
            LangageClairStage(),
            TranslationStage(),
            ValidationStage(),
            PublicationStage(),
        ]

        for stage in stages:
            await self._run_stage(program_id, stage)

    async def _run_stage(self, program_id: str, stage: PipelineStage):
        """Execute single stage with retry and state tracking."""
        state = await self.db.get_program_state(program_id)

        if state.is_stage_complete(stage.name):
            self.logger.info(f"Stage {stage.name} already complete, skipping")
            return

        try:
            result = await self._retry_with_backoff(
                stage.execute, program_id, max_retries=3
            )
            await self.db.update_program_state(
                program_id, stage.name, "completed", result
            )
        except Exception as e:
            await self.db.update_program_state(
                program_id, stage.name, "failed", error=str(e)
            )
            raise

# Pipeline Stage Interface
class PipelineStage(ABC):
    """Base class for all pipeline stages."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def execute(self, program_id: str) -> dict:
        """Execute stage logic, return result metadata."""
        pass
```

**Supporting Libraries**:
- **State Management**: Supabase Python client (managed PostgreSQL + real-time)
- **Retry Logic**: `tenacity` (declarative retry with exponential backoff)
- **Async Execution**: `asyncio` (built-in, no dependencies)
- **Observability**: `structlog` (structured logging) + Supabase logs
- **Scheduling**: `APScheduler` (lightweight cron-like scheduling) or simple cron

**Pros**:
- ✅ **Minimal infrastructure**: Just Python app + Supabase (managed PostgreSQL)
- ✅ **Fast development**: No framework learning curve, plain Python
- ✅ **Easy testing**: Stages are just async functions, mock Supabase client
- ✅ **Full control**: Customize orchestration logic without framework constraints
- ✅ **Low operational overhead**: No separate orchestrator to manage
- ✅ **Constitutional alignment**: Principle VII (Incremental Delivery) - start simple
- ✅ **Debuggable**: Standard Python debugging tools, no black box

**Cons**:
- ❌ **No built-in UI**: Need to build custom monitoring (Supabase dashboard + logs)
- ❌ **Manual retry logic**: Implement retry/backoff (mitigated by `tenacity` library)
- ❌ **Manual state management**: Design state schema (mitigated by Supabase)
- ❌ **Limited observability**: No out-of-box lineage tracking (build custom)
- ❌ **Scaling limitations**: Single-process execution (sufficient for MVP scope)

**Verdict**: **RECOMMENDED** - Aligns with project constraints (small team, linear pipeline, incremental delivery). Trade enterprise features for velocity and simplicity.

---

## Supabase as State Management Database

### Why Supabase?

**Supabase = Managed PostgreSQL + Real-time + Auth + Storage + Edge Functions**

**Pros**:
- ✅ **Managed PostgreSQL**: No database operations overhead
- ✅ **Real-time subscriptions**: Monitor pipeline state changes in real-time
- ✅ **Built-in auth**: Secure API access for future admin UI
- ✅ **Row-level security**: Fine-grained access control
- ✅ **Storage**: Store enriched data, AI model outputs, logs
- ✅ **Edge functions**: Serverless compute for lightweight tasks
- ✅ **Generous free tier**: Sufficient for MVP
- ✅ **Open source**: Can self-host if needed (no vendor lock-in)
- ✅ **Python SDK**: Official `supabase-py` client

**Cons**:
- ❌ **Vendor dependency**: Hosted service (mitigated by open-source self-hosting option)
- ❌ **PostgreSQL limitations**: Not optimized for time-series or analytics (sufficient for our use case)

**Alternatives Considered**:
- **SQLite**: Too limited for production (no concurrent writes, no remote access)
- **Managed PostgreSQL (AWS RDS, GCP Cloud SQL)**: More operational overhead than Supabase
- **MongoDB**: Document model not ideal for relational workflow state
- **Redis**: In-memory, not durable enough for state persistence

**Verdict**: **RECOMMENDED** - Best balance of features, ease of use, and cost for MVP.

---

## Supabase Schema Design

### Database Schema

```sql
-- Workflow State Table
CREATE TABLE workflow_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    program_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'running', 'completed', 'failed', 'paused')),
    current_stage TEXT,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Stage Execution Table
CREATE TABLE stage_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_run_id UUID REFERENCES workflow_runs(id) ON DELETE CASCADE,
    stage_name TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'running', 'completed', 'failed', 'skipped')),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    retry_count INT DEFAULT 0,
    error_message TEXT,
    input_data JSONB,
    output_data JSONB,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Data Source State Table (Carif Oref, Data Inclusion)
CREATE TABLE data_source_state (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_name TEXT NOT NULL,
    source_id TEXT NOT NULL, -- External ID from data source
    last_fetched_at TIMESTAMPTZ,
    last_modified_at TIMESTAMPTZ,
    checksum TEXT, -- Detect changes
    status TEXT NOT NULL CHECK (status IN ('new', 'updated', 'unchanged', 'deleted')),
    raw_data JSONB,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(source_name, source_id)
);

-- Information Sheet State Table (Progressive Enhancement)
CREATE TABLE information_sheets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    program_id TEXT NOT NULL UNIQUE,
    source_data_id UUID REFERENCES data_source_state(id),
    current_stage TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('draft', 'in_review', 'approved', 'published', 'archived')),

    -- Stage outputs (progressive enhancement)
    ingested_data JSONB,
    reconciled_data JSONB,
    enriched_data JSONB,
    langage_clair_data JSONB, -- Plain French transformation
    translated_data JSONB, -- Multilingual translations
    validation_results JSONB,
    publication_metadata JSONB,

    -- Quality metrics
    quality_score NUMERIC,
    editorial_notes TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    published_at TIMESTAMPTZ
);

-- Indexes for performance
CREATE INDEX idx_workflow_runs_program_id ON workflow_runs(program_id);
CREATE INDEX idx_workflow_runs_status ON workflow_runs(status);
CREATE INDEX idx_stage_executions_workflow_run_id ON stage_executions(workflow_run_id);
CREATE INDEX idx_stage_executions_stage_name ON stage_executions(stage_name);
CREATE INDEX idx_data_source_state_source ON data_source_state(source_name, source_id);
CREATE INDEX idx_information_sheets_program_id ON information_sheets(program_id);
CREATE INDEX idx_information_sheets_status ON information_sheets(status);

-- Triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_workflow_runs_updated_at BEFORE UPDATE ON workflow_runs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_stage_executions_updated_at BEFORE UPDATE ON stage_executions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_data_source_state_updated_at BEFORE UPDATE ON data_source_state
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_information_sheets_updated_at BEFORE UPDATE ON information_sheets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### Schema Design Rationale

**`workflow_runs`**: Tracks overall pipeline execution per program
- Enables monitoring, debugging, and replay
- Links to stage executions for detailed lineage

**`stage_executions`**: Granular tracking of each stage's execution
- Supports retry logic (retry_count)
- Stores input/output for debugging and lineage
- Enables partial replay (re-run specific stages)

**`data_source_state`**: Tracks external data sources (Carif Oref, Data Inclusion)
- Detects changes via checksum (incremental processing)
- Stores raw data for reconciliation and audit
- Supports multiple data sources

**`information_sheets`**: Progressive enhancement of information sheets
- Each stage adds data to corresponding JSONB column
- Enables partial completion and human review
- Tracks quality metrics and editorial workflow

**JSONB Columns**: Flexible schema for evolving data structures
- Avoids rigid schemas during MVP iteration
- Supports complex nested data (translations, metadata)
- PostgreSQL JSONB is indexed and queryable

---

## Recommended Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Nexus Pipeline                          │
│                                                             │
│  ┌─────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Scheduler  │───▶│ Orchestrator │───▶│   Supabase   │  │
│  │ (APScheduler│    │   (Python)   │    │  (State DB)  │  │
│  │  or cron)   │    │              │    │              │  │
│  └─────────────┘    └──────┬───────┘    └──────────────┘  │
│                             │                               │
│                             ▼                               │
│         ┌───────────────────────────────────┐              │
│         │      Pipeline Stages (libs/)      │              │
│         ├───────────────────────────────────┤              │
│         │ 1. Ingestion                      │              │
│         │ 2. Reconciliation                 │              │
│         │ 3. Enrichment                     │              │
│         │ 4. Langage Clair (AI)             │              │
│         │ 5. Translation (AI)               │              │
│         │ 6. Validation                     │              │
│         │ 7. Publication                    │              │
│         └───────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  External Services   │
                  ├──────────────────────┤
                  │ • Data Inclusion API │
                  │ • Carif Oref API     │
                  │ • Web Scraping       │
                  │ • AI APIs (OpenAI)   │
                  │ • Réfugiés.info API  │
                  └──────────────────────┘
```

### Implementation Plan

**Phase 1: Core Orchestration (Week 1-2)**
1. Set up Supabase project and schema
2. Implement `PipelineOrchestrator` class
3. Implement `PipelineStage` base class
4. Add retry logic with `tenacity`
5. Add structured logging with `structlog`
6. Write unit tests for orchestration logic

**Phase 2: Stage Implementations (Week 3-8)**
1. Implement each stage (ingestion → publication)
2. Each stage follows TDD (tests first)
3. Each stage independently testable with mocks
4. Integration tests per stage
5. Add update detection to ingestion stage (checksum-based)

**Phase 3: Update Handling (Week 9-11)**
1. Implement update router (full reprocess vs smart catch-up)
2. Build smart catch-up orchestrator with AI acceleration
3. Implement diff generator
4. Build Streamlit diff review UI
5. Add risk-based sampling logic
6. Integration tests for update workflows

**Phase 4: Monitoring & Observability (Week 12-13)**
1. Build monitoring dashboard (Supabase + Streamlit/Gradio)
2. Set up alerting (email/Slack on failures)
3. Add data lineage tracking
4. Performance metrics collection
5. Update handling metrics (diff queue, approval rates)

**Phase 5: Production Hardening (Week 14-15)**
1. Add comprehensive error handling
2. Implement graceful shutdown
3. Add health checks and readiness probes
4. Load testing and performance optimization
5. Documentation and runbooks

---

## Decision Matrix

| Criterion | Airflow | Prefect | Dagster | Temporal | Lightweight + Supabase |
|-----------|---------|---------|---------|----------|------------------------|
| **Infrastructure Overhead** | ❌ High | ⚠️ Medium | ❌ High | ❌ High | ✅ Low |
| **Learning Curve** | ❌ Steep | ⚠️ Medium | ❌ Steep | ❌ Steep | ✅ Minimal |
| **Development Velocity** | ❌ Slow | ⚠️ Medium | ⚠️ Medium | ❌ Slow | ✅ Fast |
| **Operational Complexity** | ❌ High | ⚠️ Medium | ❌ High | ❌ High | ✅ Low |
| **Testing Ease** | ❌ Hard | ⚠️ Medium | ✅ Good | ⚠️ Medium | ✅ Easy |
| **Observability** | ✅ Excellent | ✅ Excellent | ✅ Excellent | ✅ Good | ⚠️ Custom |
| **UI/Monitoring** | ✅ Rich | ✅ Rich | ✅ Rich | ✅ Good | ❌ Custom |
| **Cost** | ⚠️ Medium | ⚠️ Medium-High | ⚠️ Medium | ⚠️ Medium | ✅ Low |
| **Scalability** | ✅ Excellent | ✅ Excellent | ✅ Excellent | ✅ Excellent | ⚠️ Limited |
| **Fit for Linear Pipeline** | ❌ Overkill | ❌ Overkill | ❌ Overkill | ❌ Overkill | ✅ Perfect |
| **Constitutional Alignment** | ❌ Poor | ⚠️ Medium | ⚠️ Medium | ❌ Poor | ✅ Excellent |

**Legend**: ✅ Excellent | ⚠️ Acceptable | ❌ Poor

---

## Recommendation: Lightweight Pythonic Approach

### Why This Is The Right Choice

**1. Aligns with Constitutional Principles**
- **Principle VII (Incremental Delivery)**: Start simple, add complexity only when needed
- **Principle II (Pipeline Modularity)**: Stages are independently testable Python modules
- **Principle VI (Observability)**: Custom logging and state tracking via Supabase
- **TDD Compliance**: Plain Python functions are easier to test than framework-specific code

**2. Matches Project Constraints**
- **Small team**: No dedicated DevOps, minimize operational burden
- **Linear pipeline**: No complex DAG dependencies, sequential execution sufficient
- **MVP scope**: ~Hundreds of programs, not millions of records
- **Fast iteration**: Plain Python enables rapid prototyping and debugging

**3. Technical Advantages**
- **Minimal infrastructure**: Just Python app + Supabase (managed PostgreSQL)
- **No vendor lock-in**: Supabase is open source, can self-host if needed
- **Easy testing**: Mock Supabase client, test stages in isolation
- **Full control**: Customize orchestration logic without framework constraints
- **Debuggable**: Standard Python debugging tools, no black box

**4. Future-Proofing**
- **Gradual migration path**: If scale demands it, migrate to Prefect/Dagster later
- **Supabase scales**: PostgreSQL handles millions of rows, sufficient for foreseeable future
- **Modular design**: Stages are independent, can parallelize or distribute later
- **Custom UI**: Build monitoring dashboard when needed (Streamlit/Gradio + Supabase)

### When to Reconsider

**Migrate to enterprise orchestrator if:**
- Processing >10,000 programs daily (scale threshold)
- Need complex DAG dependencies (non-linear pipeline)
- Require distributed execution across multiple workers
- Team grows to >5 engineers (operational overhead becomes acceptable)
- Stakeholders demand rich UI for non-technical users

**Until then**: Lightweight approach maximizes velocity and minimizes complexity.

---

## Update Handling Strategy

### Problem Statement

**Context**: ~100 raw data updates per week from Data Inclusion/Carif Oref
**Challenge**: Updates arrive when original records are at various pipeline stages (enrichment, langage_clair, translation, validation)
**Risk**: Naive re-processing discards human work (manual enrichment, editorial review, quality validation)
**Goal**: Efficiently process updates while preserving human-in-the-loop work

### Update Scenarios

#### Scenario 1: Update Before Human Intervention
**Original Record Stage**: Ingestion or Reconciliation (fully automated stages)
**Strategy**: **Full Reprocessing**
**Rationale**: No human work to preserve, safe to reprocess from scratch

```
Update arrives → Detect via checksum → Mark original as superseded →
Process update through full pipeline
```

#### Scenario 2: Update During/After Human Intervention
**Original Record Stage**: Enrichment, Langage Clair, Translation, or Validation (human-in-the-loop stages)
**Strategy**: **Smart Catch-Up + Diff Review**
**Rationale**: Preserve human work, only review changes

```
Update arrives → Detect via checksum →
AI processes update to match original stage →
Generate diff → Human reviews diff →
Merge or override → Continue pipeline
```

### Recommended Approach: Smart Catch-Up with AI

#### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Update Detection                             │
│  Data Inclusion/Carif Oref → Checksum Comparison → Update Flag │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
              ┌──────────────┐
              │ Update Router│
              └──────┬───────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
┌───────────────┐        ┌────────────────────┐
│ Early Stage   │        │ Late Stage         │
│ (Auto-only)   │        │ (Human-in-loop)    │
├───────────────┤        ├────────────────────┤
│ Full Reprocess│        │ Smart Catch-Up     │
│               │        │ + Diff Review      │
└───────────────┘        └─────────┬──────────┘
                                   │
                                   ▼
                         ┌──────────────────────┐
                         │ AI Catch-Up Pipeline │
                         │ (Accelerated)        │
                         └──────────┬───────────┘
                                   │
                                   ▼
                         ┌──────────────────────┐
                         │ Diff Generation      │
                         │ (Original vs Update) │
                         └──────────┬───────────┘
                                   │
                                   ▼
                         ┌──────────────────────┐
                         │ Human Review UI      │
                         │ (Approve/Reject/Edit)│
                         └──────────┬───────────┘
                                   │
                                   ▼
                         ┌──────────────────────┐
                         │ Merge & Continue     │
                         │ Pipeline             │
                         └──────────────────────┘
```

#### Implementation Details

**1. Update Detection (Ingestion Stage)**

```python
class IngestionStage(PipelineStage):
    async def execute(self, program_id: str) -> dict:
        """Ingest raw data and detect updates."""
        raw_data = await self.fetch_from_source(program_id)
        checksum = self._compute_checksum(raw_data)

        # Check for existing record
        existing = await self.db.table("data_source_state") \
            .select("*") \
            .eq("source_id", program_id) \
            .single() \
            .execute()

        if existing:
            if existing.data["checksum"] == checksum:
                return {"status": "unchanged", "skip_pipeline": True}
            else:
                # Update detected
                return await self._handle_update(
                    program_id, raw_data, checksum, existing.data
                )
        else:
            # New record
            return await self._handle_new_record(program_id, raw_data, checksum)
```

**2. Update Router**

```python
class UpdateRouter:
    """Routes updates based on original record's current stage."""

    # Stages with no human intervention (safe to reprocess)
    AUTO_STAGES = ["ingestion", "reconciliation"]

    # Stages with human intervention (need smart catch-up)
    HUMAN_STAGES = ["enrichment", "langage_clair", "translation", "validation"]

    async def route_update(self, program_id: str, update_data: dict) -> str:
        """Determine update handling strategy."""
        original = await self.db.table("information_sheets") \
            .select("current_stage") \
            .eq("program_id", program_id) \
            .single() \
            .execute()

        if original.data["current_stage"] in self.AUTO_STAGES:
            return "full_reprocess"
        elif original.data["current_stage"] in self.HUMAN_STAGES:
            return "smart_catchup"
        else:
            # Already published, treat as new version
            return "new_version"
```

**3. Smart Catch-Up Pipeline**

```python
class SmartCatchUpOrchestrator:
    """Accelerate update processing to match original record's stage."""

    async def catch_up(self, program_id: str, target_stage: str) -> dict:
        """
        Process update through pipeline stages until reaching target_stage.
        Uses AI to accelerate human-in-the-loop stages.
        """
        stages_to_run = self._get_stages_until(target_stage)

        for stage in stages_to_run:
            if stage.name in UpdateRouter.HUMAN_STAGES:
                # Use AI to simulate human work (fast, no manual intervention)
                result = await self._ai_accelerated_stage(stage, program_id)
            else:
                # Run normal automated stage
                result = await stage.execute(program_id)

        return {"status": "caught_up", "final_stage": target_stage}

    async def _ai_accelerated_stage(self, stage: PipelineStage, program_id: str):
        """
        Use AI to quickly process stage without human intervention.
        Quality may be lower than human review, but sufficient for diff generation.
        """
        # Example: Langage Clair stage
        if stage.name == "langage_clair":
            return await self.ai_client.transform_to_plain_french(
                program_id,
                mode="fast",  # Skip human review
                quality_threshold=0.7  # Lower threshold for catch-up
            )
```

**4. Diff Generation**

```python
class DiffGenerator:
    """Generate human-readable diffs between original and updated records."""

    async def generate_diff(
        self,
        program_id: str,
        original_stage: str
    ) -> dict:
        """
        Compare original record (with human work) vs updated record (AI catch-up).
        Returns structured diff for human review.
        """
        original = await self._get_stage_data(program_id, original_stage, version="original")
        updated = await self._get_stage_data(program_id, original_stage, version="update")

        diff = {
            "program_id": program_id,
            "stage": original_stage,
            "changes": self._compute_changes(original, updated),
            "summary": self._generate_summary(original, updated),
            "impact_assessment": self._assess_impact(original, updated),
        }

        return diff

    def _compute_changes(self, original: dict, updated: dict) -> list:
        """Compute field-level changes."""
        changes = []

        for field in original.keys():
            if original[field] != updated.get(field):
                changes.append({
                    "field": field,
                    "original_value": original[field],
                    "updated_value": updated.get(field),
                    "change_type": self._classify_change(original[field], updated.get(field))
                })

        return changes

    def _classify_change(self, original, updated) -> str:
        """Classify change type for prioritization."""
        if original is None:
            return "addition"
        elif updated is None:
            return "deletion"
        elif self._is_minor_change(original, updated):
            return "minor_edit"  # Typo, formatting, etc.
        else:
            return "major_edit"  # Substantive content change
```

**5. Human Review UI (Diff Management)**

```python
# Streamlit-based diff review UI
import streamlit as st

class DiffReviewUI:
    """UI for human review of update diffs."""

    def render_diff_queue(self):
        """Display pending diffs for review."""
        diffs = self.db.table("update_diffs") \
            .select("*") \
            .eq("status", "pending_review") \
            .order("priority", desc=True) \
            .execute()

        st.title("Update Diff Review Queue")
        st.metric("Pending Reviews", len(diffs.data))

        for diff in diffs.data:
            with st.expander(f"Program {diff['program_id']} - {diff['stage']}"):
                self._render_diff(diff)

    def _render_diff(self, diff: dict):
        """Render individual diff with approval controls."""
        st.subheader("Summary")
        st.write(diff["summary"])

        st.subheader("Changes")
        for change in diff["changes"]:
            col1, col2, col3 = st.columns([2, 2, 1])

            with col1:
                st.text("Original")
                st.code(change["original_value"])

            with col2:
                st.text("Updated")
                st.code(change["updated_value"])

            with col3:
                st.text(change["change_type"])

        # Approval controls
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Accept All", key=f"accept_{diff['id']}"):
                self._approve_diff(diff["id"], action="accept_all")

        with col2:
            if st.button("Reject All", key=f"reject_{diff['id']}"):
                self._approve_diff(diff["id"], action="reject_all")

        with col3:
            if st.button("Review Manually", key=f"manual_{diff['id']}"):
                self._approve_diff(diff["id"], action="manual_review")
```

### Sampling Strategy for High Volume

**Problem**: 100 updates/week may be too many for full human review
**Solution**: **Risk-Based Sampling**

```python
class UpdateSampler:
    """Sample updates for human review based on risk assessment."""

    def should_review(self, diff: dict) -> bool:
        """Decide if diff requires human review."""
        risk_score = self._calculate_risk_score(diff)

        # Always review high-risk changes
        if risk_score > 0.8:
            return True

        # Sample medium-risk changes (e.g., 20%)
        if risk_score > 0.5:
            return random.random() < 0.2

        # Auto-approve low-risk changes
        return False

    def _calculate_risk_score(self, diff: dict) -> float:
        """Calculate risk score based on change characteristics."""
        score = 0.0

        # Major edits increase risk
        major_edits = sum(1 for c in diff["changes"] if c["change_type"] == "major_edit")
        score += major_edits * 0.3

        # Changes to critical fields increase risk
        critical_fields = ["title", "description", "contact_info", "eligibility"]
        critical_changes = sum(
            1 for c in diff["changes"] if c["field"] in critical_fields
        )
        score += critical_changes * 0.4

        # Deletions increase risk
        deletions = sum(1 for c in diff["changes"] if c["change_type"] == "deletion")
        score += deletions * 0.5

        return min(score, 1.0)
```

### Supabase Schema Extensions for Updates

```sql
-- Update Tracking Table
CREATE TABLE update_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    program_id TEXT NOT NULL,
    source_name TEXT NOT NULL,
    original_checksum TEXT NOT NULL,
    updated_checksum TEXT NOT NULL,
    original_stage TEXT NOT NULL,
    update_strategy TEXT NOT NULL CHECK (update_strategy IN ('full_reprocess', 'smart_catchup', 'new_version')),
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    status TEXT NOT NULL CHECK (status IN ('detected', 'processing', 'completed', 'failed')),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Diff Review Queue Table
CREATE TABLE update_diffs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    update_event_id UUID REFERENCES update_events(id) ON DELETE CASCADE,
    program_id TEXT NOT NULL,
    stage TEXT NOT NULL,
    original_data JSONB NOT NULL,
    updated_data JSONB NOT NULL,
    changes JSONB NOT NULL, -- Array of change objects
    summary TEXT,
    risk_score NUMERIC,
    priority INT DEFAULT 0, -- Higher = more urgent
    status TEXT NOT NULL CHECK (status IN ('pending_review', 'approved', 'rejected', 'manual_review')),
    reviewed_by TEXT,
    reviewed_at TIMESTAMPTZ,
    review_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_update_events_program_id ON update_events(program_id);
CREATE INDEX idx_update_events_status ON update_events(status);
CREATE INDEX idx_update_diffs_status ON update_diffs(status);
CREATE INDEX idx_update_diffs_priority ON update_diffs(priority DESC);
```

### Performance Analysis

**Volume**: 100 updates/week = ~14 updates/day = ~0.6 updates/hour

**Processing Time Estimates**:
- **Full Reprocess** (early stage): ~5-10 minutes per update
- **Smart Catch-Up** (late stage): ~2-5 minutes per update (AI-accelerated)
- **Diff Generation**: ~30 seconds per update
- **Human Review**: ~2-5 minutes per diff (if sampled)

**Total Weekly Effort**:
- **Automated Processing**: 100 updates × 5 min = 500 min (~8 hours)
- **Human Review** (20% sampling): 20 diffs × 3 min = 60 min (~1 hour)

**Verdict**: Manageable with smart catch-up + sampling strategy

### Recommendation

**Adopt Smart Catch-Up Strategy with Risk-Based Sampling**

**Phase 1 (MVP)**:
- Implement update detection via checksum
- Route updates (full reprocess vs smart catch-up)
- Build basic diff generation
- Manual review for all diffs (validate approach)

**Phase 2 (Optimization)**:
- Implement AI-accelerated catch-up pipeline
- Add risk-based sampling
- Build Streamlit diff review UI
- Automate low-risk approvals

**Phase 3 (Scale)**:
- Machine learning for risk scoring (learn from human decisions)
- Batch diff review (review multiple similar changes at once)
- Automated regression testing (ensure updates don't break downstream stages)

### Alternative Approaches Considered

**Alternative 1: Always Full Reprocess**
- ❌ Discards human work (enrichment, editorial review)
- ❌ Wastes human effort on repeated tasks
- ✅ Simpler implementation
- **Verdict**: Not viable due to human-in-the-loop stages

**Alternative 2: Manual Merge for All Updates**
- ✅ Preserves all human work
- ❌ 100 manual merges/week = unsustainable
- ❌ Slow, blocks pipeline
- **Verdict**: Not scalable

**Alternative 3: Ignore Updates**
- ❌ Stale data published to Réfugiés.info
- ❌ Violates data quality principles
- ✅ No implementation needed
- **Verdict**: Unacceptable for data quality

**Alternative 4: Smart Catch-Up + Sampling (RECOMMENDED)**
- ✅ Preserves human work
- ✅ Scalable (AI-accelerated, risk-based sampling)
- ✅ Balances quality and efficiency
- ⚠️ Requires AI infrastructure and diff UI
- **Verdict**: Best balance of quality, efficiency, and human oversight

---

## Next Steps

### Immediate Actions (This Week)
1. ✅ **Document decision** (this document)
2. 🔲 **Set up Supabase project** (create account, provision database)
3. 🔲 **Create schema** (run SQL migrations)
4. 🔲 **Implement orchestrator core** (`libs/common/src/nexus/common/orchestrator.py`)
5. 🔲 **Write orchestrator tests** (`libs/common/tests/unit/test_orchestrator.py`)

### Short-Term (Next 2 Weeks)
1. 🔲 **Implement stage base class** (`libs/common/src/nexus/common/pipeline_stage.py`)
2. 🔲 **Set up structured logging** (`structlog` configuration)
3. 🔲 **Implement retry logic** (`tenacity` decorators)
4. 🔲 **Create first stage** (ingestion) with TDD
5. 🔲 **Add update detection** (checksum-based change detection in ingestion)
6. 🔲 **Integration test** (orchestrator + ingestion + Supabase)

### Medium-Term (Next 4-11 Weeks)
1. 🔲 **Implement all 7 stages** (TDD for each)
2. 🔲 **End-to-end integration tests**
3. 🔲 **Implement update router** (full reprocess vs smart catch-up)
4. 🔲 **Build smart catch-up orchestrator** (AI-accelerated pipeline)
5. 🔲 **Implement diff generator** (compare original vs updated)
6. 🔲 **Build diff review UI** (Streamlit-based)
7. 🔲 **Add risk-based sampling** (prioritize high-risk changes)
8. 🔲 **Update handling integration tests**

### Long-Term (Next 3-6 Months)
1. 🔲 **Build monitoring dashboard** (Streamlit + Supabase)
2. 🔲 **Set up alerting** (email/Slack on failures)
3. 🔲 **Performance testing** (load test with realistic data volume)
4. 🔲 **Production deployment** (hosting, CI/CD, monitoring)
5. 🔲 **Operational runbooks** (incident response, debugging)
6. 🔲 **ML-based risk scoring** (learn from human review decisions)
7. 🔲 **Batch diff review** (review similar changes together)
8. 🔲 **Evaluate scale** (monitor performance, decide if migration needed)
9. 🔲 **Iterate based on feedback** (Réfugiés.info stakeholders, editorial team)

---

## Appendix: Supporting Libraries

### Recommended Python Libraries

**Core Orchestration**:
- `supabase-py`: Official Supabase Python client
- `asyncio`: Built-in async/await support
- `tenacity`: Retry logic with exponential backoff
- `structlog`: Structured logging (JSON format)

**Pipeline Stages**:
- `httpx`: Async HTTP client (API calls)
- `pydantic`: Data validation and serialization
- `beautifulsoup4`: Web scraping (enrichment stage)
- `openai`: AI API client (langage clair, translation)

**Testing**:
- `pytest`: Test framework
- `pytest-asyncio`: Async test support
- `pytest-mock`: Mocking utilities
- `faker`: Generate test data

**Monitoring**:
- `prometheus-client`: Metrics collection (optional)
- `sentry-sdk`: Error tracking (optional)

**Scheduling**:
- `APScheduler`: Lightweight cron-like scheduling
- Alternative: System cron (simpler, no Python dependency)

### Supabase Python SDK Example

```python
from supabase import create_client, Client

# Initialize Supabase client
supabase: Client = create_client(
    supabase_url="https://your-project.supabase.co",
    supabase_key="your-anon-key"
)

# Create workflow run
workflow_run = supabase.table("workflow_runs").insert({
    "program_id": "carif-oref-12345",
    "status": "running",
    "current_stage": "ingestion"
}).execute()

# Update stage execution
supabase.table("stage_executions").insert({
    "workflow_run_id": workflow_run.data[0]["id"],
    "stage_name": "ingestion",
    "status": "completed",
    "output_data": {"records_processed": 1}
}).execute()

# Query information sheets
sheets = supabase.table("information_sheets") \
    .select("*") \
    .eq("status", "draft") \
    .execute()
```

---

## Conclusion

**Decision**: Adopt **Lightweight Pythonic Approach** with **Supabase** for state management.

**Rationale**: Maximizes development velocity, minimizes operational complexity, and aligns with Constitutional Principle VII (Incremental Delivery). Enterprise orchestrators are overkill for a 7-stage linear pipeline processing hundreds of programs.

**Trade-off**: Sacrifice enterprise features (rich UI, complex DAGs, distributed execution) for simplicity, testability, and fast iteration. Migrate to enterprise orchestrator only if scale or complexity demands it.

**Next Step**: Set up Supabase project and implement orchestrator core.

---

**Document Status**: ✅ Complete
**Approved By**: [Pending Review]
**Implementation Start**: [TBD]
