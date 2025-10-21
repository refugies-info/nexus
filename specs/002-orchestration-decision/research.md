# Technical Research: Pipeline Orchestration & Update Handling

**Feature**: Pipeline Orchestration & Update Handling
**Date**: 2025-10-20
**Status**: Complete

## Overview

This document consolidates technical research for implementing hybrid orchestration infrastructure using n8n + Python services. Research covers n8n integration patterns, Supabase schema design, FastAPI best practices, and diff generation algorithms.

## 1. n8n Integration Architecture

### Decision: HTTP Request Nodes + FastAPI Services

**Rationale**:
- n8n's HTTP Request node provides flexible API integration
- FastAPI services expose REST endpoints for each orchestration function
- Clear separation: n8n handles workflow logic, Python handles business logic
- Standard HTTP/JSON communication enables easy testing and debugging

**Alternatives Considered**:
- **n8n Code Node (JavaScript)**: Rejected - complex logic in JavaScript defeats TDD compliance goal
- **n8n Python Node**: Rejected - limited library support, harder to test in isolation
- **Direct database access from n8n**: Rejected - violates service encapsulation, harder to test

**Implementation Pattern**:
```
n8n Workflow
  ↓ HTTP POST /api/workflows/execute
FastAPI Service (Python)
  ↓ Supabase Client
Supabase (PostgreSQL)
```

**Best Practices**:
- Use correlation IDs to link n8n executions with Python service logs
- Implement idempotency keys for retry safety
- Return structured responses with status codes (200/201 success, 4xx client error, 5xx server error)
- Use webhooks for long-running operations (>30 seconds)

**References**:
- n8n HTTP Request Node: https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/
- FastAPI Best Practices: https://fastapi.tiangolo.com/tutorial/

---

## 2. Supabase Schema Design

### Decision: Normalized Schema with JSONB for Flexibility

**Rationale**:
- Normalized tables for core entities (workflow_runs, stage_executions, update_events, update_diffs)
- JSONB columns for flexible metadata storage (stage-specific data, diff details)
- PostgreSQL provides ACID guarantees for state management
- Supabase real-time subscriptions enable live monitoring dashboards

**Schema Overview**:

**workflow_runs** (tracks pipeline execution):
- `id` (UUID, primary key)
- `program_id` (TEXT, Data Inclusion unique ID)
- `current_stage` (TEXT, enum: ingestion|reconciliation|enrichment|langage_clair|translation|validation|publication)
- `status` (TEXT, enum: pending|running|completed|failed)
- `created_at` (TIMESTAMPTZ)
- `updated_at` (TIMESTAMPTZ)
- `completed_at` (TIMESTAMPTZ, nullable)
- `error_message` (TEXT, nullable)

**stage_executions** (tracks individual stage runs):
- `id` (UUID, primary key)
- `workflow_run_id` (UUID, foreign key to workflow_runs)
- `stage_name` (TEXT)
- `status` (TEXT, enum: pending|running|completed|failed)
- `retry_count` (INTEGER, default 0)
- `input_data` (JSONB)
- `output_data` (JSONB, nullable)
- `execution_metadata` (JSONB, e.g., processing time, AI model used)
- `created_at` (TIMESTAMPTZ)
- `completed_at` (TIMESTAMPTZ, nullable)
- `error_message` (TEXT, nullable)

**information_sheets** (tracks program data with progressive enhancement):
- `id` (UUID, primary key)
- `program_id` (TEXT, unique, Data Inclusion unique ID)
- `refugies_info_id` (TEXT, nullable, MongoDB ObjectId from Réfugiés.info system)
- `current_stage` (TEXT)
- `status` (TEXT, enum: draft|in_review|approved|published)
- `ingested_data` (JSONB)
- `reconciled_data` (JSONB, nullable)
- `enriched_data` (JSONB, nullable)
- `langage_clair_data` (JSONB, nullable)
- `translated_data` (JSONB, nullable)
- `validated_data` (JSONB, nullable)
- `published_data` (JSONB, nullable)
- `created_at` (TIMESTAMPTZ)
- `updated_at` (TIMESTAMPTZ)

