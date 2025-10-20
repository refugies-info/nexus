# Quickstart: Pipeline Orchestration & Update Handling

**Feature**: Pipeline Orchestration & Update Handling
**Branch**: `002-orchestration-decision`
**Last Updated**: 2025-10-20

## Overview

This quickstart guide helps developers set up and run the Nexus pipeline orchestration system locally. The system uses a hybrid architecture with **n8n** for workflow orchestration and **Python FastAPI services** for business logic, with **Supabase** for state management.

## Prerequisites

- **Python 3.11+** with `uv` package manager
- **Node.js 18+** with `pnpm`
- **Docker** (for n8n and Supabase)
- **Supabase CLI** (optional, for local development)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     n8n Workflows                        │
│  (Orchestration, Retry Logic, Error Handling)           │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST
                     ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Orchestration Service               │
│  (Business Logic, Validation, AI Integration)           │
└────────────────────┬────────────────────────────────────┘
                     │ Supabase Client
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Supabase (PostgreSQL)                   │
│  (State Management, Data Storage, Real-time Updates)    │
└─────────────────────────────────────────────────────────┘
```

## Quick Start (5 minutes)

### 1. Clone and Setup

```bash
# Clone repository
git clone <repository-url>
cd nexus

# Checkout orchestration branch
git checkout 002-orchestration-decision

# Install Python dependencies
uv sync

# Install Node.js dependencies
pnpm install
```

### 2. Start Supabase Locally

```bash
# Start Supabase (PostgreSQL + Auth + Storage)
supabase start

# Note the API URL and anon key from output
# Example output:
#   API URL: http://localhost:54321
#   anon key: eyJhbGc...
```

### 3. Initialize Database Schema

```bash
# Apply migrations
supabase db reset

# Or manually run schema from data-model.md
psql -h localhost -p 54322 -U postgres -d postgres -f scripts/init-schema.sql
```

### 4. Configure Environment

Create `.env` file in repository root:

```bash
# Supabase
SUPABASE_URL=http://localhost:54321
SUPABASE_KEY=<your-anon-key>

# Vercel AI SDK Gateway (for enrichment, langage clair, translation)
VERCEL_AI_GATEWAY_URL=<your-vercel-gateway-url>
VERCEL_AI_GATEWAY_TOKEN=<your-vercel-gateway-token>

# Data Inclusion API (staging - no API key required)
DATA_INCLUSION_API_URL=https://staging.api.data.inclusion.beta.gouv.fr
```

### 5. Start Orchestration Service

```bash
# Start FastAPI service
cd apps/orchestration
uv run uvicorn src.main:app --reload --port 8000

# Service available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### 6. Start n8n

```bash
# Start n8n with Docker
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -e N8N_BASIC_AUTH_ACTIVE=true \
  -e N8N_BASIC_AUTH_USER=admin \
  -e N8N_BASIC_AUTH_PASSWORD=admin \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

# Access n8n at http://localhost:5678
# Login: admin / admin
```

### 7. Import n8n Workflows

1. Open n8n at http://localhost:5678
2. Navigate to **Workflows** → **Import from File**
3. Import workflows from `specs/002-orchestration-decision/contracts/n8n-workflows/`:
   - `pipeline-orchestration.json` (main workflow)
   - `update-handler.json` (update detection and routing)
   - `diff-generator.json` (diff generation for review)

### 8. Test Pipeline

```bash
# Trigger pipeline with test data
curl -X POST http://localhost:8000/api/workflows/execute \
  -H "Content-Type: application/json" \
  -d '{
    "program_id": "test-program-001",
    "source": "data_inclusion",
    "data": {
      "nom": "Cours de français - Niveau A1",
      "description": "Cours de français pour débutants",
      "contact": "contact@example.fr"
    }
  }'

# Check workflow status
curl http://localhost:8000/api/workflows/test-program-001/status
```

## Development Workflow

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test suite
uv run pytest tests/unit/orchestration/
uv run pytest tests/integration/orchestration/
uv run pytest tests/contract/orchestration/

# Run with coverage
uv run pytest --cov=src --cov-report=html
```

### Monitoring Pipeline Execution

```bash
# View workflow runs
curl http://localhost:8000/api/workflows/runs

# View stage executions for a workflow
curl http://localhost:8000/api/workflows/{workflow_id}/stages

# View pending diffs for review
curl http://localhost:8000/api/diffs?status=pending
```

### Database Queries

```sql
-- View all workflow runs
SELECT id, program_id, current_stage, status, created_at
FROM workflow_runs
ORDER BY created_at DESC
LIMIT 10;

