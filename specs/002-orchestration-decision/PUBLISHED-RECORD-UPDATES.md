# Published Record Updates: Edge Case Handling

**Date**: 2025-10-21
**Context**: Handling updates detected for records already at publication stage
**Decision**: Option 2 - Smart Catch-Up with Republication

---

## Problem Statement

When an update is detected from Data Inclusion/Carif Oref for a record that has already been published to Réfugiés.info:

- **Current stage**: `publication` (already published)
- **Update detected**: Checksum mismatch indicates source data changed
- **Question**: Should we update the published record?

### Why This Matters
- Published records are visible to end users
- Updates may contain important corrections (eligibility, contact info, etc.)
- Ignoring updates = stale data
- But unreviewed updates = quality risk

---

## Solution: Smart Catch-Up with Republication

### Routing Decision
```
If update detected AND original_stage = 'publication':
  → Route to smart_catchup (same as late-stage updates)
  → Process through all pipeline stages to publication
  → Generate diff (published version vs updated version)
  → Human reviews diff (high-risk by default, always reviewed)
  → If approved: republish to Réfugiés.info
  → If rejected: keep published version unchanged
```

### Implementation Flow

```
Update Detected (publication stage)
  ↓
Smart Catch-Up Orchestrator
  ├─ Ingestion: Parse updated raw data
  ├─ Reconciliation: Normalize and validate
  ├─ Enrichment: Apply enrichment transformations
  ├─ Langage Clair: Simplify language (reuse existing logic)
  ├─ Translation: Translate to other languages (reuse existing logic)
  ├─ Validation: Quality checks (reuse existing logic)
  └─ Publication: Prepare for republication
  ↓
Diff Generator
  ├─ Compare: published_data vs updated_data
  ├─ Classify: additions, deletions, minor_edits, major_edits
  ├─ Risk Score: Calculate (high-risk by default)
  └─ Output: Structured diff
  ↓
Diff Review UI (Streamlit)
  ├─ Always reviewed (no auto-approval for published records)
  ├─ Editorial team decides: approve or reject
  ├─ If approved: trigger republication workflow
  └─ If rejected: keep published version
  ↓
Republication (if approved)
  ├─ Update information_sheets with new data
  ├─ Trigger Réfugiés.info API update
  ├─ Update publication timestamp
  └─ Log republication event
```

### Key Differences from Late-Stage Updates

| Aspect | Late-Stage (enrichment-validation) | Published (publication) |
|--------|-----------------------------------|------------------------|
| **Auto-approval** | Yes (low-risk) | No (always reviewed) |
| **Risk scoring** | Calculated | High-risk by default |
| **Republication** | N/A | Yes (if approved) |
| **User impact** | Internal only | Visible to end users |
| **Audit trail** | Diff review only | Diff review + republication log |

---

## Reusing Existing Pipeline Transformations

### Advantage: Consistency
By routing published updates through the full pipeline, we ensure:
- ✅ Same enrichment logic applied
- ✅ Same language simplification rules
- ✅ Same translation quality standards
- ✅ Same validation checks

### Implementation Strategy

**Phase 1 (MVP)**:
- Route published updates to smart_catchup
- Process through all stages
- Generate diff
- Manual review required (no auto-approval)

**Phase 2 (Optimization)**:
- Implement republication workflow in n8n
- Add Réfugiés.info API integration
- Track republication events

**Phase 3 (Enhancement)**:
- ML-based risk scoring for published updates
- Batch republication (update multiple records at once)
- Rollback capability (revert to previous published version)

---

## Data Model Updates

### update_events Table
Add field to track published record updates:
```sql
ALTER TABLE update_events ADD COLUMN is_published_update BOOLEAN DEFAULT FALSE;
```

### update_diffs Table
Add field to track republication:
```sql
ALTER TABLE update_diffs ADD COLUMN republished_at TIMESTAMPTZ NULLABLE;
ALTER TABLE update_diffs ADD COLUMN republication_status TEXT DEFAULT 'pending';
  -- Values: pending, republished, failed
```

### information_sheets Table
Add field to track publication history:
```sql
ALTER TABLE information_sheets ADD COLUMN published_at TIMESTAMPTZ NULLABLE;
ALTER TABLE information_sheets ADD COLUMN republished_at TIMESTAMPTZ NULLABLE;
```

---

## Risk Assessment

### Risks of Accepting Published Updates
- ❌ Unreviewed changes visible to users
- ❌ Potential data quality issues
- ❌ User confusion if data changes frequently

### Mitigations
- ✅ Always require human review (no auto-approval)
- ✅ High-risk scoring by default
- ✅ Clear audit trail of all republications
- ✅ Rollback capability (Phase 3)

### Risks of Rejecting Published Updates
- ❌ Stale data published to users
- ❌ Missed corrections (eligibility, contact info)
- ❌ Data integrity issues
- ❌ User frustration

### Mitigations
- ✅ Smart catch-up ensures quality
- ✅ Human review catches issues
- ✅ Republication only if approved

---

## Example Scenarios

### Scenario 1: Contact Information Update
```
Published: Phone: 01 23 45 67 89
Updated:   Phone: 01 23 45 67 90 (corrected)

Flow:
1. Update detected
2. Smart catch-up processes update
3. Diff shows: phone number changed
4. Risk score: Medium (contact field, minor edit)
5. Editorial team reviews
6. Approves (it's a correction)
7. Republishes to Réfugiés.info
8. Users see updated phone number
```

### Scenario 2: Eligibility Criteria Change
```
Published: Eligible: Unemployed persons
Updated:   Eligible: Unemployed persons, Students

Flow:
1. Update detected
2. Smart catch-up processes update
3. Diff shows: eligibility expanded
4. Risk score: High (critical field, major edit)
5. Editorial team reviews carefully
6. Approves (legitimate expansion)
7. Republishes to Réfugiés.info
8. More users now see this service
```

### Scenario 3: Spam/Vandalism
```
Published: Description: Professional training program
Updated:   Description: SPAM SPAM SPAM

Flow:
1. Update detected
2. Smart catch-up processes update
3. Diff shows: description replaced with spam
4. Risk score: High (critical field, major edit)
5. Editorial team reviews
6. Rejects (clearly spam)
7. Keeps published version unchanged
8. Users continue to see original description
```

---

## Implementation Tasks

- **T100**: Add published_update fields to data model
- **T101**: Implement republication workflow in n8n
- **T102**: Add Réfugiés.info API integration
- **T103**: Update diff review UI for published records
- **T104**: Add republication audit trail
- **T105**: Test published record update scenarios

---

## References

- [UPDATE-HANDLING-SUMMARY](./UPDATE-HANDLING-SUMMARY.md)
- [Data Model](./data-model.md)
- [Diff Generation Algorithm](./research.md#4-diff-generation-algorithm)
