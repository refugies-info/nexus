# Database Rollback Strategy

**Date**: 2025-10-21
**Context**: Nexus orchestration service with Supabase PostgreSQL backend
**Approach**: Point-in-Time Recovery (PITR) + Simple Forward-Only Migrations

---

## Overview

We use a **hybrid strategy** combining:
1. **Simple forward-only migrations** (Supabase CLI native)
2. **Point-in-Time Recovery (PITR)** for rollback capability
3. **Daily backups** as additional safety net

This approach balances simplicity with safety, leveraging Supabase's built-in capabilities.

---

## Migration Strategy: Forward-Only

### Principle
- All migrations are **immutable** and **forward-only**
- Never write rollback migrations
- If a mistake is made, write a new migration to fix it

### Implementation
```bash
# Create new migration
supabase migration new add_approval_type_column

# This creates: supabase/migrations/20251021090000_add_approval_type_column.sql
# Edit the file with your DDL changes

# Deploy to production
supabase db push
```

### Example Workflow
```sql
-- supabase/migrations/001_init_schema.sql
CREATE TABLE workflow_runs (
  id UUID PRIMARY KEY,
  program_id TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- supabase/migrations/002_add_update_events.sql
CREATE TABLE update_events (
  id UUID PRIMARY KEY,
  program_id TEXT NOT NULL,
  original_checksum TEXT NOT NULL,
  updated_checksum TEXT NOT NULL
);

-- supabase/migrations/003_fix_update_events_constraint.sql
-- If we made a mistake in 002, we fix it here (don't rollback 002)
ALTER TABLE update_events ADD CONSTRAINT unique_program_update
  UNIQUE(program_id, original_checksum);
```

### Advantages
- ✅ Simple, clear audit trail
- ✅ No complex rollback logic
- ✅ Matches Supabase's native approach
- ✅ Easier to debug and understand
- ✅ Proven in production (PostgreSQL community standard)

---

## Rollback Strategy: Point-in-Time Recovery

### What is PITR?
Point-in-Time Recovery allows restoring the database to **any moment in time** (up to seconds granularity) within the retention period.

**How it works**:
- Supabase takes weekly physical backups
- Write-Ahead Log (WAL) files record every database change
- Combined: can restore to any point in time

### Configuration

**For Production** (Recommended):
```yaml
PITR Retention: 7 days
Cost: ~$0.50-1.00 per day (varies by region)
Granularity: Seconds
Recovery Time: 5-30 minutes depending on WAL volume
```

**For Development/Staging**:
```yaml
PITR Retention: 1-3 days (or use free daily backups)
Cost: Minimal
```

### When to Use PITR

**Scenario 1: Migration Corrupted Data**
```
Timeline:
- 10:00 AM: Deploy migration that accidentally deletes data
- 10:05 AM: Discover the issue
- 10:10 AM: Restore to 10:02 AM (before migration)
- 10:30 AM: Investigate, fix migration, redeploy
```

**Scenario 2: Application Bug Corrupted Database**
```
Timeline:
- 2:00 PM: Deploy buggy code that corrupts records
- 2:15 PM: Alerts fire, data corruption detected
- 2:20 PM: Restore to 1:55 PM (before corruption)
- 3:00 PM: Fix code, redeploy
```

### Restore Procedure

**Via Supabase Dashboard**:
1. Go to Project Settings → Backups
2. Click "Restore" under Point-in-Time Recovery
3. Select the timestamp to restore to
4. Confirm (this creates a new project)
5. Test the restored data
6. Update DNS/connection strings to point to restored project
7. Delete old project

**Via Supabase CLI**:
```bash
# List available restore points
supabase projects list

# Restore to specific timestamp
supabase projects restore --project-id <project-id> --backup-id <backup-id>
```

### Recovery Time Objective (RTO) & Recovery Point Objective (RPO)

| Metric | Value | Notes |
|--------|-------|-------|
| **RTO** | 5-30 min | Time to restore and switch traffic |
| **RPO** | Seconds | Maximum data loss (up to restore point) |
| **Retention** | 7 days | Can restore to any point in last 7 days |

