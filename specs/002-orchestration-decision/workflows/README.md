# Nexus n8n Workflows

This directory contains n8n workflow definitions for the Nexus pipeline orchestration system.

## Overview

n8n handles workflow orchestration, stage sequencing, retry logic, error handling, and state management for the Nexus pipeline. Each workflow corresponds to a major pipeline function.

## Architecture

**n8n handles**:
- Workflow orchestration and stage sequencing
- Retry logic with exponential backoff
- Error handling and failure routing
- Manual review triggers
- Supabase state updates
- Monitoring and alerting

**FastAPI services handle**:
- Complex data transformations
- AI integrations (enrichment, langage clair, translation)
- Diff generation and risk scoring
- Business logic and validation rules

## Workflows

### 1. pipeline-orchestration.json

**Purpose**: Main pipeline orchestration workflow

**Stages**:
1. Ingestion - Fetch data from Data Inclusion API
2. Editorial Policy Validation - Reject non-compliant programs
3. Reconciliation - Merge with Carif-Oref data
4. Enrichment - Fill gaps via web scraping
5. Langage Clair - AI-assisted plain language transformation
6. Translation - Multilingual translation (8 languages)
7. Validation - Quality checks and editorial compliance
8. Publication - Push to Réfugiés.info API

**Flow**:
```
Start
  ↓
[Ingestion] → [Policy Validation] → [Reconciliation] → [Enrichment]
  ↓              ↓                    ↓                  ↓
  ✓              ✗ (Reject)           ✓                 ✓
                                      ↓
                              [Langage Clair] → [Translation] → [Validation] → [Publication]
                                  ↓                  ↓              ↓              ↓
                                  ✓                  ✓              ✓              ✓
                                                                    ↓
                                                            [Manual Review] (if failed)
```

**Error Handling**:
- Transient errors: Retry with exponential backoff (1s → 5min, max 10 retries)
- Policy validation failures: Route to manual review queue
- Stage failures: Log error, route to manual review, alert operators
- External API failures: Retry up to 24 hours

**State Management**:
- Update `workflow_runs.current_stage` after each stage completes
- Update `stage_executions` with input/output data and metadata
- Update `information_sheets` with stage-specific data

### 2. update-detection.json

**Purpose**: Detect and route data updates

**Flow**:
```
Scheduled trigger (hourly)
  ↓
Fetch latest programs from Data Inclusion
  ↓
Compare checksums with stored versions
  ↓
For each update:
  - Determine original_stage
  - Route: full_reprocess (early stages) or smart_catchup (late stages)
  - Create update_event in Supabase
```

**Output**:
- `update_events` table populated with detected updates
- Updates routed to appropriate handler (full_reprocess or smart_catchup)

### 3. smart-catchup.json

**Purpose**: Process updates through pipeline stages to match original stage

**Flow**:
```
For each update_event with strategy = smart_catchup:
  ↓
Fetch original program data
  ↓
Process through stages: ingestion → ... → original_stage
  ↓
Generate diff (original vs updated)
  ↓
Create update_diff in Supabase
  ↓
Route to diff review queue (risk-based sampling)
```

**Performance**:
- Target: <5 minutes to process update through pipeline
- Uses FastAPI services for stage processing
- Parallel processing for multiple updates

### 4. diff-generation.json

**Purpose**: Generate diffs and route to review queue

**Flow**:
```
For each update_diff with review_status = pending:
  ↓
Calculate risk_score (weighted formula)
  ↓
Assign priority (low/medium/high based on risk_score)
  ↓
Route based on priority:
  - Low (<0.5): Auto-approve
  - Medium (0.5-0.8): Sample 20% for review
  - High (>0.8): Always review
  ↓
Update update_diffs table
  ↓
Notify editorial team (if review required)
```

## Integration with FastAPI

### HTTP Request Nodes

n8n workflows call FastAPI endpoints via HTTP Request nodes:

```javascript
// Example: Call enrichment service
POST /api/services/enrichment
{
  "program_id": "...",
  "data": {...},
  "mode": "normal"  // or "fast"
}

// Response
{
  "program_id": "...",
  "enriched_data": {...},
  "confidence": 0.85,
  "processing_time_ms": 1234
}
```

### Correlation ID Propagation

All HTTP requests include correlation ID for tracing:

```
X-Correlation-ID: 550e8400-e29b-41d4-a716-446655440000
```

This enables linking n8n execution logs with Python service logs.

### Error Handling

FastAPI services return standardized error responses:

```json
{
  "error_code": "VALIDATION_FAILED",
  "message": "Program failed policy validation",
  "details": {
    "program_id": "...",
    "reason": "For-profit with direct payment"
  },
  "correlation_id": "..."
}
```

n8n workflows handle these errors with retry logic or manual review routing.

## Deployment

### Local Development

1. Start n8n: `docker-compose up n8n`
2. Access n8n Studio: http://localhost:5678
3. Import workflows from this directory
4. Configure FastAPI service URL in n8n settings

### Production

1. Export workflows as JSON
2. Version control workflows in Git
3. Deploy via n8n CLI or Docker
4. Configure environment variables for API endpoints
5. Set up monitoring and alerting

## Monitoring

### n8n Execution Logs

- View execution history in n8n Studio
- Export logs for analysis
- Set up alerts for failed executions

### Metrics

- Workflow execution time
- Success/failure rates per stage
- Update processing latency
- Diff review queue size

### Dashboards

- n8n built-in execution dashboard
- Grafana dashboards (optional)
- Streamlit monitoring dashboard (Phase 4)

## Troubleshooting

### Common Issues

1. **Workflow fails to connect to FastAPI**
   - Verify FastAPI service is running
   - Check network connectivity
   - Verify API endpoint URLs in n8n settings

2. **Supabase connection errors**
   - Verify Supabase credentials in n8n environment
   - Check database migrations have been applied
   - Verify network access to Supabase

3. **Timeout errors**
   - Increase timeout in n8n HTTP Request node
   - Check FastAPI service performance
   - Verify external API availability (Data Inclusion, Carif-Oref)

### Debugging

1. Enable debug logging in n8n
2. Check execution logs for error details
3. Verify input/output data at each node
4. Test individual nodes with sample data

## References

- [n8n Documentation](https://docs.n8n.io/)
- [FastAPI Integration](../research.md#1-n8n-integration-architecture)
- [Data Model](../data-model.md)
- [API Contracts](../contracts/)
