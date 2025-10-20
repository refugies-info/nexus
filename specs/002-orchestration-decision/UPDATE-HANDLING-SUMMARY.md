# Update Handling Strategy - Executive Summary

**Date**: 2025-10-20
**Context**: ~100 raw data updates per week, human-in-the-loop at multiple stages
**Full Analysis**: See `orchestration-analysis.md` for complete details

---

## The Problem

When raw data is updated from Data Inclusion/Carif Oref:
- Original record may be at **any pipeline stage** (enrichment, langage_clair, translation, validation)
- **Human work exists** at later stages (manual enrichment, editorial review, quality checks)
- **Naive reprocessing discards human work** → wasted effort, unsustainable

---

## The Solution: Smart Catch-Up with AI

### Core Idea
**Use AI to "catch up" the updated record to the same stage as the original, then show humans only the diff.**

### Two-Track Strategy

#### Track 1: Early Stage Updates (Auto-Only Stages)
**Stages**: Ingestion, Reconciliation
**Strategy**: Full reprocessing (no human work to preserve)

```
Update detected → Mark original as superseded →
Full pipeline reprocessing
```

#### Track 2: Late Stage Updates (Human-in-Loop Stages)
**Stages**: Enrichment, Langage Clair, Translation, Validation
**Strategy**: Smart catch-up + diff review

```
Update detected →
AI processes update to match original stage (fast, no human review) →
Generate diff (original vs updated) →
Human reviews diff (approve/reject/edit) →
Merge and continue pipeline
```

---

## Key Benefits

✅ **Preserves human work** - No discarding of manual enrichment or editorial review
✅ **Efficient** - AI catch-up is fast (2-5 min vs full human review)
✅ **Scalable** - Risk-based sampling reduces human review burden
✅ **Quality-focused** - Humans review only changes, not entire record
✅ **Manageable** - 100 updates/week = ~1 hour human review with 20% sampling

---

## Risk-Based Sampling

**Problem**: 100 updates/week may be too many for full human review
**Solution**: Automatically approve low-risk changes, sample medium-risk, always review high-risk

### Risk Factors
- **Major edits** to content (vs minor typos)
- **Critical fields** changed (title, description, eligibility)
- **Deletions** (higher risk than additions)

### Sampling Rules
- **High risk (>0.8)**: Always review (100%)
- **Medium risk (0.5-0.8)**: Sample 20%
- **Low risk (<0.5)**: Auto-approve (0%)

### Expected Workload
- **Automated processing**: 100 updates × 5 min = ~8 hours/week (AI)
- **Human review**: 20 diffs × 3 min = ~1 hour/week (with 20% sampling)

---

## Architecture Components

### 1. Update Detection (Ingestion Stage)
- Checksum-based change detection
- Compare new data with existing record
- Route to appropriate strategy

### 2. Update Router
- Determine strategy based on original record's current stage
- Routes: `full_reprocess`, `smart_catchup`, or `new_version`

### 3. Smart Catch-Up Orchestrator
- Process update through pipeline stages until reaching original's stage
- Use AI to accelerate human-in-the-loop stages (fast mode, lower quality threshold)
- No manual intervention during catch-up

### 4. Diff Generator
- Compare original (with human work) vs updated (AI catch-up)
- Classify changes: addition, deletion, minor_edit, major_edit
- Calculate risk score
- Generate human-readable summary

### 5. Diff Review UI (Streamlit)
- Queue of pending diffs, sorted by priority
- Side-by-side comparison (original vs updated)
- Approval controls: Accept All, Reject All, Manual Review
- Risk-based filtering

---

## Supabase Schema Extensions

### New Tables

**`update_events`**: Track update detection and processing
- Links to original program
- Stores checksums (original vs updated)
- Records update strategy chosen
- Tracks processing status

**`update_diffs`**: Queue of diffs awaiting human review
- Links to update event
- Stores original and updated data
- Contains structured changes array
- Includes risk score and priority
- Tracks review status and reviewer

---

## Implementation Phases