---

## Backup Strategy: Daily Backups

### Free Daily Backups (Included)
- **Frequency**: Once per day (automatic)
- **Retention**: 7 days
- **Granularity**: Daily (not point-in-time)
- **Cost**: Free

### When PITR is Disabled
If PITR is not enabled, daily backups are automatic. Use these for:
- Long-term archival
- Compliance/audit trail
- Disaster recovery (full data center failure)

### Manual Backups (Optional)
```bash
# Export full backup
supabase db dump -f backup_$(date +%F_%H%M%S).sql

# Store in Git (for schema) or S3 (for data)
git add supabase/backups/backup_2025-10-21_090000.sql
```

---

## Disaster Recovery Scenarios

### Scenario 1: Migration Bug (Most Common)
```
Problem: Migration script has syntax error or logic bug
Detection: Immediate (deployment fails or data corrupted)
Recovery: PITR to pre-migration timestamp
Time: 5-10 minutes
Data Loss: None (restore to exact moment)
```

### Scenario 2: Data Corruption
```
Problem: Application bug corrupts records
Detection: Monitoring alerts (data quality checks)
Recovery: PITR to pre-corruption timestamp
Time: 10-20 minutes
Data Loss: None (restore to exact moment)
```

### Scenario 3: Accidental Data Deletion
```
Problem: DELETE query without WHERE clause
Detection: Monitoring alerts
Recovery: PITR to pre-deletion timestamp
Time: 5-10 minutes
Data Loss: None (restore to exact moment)
```

### Scenario 4: Full Data Center Failure
```
Problem: Supabase region goes down
Detection: Connection failures
Recovery: Restore from daily backup to alternate region
Time: 30-60 minutes
Data Loss: Up to 24 hours (since last daily backup)
```

---

## Implementation Checklist

- [ ] Enable PITR for production project (7-day retention)
- [ ] Document PITR costs in project budget
- [ ] Set up monitoring alerts for backup failures
- [ ] Test restore procedure monthly
- [ ] Document restore runbook for on-call team
- [ ] Train team on forward-only migration pattern
- [ ] Add pre-migration backup step to CI/CD pipeline
- [ ] Document rollback decision criteria (when to use PITR vs fix-forward)

---

## Decision Criteria: When to Rollback vs Fix Forward

### Use PITR (Rollback) When:
- ✅ Data corruption is widespread
- ✅ Migration introduced critical bugs
- ✅ Need to preserve exact state at specific moment
- ✅ Time-sensitive issue (faster than fix-forward)

### Use Fix-Forward When:
- ✅ Bug is isolated to specific records
- ✅ Can write targeted fix migration
- ✅ Prefer to maintain linear history
- ✅ Non-critical data affected

### Example Decision Tree
```
Is data corrupted?
├─ YES: Is corruption widespread (>10% of records)?
│  ├─ YES: Use PITR (faster recovery)
│  └─ NO: Use fix-forward (targeted fix)
└─ NO: Is migration syntax error?
   ├─ YES: Use PITR (simpler)
   └─ NO: Use fix-forward (maintain history)
```

---

## Cost Analysis

### Scenario: Production with 7-day PITR
```
PITR Cost: ~$0.50-1.00 per day
Monthly Cost: ~$15-30
Annual Cost: ~$180-360

Value:
- Seconds-granularity recovery
- Covers 99% of disaster scenarios
- Peace of mind for data integrity
```

### Recommendation
**Enable PITR for production, disable for dev/staging** to minimize costs while maintaining safety.

---

## References

- [Supabase Database Backups](https://supabase.com/docs/guides/platform/backups)
- [Supabase PITR Configuration](https://supabase.com/docs/guides/platform/manage-your-usage/point-in-time-recovery)
- [Supabase CLI Migrations](https://supabase.com/docs/guides/cli/local-development#database-migrations)
- [PostgreSQL WAL (Write-Ahead Logging)](https://www.postgresql.org/docs/current/wal-intro.html)