**update_events** (tracks source data updates):
- `id` (UUID, primary key)
- `program_id` (TEXT, Data Inclusion unique ID)
- `original_checksum` (TEXT, SHA-256 hash of complete service JSON)
- `updated_checksum` (TEXT, SHA-256 hash of complete service JSON)
- `original_stage` (TEXT, stage of original program when update detected)
- `update_strategy` (TEXT, enum: full_reprocess|smart_catchup)
- `processing_status` (TEXT, enum: pending|processing|completed|failed)
- `created_at` (TIMESTAMPTZ)
- `completed_at` (TIMESTAMPTZ, nullable)

**Checksum Calculation Strategy**:
The checksum is calculated on the **complete Data Inclusion service JSON** to detect any changes in the source data. This includes:

**Core Service Fields** (always included):
- `id` (service identifier)
- `nom` (service name)
- `description` (service description)
- `date_maj` (last modification date from source)
- `type` (service type)
- `thematiques` (service themes)
- `frais` (cost: free/paid)
- `frais_precisions` (cost details)

**Target Audience Fields**:
- `publics` (target audiences)
- `publics_precisions` (audience details)
- `conditions_acces` (access conditions)

**Location Fields**:
- `commune` (city)
- `code_postal` (postal code)
- `code_insee` (INSEE code)
- `adresse` (address)
- `complement_adresse` (address complement)
- `longitude`, `latitude` (coordinates)

**Contact Fields**:
- `telephone` (phone)
- `courriel` (email)
- `contact_nom_prenom` (contact name)

**Access & Mobilization Fields**:
- `modes_accueil` (reception modes)
- `zone_eligibilite` (eligibility zone)
- `lien_source` (source link)
- `modes_mobilisation` (mobilization modes)
- `mobilisable_par` (who can mobilize)
- `mobilisation_precisions` (mobilization details)

**Schedule Fields**:
- `horaires_accueil` (reception hours)
- `volume_horaire_hebdomadaire` (weekly hours)
- `nombre_semaines` (number of weeks)