### Phase 1 (MVP - Weeks 9-11)
- ✅ Update detection via checksum
- ✅ Update router (full reprocess vs smart catch-up)
- ✅ Basic diff generation
- ✅ Manual review for all diffs (validate approach)

### Phase 2 (Optimization - Weeks 12-15)
- ✅ AI-accelerated catch-up pipeline
- ✅ Risk-based sampling
- ✅ Streamlit diff review UI
- ✅ Automate low-risk approvals

### Phase 3 (Scale - Months 4-6)
- ✅ ML-based risk scoring (learn from human decisions)
- ✅ Batch diff review (review similar changes together)
- ✅ Automated regression testing

---

## Alternatives Considered & Rejected

### ❌ Always Full Reprocess
- Discards human work → unsustainable
- Wastes editorial effort

### ❌ Manual Merge for All Updates
- 100 manual merges/week → unsustainable
- Blocks pipeline

### ❌ Ignore Updates
- Stale data published → violates data quality principles
- Unacceptable

### ✅ Smart Catch-Up + Sampling (RECOMMENDED)
- Preserves human work
- Scalable with AI acceleration
- Balances quality and efficiency

---

## Code Examples

### Update Detection
```python
# In IngestionStage
checksum = compute_checksum(raw_data)
existing = db.get_existing_record(program_id)

if existing and existing.checksum != checksum:
    # Update detected!
    return handle_update(program_id, raw_data, existing)
```

### Update Routing
```python
# UpdateRouter
if original_stage in ["ingestion", "reconciliation"]:
    return "full_reprocess"  # No human work to preserve
elif original_stage in ["enrichment", "langage_clair", "translation", "validation"]:
    return "smart_catchup"  # Preserve human work
```

### Smart Catch-Up
```python
# SmartCatchUpOrchestrator
for stage in stages_until_target:
    if stage.has_human_intervention:
        # AI-accelerated (fast, lower quality)
        result = await ai_process_stage(stage, mode="fast")
    else:
        # Normal automated processing
        result = await stage.execute(program_id)
```

### Diff Generation
```python
# DiffGenerator
changes = []
for field in original.keys():
    if original[field] != updated[field]:
        changes.append({
            "field": field,
            "original": original[field],
            "updated": updated[field],
            "type": classify_change(original[field], updated[field])
        })

risk_score = calculate_risk(changes)
```

### Risk-Based Sampling
```python
# UpdateSampler
if risk_score > 0.8:
    return True  # Always review high-risk
elif risk_score > 0.5:
    return random() < 0.2  # Sample 20% of medium-risk
else:
    return False  # Auto-approve low-risk
```

---

## Performance Metrics to Track

### Update Processing
- Updates detected per week
- Update strategy distribution (full_reprocess vs smart_catchup)
- Catch-up processing time (AI-accelerated)
- Diff generation time

### Human Review
- Diffs pending review (queue size)
- Diffs reviewed per week
- Review time per diff
- Approval rate (accept vs reject vs manual)
- Risk score distribution

### Quality
- False positive rate (auto-approved but should have been reviewed)
- False negative rate (reviewed but was low-risk)
- Human override rate (manual edits to AI suggestions)

---

## Success Criteria

✅ **Efficiency**: <1 hour/week human review time (with sampling)
✅ **Quality**: <5% false positive rate on auto-approvals
✅ **Preservation**: 100% of human work preserved (no discarding)
✅ **Timeliness**: Updates processed within 24 hours
✅ **Scalability**: System handles 200 updates/week without degradation

---

## Next Steps

1. **Implement update detection** in ingestion stage (checksum-based)
2. **Build update router** (routing logic based on stage)
3. **Create smart catch-up orchestrator** (AI-accelerated pipeline)
4. **Implement diff generator** (compare original vs updated)
5. **Build Streamlit diff review UI** (human approval interface)
6. **Add risk-based sampling** (prioritize high-risk changes)
7. **Test with real data** (validate approach with Carif Oref updates)
8. **Iterate based on feedback** (adjust risk thresholds, sampling rates)

---

**Full Technical Details**: See `orchestration-analysis.md` for complete architecture, code examples, and schema design.