-- View failed stages
SELECT wr.program_id, se.stage_name, se.error_message, se.created_at
FROM stage_executions se
JOIN workflow_runs wr ON se.workflow_run_id = wr.id
WHERE se.status = 'failed'
ORDER BY se.created_at DESC;

-- View pending diffs
SELECT program_id, stage, risk_score, priority, created_at
FROM update_diffs
WHERE review_status = 'pending'
ORDER BY priority DESC, created_at ASC;
```

## Key Endpoints

### Orchestration Service (FastAPI)

- `POST /api/workflows/execute` - Start new workflow
- `GET /api/workflows/{workflow_id}/status` - Get workflow status
- `GET /api/workflows/runs` - List all workflow runs
- `POST /api/stages/{stage_name}/execute` - Execute specific stage
- `GET /api/diffs` - List pending diffs
- `POST /api/diffs/{diff_id}/approve` - Approve diff
- `POST /api/diffs/{diff_id}/reject` - Reject diff

### n8n Webhooks

- `POST /webhook/pipeline-start` - Trigger pipeline workflow
- `POST /webhook/update-detected` - Trigger update handler
- `POST /webhook/diff-review` - Trigger diff generation

## Project Structure

```
apps/orchestration/              # Python orchestration service
├── src/
│   ├── api/                     # FastAPI routes
│   │   ├── workflows.py         # Workflow management endpoints
│   │   ├── stages.py            # Stage execution endpoints
│   │   └── diffs.py             # Diff review endpoints
│   ├── services/                # Business logic
│   │   ├── workflow_service.py  # Workflow orchestration
│   │   ├── stage_service.py     # Stage execution
│   │   ├── update_service.py    # Update detection & routing
│   │   └── diff_service.py      # Diff generation & review
│   ├── models/                  # Pydantic models
│   │   ├── workflow.py          # Workflow models
│   │   ├── stage.py             # Stage models
│   │   └── diff.py              # Diff models
│   ├── db/                      # Database layer
│   │   ├── supabase.py          # Supabase client
│   │   └── repositories/        # Data access layer
│   └── main.py                  # FastAPI app entry point
├── tests/
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── contract/                # Contract tests
├── pyproject.toml               # Python dependencies
└── pytest.ini                   # Pytest configuration

specs/002-orchestration-decision/
├── contracts/
│   ├── orchestration-api.yaml   # OpenAPI spec
│   └── n8n-workflows/           # n8n workflow exports
├── data-model.md                # Database schema
├── research.md                  # Technical research
└── plan.md                      # Implementation plan
```

## Common Tasks

### Add New Pipeline Stage

1. Define stage in `src/services/stage_service.py`
2. Add stage execution logic
3. Update n8n workflow to include new stage
4. Add tests in `tests/unit/stages/test_{stage_name}.py`

### Modify Update Routing Logic

1. Update `src/services/update_service.py`
2. Modify routing rules in `determine_update_strategy()`
3. Update tests in `tests/unit/test_update_service.py`

### Adjust Diff Risk Scoring

1. Update `src/services/diff_service.py`
2. Modify `calculate_risk_score()` function
3. Add test cases in `tests/unit/test_diff_service.py`

## Troubleshooting

### Pipeline Not Starting

- Check Supabase connection: `curl http://localhost:54321/rest/v1/`
- Check orchestration service logs: `docker logs <container-id>`
- Verify n8n webhook configuration

### Stage Execution Failing

- Check stage logs in `stage_executions` table
- Verify input data format matches contract
- Check Vercel AI Gateway credentials if AI stage failing

### Diffs Not Generating

- Verify update event created in `update_events` table
- Check diff service logs
- Ensure original and updated data exist in `information_sheets`

## Next Steps

1. **Implement Pipeline Stages**: Follow `/speckit.tasks` to implement individual pipeline stages
2. **Build Diff Review UI**: Create Streamlit interface for editorial team
3. **Configure Monitoring**: Set up structured logging and metrics
4. **Deploy to Production**: Configure production Supabase and n8n instances

## Resources

- **API Documentation**: http://localhost:8000/docs
- **n8n Documentation**: https://docs.n8n.io
- **Supabase Documentation**: https://supabase.com/docs
- **Feature Spec**: `specs/002-orchestration-decision/spec.md`
- **Data Model**: `specs/002-orchestration-decision/data-model.md`
- **Research**: `specs/002-orchestration-decision/research.md`