**Metadata Fields** (EXCLUDED from checksum):
- `source` (data producer - doesn't affect content)
- `structure_id` (parent structure - managed separately)
- `lien_mobilisation` (mobilization link - operational, not content)

**Checksum Algorithm**:
```python
import hashlib
import json

def calculate_service_checksum(service_data: dict) -> str:
    """
    Calculate SHA-256 checksum of Data Inclusion service data.

    Excludes metadata fields (source, structure_id, lien_mobilisation).
    Normalizes JSON to ensure consistent hashing.
    """
    # Create a copy excluding metadata
    content_data = {
        k: v for k, v in service_data.items()
        if k not in ('source', 'structure_id', 'lien_mobilisation')
    }

    # Sort keys for consistent JSON serialization
    normalized_json = json.dumps(content_data, sort_keys=True, ensure_ascii=False)

    # Calculate SHA-256 hash
    return hashlib.sha256(normalized_json.encode('utf-8')).hexdigest()
```

**Rationale**:
- **Complete JSON**: Captures all content changes (name, description, location, contact, schedule, etc.)
- **Exclude metadata**: `source` and `structure_id` are organizational, not content
- **Normalized JSON**: Sort keys to ensure consistent hashing regardless of field order
- **SHA-256**: Cryptographically secure, collision-resistant, 64-character hex string
- **UTF-8 encoding**: Handles French characters and special characters correctly

**Collision Resistance Details**:
- **SHA-256 properties**: Produces 256-bit (64-character hex) output with cryptographic guarantees
  - Collision resistance: Computationally infeasible to find two inputs with same hash
  - Avalanche effect: Single bit change in input produces completely different hash
  - One-way function: Cannot reverse-engineer input from hash
- **For Nexus**: Two different service updates will always have different checksums (no false negatives); extremely unlikely two different services produce same checksum (no false positives)

**UTF-8 Encoding Details**:
- **Why UTF-8**: Handles French characters (é, è, ê, ë, à, ç) and special characters (€, •, —) consistently
- **Implementation**: Line 177 uses `ensure_ascii=False` to preserve Unicode; Line 180 uses `.encode('utf-8')` for consistent byte representation
- **For Nexus**: Service names like "Cours de français" and descriptions with accents hash consistently every time, preventing false update detection due to encoding differences
- **Examples**:
  - `"Cours de français"` (with é) ≠ `"Cours de francais"` (without é) → Different checksums ✓
  - `{"nom": "Cours", "type": "formation"}` = `{"type": "formation", "nom": "Cours"}` → Same checksum ✓ (due to key sorting)
  - `"Éligibilité"` always encodes to same bytes → Consistent hash ✓

**Update Detection Flow**:
When fetching from Data Inclusion API:
1. Calculate checksum of fetched service JSON
2. Look up existing `information_sheet` by `program_id`
3. Compare fetched checksum with stored checksum in `information_sheets.ingested_data`
4. If different → create `update_event`:
   - `original_checksum`: Checksum from existing `information_sheets.ingested_data`
   - `updated_checksum`: Checksum from newly fetched data
   - `original_stage`: **Copied from `information_sheets.current_stage`** (snapshot at detection time)
   - `update_strategy`: Determined by `original_stage` value
     - If `original_stage` IN ('ingestion', 'reconciliation') → `full_reprocess`
     - If `original_stage` IN ('enrichment', 'langage_clair', 'translation', 'validation', 'publication') → `smart_catchup`

**`original_stage` Field Lifecycle**:

**Population** (when update is detected):
- **Source**: Current value of `information_sheets.current_stage` for the program
- **Purpose**: Snapshot the stage at the moment the update was detected
- **Immutable**: Once set, this field NEVER changes (it's a historical record)

**Example Scenario**:
```
Day 1: Program ingested
  - information_sheets.current_stage = 'ingestion'
  - information_sheets.status = 'draft'

Day 2: Program progresses through pipeline
  - information_sheets.current_stage = 'enrichment'
  - information_sheets.status = 'draft'

Day 3: Human enrichment work completed
  - information_sheets.current_stage = 'langage_clair'
  - information_sheets.status = 'in_review'

Day 4: Update detected from Data Inclusion
  - Create update_event:
    - original_stage = 'langage_clair' (copied from information_sheets.current_stage)
    - update_strategy = 'smart_catchup' (because original_stage is late stage)
    - processing_status = 'pending'

  - information_sheets.current_stage remains 'langage_clair' (unchanged)

Day 5: Smart catch-up processing
  - AI processes update through: ingestion → reconciliation → enrichment → langage_clair
  - Generate diff comparing original (with human work) vs updated (AI catch-up)
  - update_event.original_stage still 'langage_clair' (immutable historical record)

Day 6: Editorial review
  - Editor approves diff
  - Merge changes into information_sheets
  - information_sheets.current_stage advances to 'translation'
  - update_event.original_stage still 'langage_clair' (never changes)
```

**Key Points**:
- **`information_sheets.current_stage`**: MUTABLE - advances as program progresses through pipeline
- **`update_events.original_stage`**: IMMUTABLE - frozen snapshot at update detection time
- **Purpose of immutability**: Preserves historical record of what stage the program was at when update arrived (important for audit trail and understanding update routing decisions)

**update_diffs** (tracks diffs awaiting review):
- `id` (UUID, primary key)
- `program_id` (TEXT, Data Inclusion unique ID)
- `update_event_id` (UUID, foreign key to update_events)
- `stage` (TEXT, stage where diff was generated)
- `original_data` (JSONB)
- `updated_data` (JSONB)
- `changes` (JSONB, structured diff: additions, deletions, modifications)
- `risk_score` (FLOAT, 0.0-1.0)
- `priority` (TEXT, enum: low|medium|high)
- `review_status` (TEXT, enum: pending|approved|rejected|edited)
- `reviewed_by` (UUID, nullable, Supabase Auth user ID)
- `reviewed_at` (TIMESTAMPTZ, nullable)
- `created_at` (TIMESTAMPTZ)

**Indexes**:
- `workflow_runs`: (program_id), (status), (current_stage)
- `stage_executions`: (workflow_run_id), (stage_name, status)
- `information_sheets`: (program_id UNIQUE), (refugies_info_id), (status)
- `update_events`: (program_id), (processing_status)
- `update_diffs`: (program_id), (review_status), (priority)

**Alternatives Considered**:
- **Single monolithic table**: Rejected - harder to query, poor normalization
- **Document database (MongoDB)**: Rejected - Supabase provides PostgreSQL, ACID guarantees important for state management
- **Separate databases per concern**: Rejected - adds operational complexity, harder to maintain referential integrity

**References**:
- Supabase Database Design: https://supabase.com/docs/guides/database/tables
- PostgreSQL JSONB: https://www.postgresql.org/docs/current/datatype-json.html

---

## 3. FastAPI Service Architecture

### Decision: Service Layer Pattern with Repository Pattern

**Rationale**:
- **Service Layer**: Encapsulates business logic (update detection, smart catch-up, diff generation, risk scoring)
- **Repository Pattern**: Abstracts Supabase database access, enables easy mocking for tests
- **Pydantic Models**: Type-safe request/response validation, automatic OpenAPI documentation
- **Dependency Injection**: FastAPI's DI system enables clean testing

**Architecture**:
```
FastAPI Router (api/workflows.py)
  ↓ depends on
Service Layer (services/update_detector.py)
  ↓ depends on
Repository Layer (db/update_repo.py)
  ↓ uses
Supabase Client (db/client.py)
```

**Best Practices**:
- Use async/await for I/O operations (Supabase queries, external API calls)
- Implement structured logging with correlation IDs
- Use Pydantic BaseSettings for configuration management
- Implement health check endpoints (/health, /ready)
- Use FastAPI middleware for request logging and error handling
- Implement rate limiting for external-facing endpoints

**Testing Strategy**:
- **Unit tests**: Mock repository layer, test service logic in isolation
- **Integration tests**: Use test Supabase instance, test end-to-end flows
- **Contract tests**: Validate API contracts match n8n expectations

**Alternatives Considered**:
- **Flask**: Rejected - FastAPI provides better async support, automatic OpenAPI docs, type validation
- **Django**: Rejected - too heavy for microservices, ORM not needed (using Supabase client directly)
- **Direct Supabase access from n8n**: Rejected - violates TDD compliance, harder to test

**References**:
- FastAPI Best Practices: https://fastapi.tiangolo.com/tutorial/bigger-applications/
- Repository Pattern: https://martinfowler.com/eaaCatalog/repository.html

---

## 4. Diff Generation Algorithm

### Decision: Field-Level Diff with Semantic Classification

**Rationale**:
- Field-level granularity enables precise change detection
- Semantic classification (addition, deletion, minor edit, major edit) enables risk scoring
- JSON diff libraries (jsondiff, deepdiff) provide robust comparison
- Structured diff format enables visual rendering in Streamlit UI

**Algorithm**:
1. **Normalize data**: Convert both original and updated data to canonical JSON format
2. **Compute diff**: Use deepdiff library to generate structured diff
3. **Classify changes**:
   - **Addition**: New field added
   - **Deletion**: Field removed
   - **Minor edit**: Typo fix, formatting change (Levenshtein distance < threshold)
   - **Major edit**: Content change (Levenshtein distance >= threshold)
4. **Calculate risk score**: Weighted sum based on change types
   - Deletion: high risk (0.8-1.0)
   - Major edit to critical fields: high risk (0.8-1.0)
   - Addition: medium risk (0.5-0.7)
   - Minor edit: low risk (0.0-0.4)

**Risk Scoring Formula**:
```python
risk_score = (
    deletions * 0.9 +
    major_edits_critical * 0.8 +
    major_edits_normal * 0.6 +
    additions * 0.5 +
    minor_edits * 0.2
) / total_fields
```

**Critical Fields** (higher risk weight, based on Data Inclusion schema):
- `nom` * (Service name/title) - Required, 3-150 chars
- `description` * (Service description) - Required, 50-2000 chars, impacts quality score
- `publics` * (Target audiences) - Required, eligibility criteria
- `date_maj` * (Last modification date) - Required, indicates source data update timing
- `conditions_acces` (Access conditions) - Eligibility requirements
- `adresse` (Address) - Location information
- `commune` (City) - Location information
- `code_postal` (Postal code) - Location information
- `telephone` (Phone) - Contact information
- `courriel` (Email) - Contact information
- `contact_nom_prenom` (Contact name) - Contact information
- `frais` (Cost: free/paid) - Service accessibility
- `zone_eligibilite` (Eligibility zone) - Geographic scope

**Rationale**: Fields marked with `*` are required in the schema. Changes to these fields have higher impact on service discoverability and user eligibility. Location and contact fields are critical for users to access the service.

**Alternatives Considered**:

### **Option A: deepdiff Library (Recommended for MVP)**

**Approach**: Algorithmic field-level diff with heuristic risk scoring

**Pros**:
- ✅ **Deterministic**: Same input always produces same output (reproducible)
- ✅ **Fast**: Milliseconds per diff (no API latency)
- ✅ **Cost**: Zero cost (open source library)
- ✅ **Offline**: No external API dependency
- ✅ **Structured output**: JSON diff format easy to render in UI
- ✅ **Testable**: Unit tests can validate diff logic
- ✅ **Privacy**: No data sent to external services
- ✅ **Explainable**: Clear rules for risk scoring (deletions = high risk, etc.)

**Cons**:
- ❌ **Semantic understanding**: Cannot understand meaning (e.g., "10€" vs "10 euros" treated as different)
- ❌ **Context-blind**: Cannot assess importance based on domain knowledge
- ❌ **Fixed rules**: Risk scoring based on predefined heuristics, not learned from data
- ❌ **False positives**: May flag benign changes as high-risk (e.g., reformatting)

**Best for**: MVP where speed, cost, and determinism are priorities

---

### **Option B: LLM-as-Judge (Considered for Phase 3)**

**Approach**: Use LLM (e.g., GPT-4) to analyze diffs and assess risk

**Prompt Example**:
```
You are reviewing an update to a French language learning program information sheet.

Original data:
{original_json}

Updated data:
{updated_json}

Analyze the changes and provide:
1. List of changes (additions, deletions, modifications)
2. Risk assessment (low/medium/high) with justification
3. Recommendation (auto-approve, manual review, reject)

Consider:
- Critical fields: program name, provider, location, contact, eligibility
- Minor changes: typo fixes, formatting, punctuation
- Semantic equivalence: "10€" vs "10 euros"
- Context: French administrative vocabulary, refugee/immigrant audience
```

**Pros**:
- ✅ **Semantic understanding**: Can recognize "10€" and "10 euros" as equivalent
- ✅ **Context-aware**: Understands domain (French language learning, refugee services)
- ✅ **Nuanced risk assessment**: Can assess importance based on meaning, not just structure
- ✅ **Adaptive**: Can handle edge cases not covered by rules
- ✅ **Natural language explanations**: Provides human-readable justifications
- ✅ **Cultural awareness**: Can flag culturally sensitive changes (e.g., religious requirements)

**Cons**:
- ❌ **Non-deterministic**: Same input may produce different outputs (stochastic)
- ❌ **Slow**: 1-5 seconds per diff (API latency)
- ❌ **Cost**: $0.01-0.10 per diff (100 updates/week = $5-50/week = $260-2600/year)
- ❌ **API dependency**: Requires OpenAI API availability
- ❌ **Privacy concerns**: Sends program data to external service (GDPR considerations)
- ❌ **Harder to test**: Non-deterministic outputs complicate unit testing
- ❌ **Explainability**: "Black box" decision-making (harder to debug)
- ❌ **Prompt engineering**: Requires careful prompt design and maintenance

**Best for**: Phase 3 enhancement when cost and latency are acceptable, and semantic understanding is critical

---

### **Option C: Hybrid Approach (Future Consideration)**

**Approach**: Use deepdiff for structure, LLM for semantic analysis

**Flow**:
1. **deepdiff**: Generate structured diff (fast, deterministic)
2. **Heuristic filter**: Auto-approve obvious low-risk changes (typos, formatting)
3. **LLM judge**: For ambiguous cases, use LLM to assess semantic importance
4. **Human review**: High-risk changes flagged by either system

**Pros**:
- ✅ **Best of both worlds**: Fast + deterministic for simple cases, semantic for complex
- ✅ **Cost optimization**: Only use LLM for ~20% of diffs (reduces cost by 80%)
- ✅ **Fallback**: If LLM API unavailable, deepdiff still works

**Cons**:
- ⚠️ **Complexity**: Two systems to maintain
- ⚠️ **Threshold tuning**: Need to define when to escalate to LLM

---

### **Decision Matrix**

| Criterion | deepdiff | LLM-as-Judge | Hybrid |
|-----------|----------|--------------|--------|
| **Speed** | ✅ <10ms | ❌ 1-5s | ⚠️ 10ms-5s |
| **Cost** | ✅ $0 | ❌ $260-2600/year | ⚠️ $50-500/year |
| **Determinism** | ✅ 100% | ❌ Stochastic | ⚠️ Partial |
| **Semantic Understanding** | ❌ None | ✅ Excellent | ✅ Good |
| **Privacy** | ✅ Local | ❌ External API | ⚠️ Partial external |
| **Testability** | ✅ Easy | ❌ Hard | ⚠️ Medium |
| **Explainability** | ✅ Clear rules | ❌ Black box | ⚠️ Mixed |
| **MVP Readiness** | ✅ Yes | ❌ No | ❌ No |

---

### **Recommendation: deepdiff for MVP, LLM-as-Judge for Phase 3**

**Phase 1 (MVP)**: Use deepdiff with heuristic risk scoring
- Rationale: Fast, cost-free, deterministic, privacy-compliant
- Acceptable trade-off: Some false positives (editorial team reviews more diffs than necessary)
- Mitigation: Iteratively tune risk scoring thresholds based on editorial feedback (CAR-014)

**Phase 2 (Optimization)**: Collect data on editorial decisions
- Track: Which diffs were approved/rejected, time spent per review
- Analyze: Common false positives (benign changes flagged as high-risk)
- Refine: Adjust heuristic rules to reduce false positives

**Phase 3 (Enhancement)**: Introduce LLM-as-judge for ambiguous cases
- Trigger: If heuristic risk score is borderline (0.45-0.55), escalate to LLM
- Cost: ~20% of diffs use LLM = $50-500/year (acceptable)
- Benefit: Reduce editorial review workload by catching semantic equivalences

**Phase 4 (ML-based)**: Train custom model on historical decisions
- Dataset: Editorial team's approve/reject decisions on diffs
- Model: Fine-tuned classifier (cheaper and faster than GPT-4)
- Benefit: Deterministic + semantic understanding + cost-effective

---

**References**:
- deepdiff library: https://github.com/seperman/deepdiff
- Levenshtein distance: https://en.wikipedia.org/wiki/Levenshtein_distance
- LLM-as-Judge pattern: https://arxiv.org/abs/2306.05685
- OpenAI Pricing: https://openai.com/pricing
- Data Inclusion Service Schema (HTML): https://gip-inclusion.github.io/data-inclusion-schema/latest/service/
- Data Inclusion Service Schema (JSON): https://raw.githubusercontent.com/gip-inclusion/data-inclusion-schema/main/schemas/v1/service.json

---

## 5. Streamlit Diff Review UI

### Decision: Streamlit with Supabase Auth Integration

**Rationale**:
- Streamlit provides rapid UI development for data-heavy applications
- Native support for side-by-side comparison, syntax highlighting
- Supabase Auth integration via streamlit-supabase-auth library
- RBAC enforced at API level (FastAPI checks Supabase JWT)

**UI Components**:
1. **Authentication**: Supabase Auth login page
2. **Diff Queue**: Table showing pending diffs sorted by priority (high-risk first)
3. **Diff Viewer**: Side-by-side comparison with changes highlighted
4. **Approval Controls**: Approve all / Reject all / Manual edit buttons
5. **Audit Trail**: Shows who reviewed what and when

**Best Practices**:
- Use st.session_state for authentication state management
- Implement optimistic locking to prevent concurrent edits
- Cache Supabase queries with st.cache_data
- Use st.columns for side-by-side layout
- Implement keyboard shortcuts for faster review (e.g., 'a' approve, 'r' reject)

**Alternatives Considered**:
- **React + Supabase**: Rejected - slower development, overkill for internal tool
- **Django Admin**: Rejected - less flexible for custom diff rendering
- **Jupyter Notebook**: Rejected - not suitable for production editorial workflow

**References**:
- Streamlit Documentation: https://docs.streamlit.io/
- streamlit-supabase-auth: https://github.com/SiddhantSadangi/st-supabase-connection

---

## 6. n8n Workflow Export & Version Control

### Decision: Export Workflows as JSON, Store in Git

**Rationale**:
- n8n workflows can be exported as JSON files
- JSON files tracked in Git enable version control, code review, rollback
- CI/CD can validate workflow syntax, deploy to n8n via API
- Documentation in README.md explains workflow structure

**Workflow Organization**:
```
workflows/
├── pipeline-orchestration.json    # Main 7-stage pipeline
├── update-detection.json          # Update detection and routing
├── smart-catchup.json             # AI-accelerated catch-up
└── README.md                      # Workflow documentation
```

**Best Practices**:
- Use descriptive node names in n8n (e.g., "Call Update Detector API" not "HTTP Request")
- Document workflow logic in README.md with diagrams
- Use n8n's built-in error handling nodes for retry logic
- Implement webhook triggers for manual interventions
- Use n8n's environment variables for configuration (API URLs, credentials)

**CI/CD Integration**:
- Validate JSON syntax in CI pipeline
- Deploy workflows to n8n via API (POST /workflows)
- Run smoke tests after deployment

**Alternatives Considered**:
- **n8n Cloud only**: Rejected - want self-hosting option, version control important
- **Terraform for n8n**: Rejected - n8n doesn't have official Terraform provider
- **Manual workflow management**: Rejected - no version control, hard to review changes

**References**:
- n8n Workflow Export: https://docs.n8n.io/workflows/export-import/
- n8n API: https://docs.n8n.io/api/

---

## 7. Error Handling & Retry Strategy

### Decision: Exponential Backoff with Circuit Breaker

**Rationale**:
- Exponential backoff prevents thundering herd problem
- Circuit breaker prevents cascading failures
- n8n provides built-in retry logic, Python services implement tenacity library
- Max retry duration: 24 hours for external API failures (Data Inclusion, Carif Oref)

**Retry Strategy**:
- **Transient errors** (network timeout, 5xx): Retry with exponential backoff
  - Initial delay: 1 second
  - Max delay: 5 minutes
  - Max retries: 10
- **Client errors** (4xx): No retry, log error, alert operators
- **External API unavailable**: Queue programs, retry up to 24 hours

**Circuit Breaker**:
- Open circuit after 5 consecutive failures
- Half-open after 60 seconds (test with single request)
- Close circuit after 3 consecutive successes

**Alternatives Considered**:
- **Fixed retry interval**: Rejected - can overwhelm failing service
- **Infinite retries**: Rejected - can cause resource exhaustion
- **No circuit breaker**: Rejected - cascading failures harder to recover from

**References**:
- Tenacity library: https://tenacity.readthedocs.io/
- Circuit Breaker pattern: https://martinfowler.com/bliki/CircuitBreaker.html

---

## 8. Observability & Monitoring

### Decision: Structured Logging + Supabase Metrics + n8n Execution Logs

**Rationale**:
- Structured logs (JSON) enable easy parsing and querying
- Supabase tracks workflow state, enables custom dashboards
- n8n provides built-in execution logs with visual debugging
- Correlation IDs link n8n executions with Python service logs

**Logging Strategy**:
- **Python services**: Use structlog for structured JSON logging
- **Log levels**: DEBUG (development), INFO (production), ERROR (always)
- **Correlation ID**: Generated by n8n, passed to Python services via HTTP header
- **Log fields**: timestamp, level, correlation_id, service, function, message, metadata

**Metrics**:
- **Workflow metrics**: Total runs, success rate, average duration per stage
- **Update metrics**: Updates detected, smart catch-up success rate, diff review time
- **Performance metrics**: API response time (p50, p95, p99), database query time

**Dashboards**:
- **Operator dashboard**: Current pipeline status, failed programs, error rates
- **Editorial dashboard**: Pending diffs, review queue depth, approval rates

**Alternatives Considered**:
- **External monitoring (Datadog, New Relic)**: Deferred - out of scope for MVP
- **Prometheus + Grafana**: Deferred - adds operational complexity
- **ELK stack**: Deferred - overkill for MVP scale

**References**:
- structlog: https://www.structlog.org/
- Supabase Analytics: https://supabase.com/docs/guides/platform/metrics

---

## Summary

All technical unknowns resolved. Key decisions:
1. **n8n + FastAPI**: HTTP integration pattern
2. **Supabase**: Normalized schema with JSONB flexibility
3. **FastAPI**: Service + Repository pattern
4. **Diff generation**: Field-level with semantic classification
5. **Streamlit**: Rapid UI development with Supabase Auth
6. **Version control**: n8n workflows as JSON in Git
7. **Error handling**: Exponential backoff + circuit breaker
8. **Observability**: Structured logging + Supabase metrics

Ready to proceed to Phase 1 (data model and contracts).
