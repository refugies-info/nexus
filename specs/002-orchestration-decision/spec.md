# Feature Specification: Pipeline Orchestration & Update Handling

**Feature Branch**: `002-orchestration-decision`
**Created**: 2025-10-20
**Status**: Draft
**Input**: User description: "Implement lightweight Python orchestration for the Nexus AI pipeline with Supabase state management and smart update handling that preserves human-in-the-loop work through AI-accelerated catch-up and diff review."

## User Research *(mandatory for Nexus)*

**User Research Conducted**:
- **Not applicable** - This is an infrastructure feature that enables the pipeline to process data and deliver information sheets to end users
- Primary stakeholders are the Réfugiés.info editorial team who will use the diff review interface to manage content updates
- Editorial team requirements derived from Constitutional Principle IX (User-Centered Development) and Principle IV (Editorial Compliance)
- Future user research needed for diff review UI usability with editorial team

**AI Transparency Testing** (if applicable):
- **Not applicable** - This feature is infrastructure/orchestration, not user-facing content generation
- AI transparency requirements apply to downstream features (langage clair, translation) that generate user-facing content

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Process New Programs Through Pipeline (Priority: P1)

As the Nexus system, I need to process new French learning programs from Data Inclusion through all pipeline stages (ingestion → editorial policy validation → reconciliation → enrichment → langage clair → translation → validation → publication) so that accurate, multilingual information sheets are published to Réfugiés.info, with non-compliant programs rejected early and data reconciled with Carif-Oref.

**Why this priority**: Foundation for all pipeline functionality - without this, no information sheets can be generated. This is the core value proposition of Nexus. Editorial policy validation ensures compliance before processing begins; Carif-Oref reconciliation ensures data completeness.

**Independent Test**: Can be fully tested by submitting a new program and verifying it progresses through all 9 stages (including editorial policy validation and enhanced reconciliation), with state tracked at each stage, and delivers a published information sheet. Non-compliant programs should be rejected at validation stage with audit trail.

**Acceptance Scenarios**:

1. **Given** a new French learning program from Data Inclusion, **When** the pipeline processes it, **Then** the program progresses through all 9 stages sequentially and state is tracked in the database
2. **Given** a program that violates editorial policy (e.g., for-profit with direct payment), **When** the editorial policy validation stage processes it, **Then** the program is rejected with reason and audit trail, and does not proceed to reconciliation
3. **Given** a program with Carif-Oref source ID, **When** the reconciliation stage processes it, **Then** the system fetches matching Carif-Oref CSV data, scrapes additional details, and merges data
4. **Given** a program at the enrichment stage, **When** a stage fails with a transient error, **Then** the system retries the stage automatically without manual intervention
5. **Given** a program at the validation stage, **When** quality checks fail, **Then** the program is routed to the editorial review queue and does not proceed to publication
6. **Given** multiple programs being processed, **When** one program fails, **Then** other programs continue processing without interruption

---

### User Story 2 - Handle Data Updates Efficiently (Priority: P2)

As the Nexus system, I need to detect when source data is updated and process updates efficiently without discarding human work (manual enrichment, editorial review) so that information sheets stay current while preserving editorial effort.

**Why this priority**: ~100 updates per week require efficient handling. Without this, either information sheets become stale or editorial team wastes effort re-reviewing unchanged content.

**Independent Test**: Can be tested by submitting an update to an existing program at various stages and verifying the system routes it appropriately (full reprocess for early stages, smart catch-up for late stages).

**Acceptance Scenarios**:

1. **Given** a program at the ingestion stage, **When** source data is updated, **Then** the system detects the change via checksum and reprocesses the program from the beginning
2. **Given** a program at the langage clair stage (with human editorial work), **When** source data is updated, **Then** the system processes the update to the same stage and generates a diff for editorial review
3. **Given** an update with minor changes (typos, formatting), **When** the diff is generated, **Then** the system auto-approves the update without requiring human review
4. **Given** an update with major changes (content deletions, critical field changes), **When** the diff is generated, **Then** the system flags it for mandatory human review

---

### User Story 3 - Review and Approve Update Diffs (Priority: P3)

As a Réfugiés.info editor, I need to review diffs between original and updated information sheets so that I can approve changes without re-reviewing the entire content.

**Why this priority**: Enables editorial team to manage updates efficiently. Builds on P2 by adding human oversight for high-risk changes.

**Independent Test**: Can be tested by generating update diffs and verifying editors can view, approve, reject, or manually edit changes through the review interface.

**Acceptance Scenarios**:

1. **Given** pending update diffs in the review queue, **When** an editor opens the review interface, **Then** they see diffs sorted by priority (high-risk first)
2. **Given** a diff showing side-by-side comparison, **When** the editor reviews the changes, **Then** they can see original vs updated content with changes highlighted
3. **Given** a low-risk diff, **When** the editor approves all changes, **Then** the updated content merges and the program continues through the pipeline
4. **Given** a high-risk diff, **When** the editor rejects changes, **Then** the original content is preserved and the update is marked as rejected
5. **Given** a diff requiring manual edits, **When** the editor makes custom changes, **Then** the system records the manual edits and continues the pipeline with the edited content

---

### User Story 4 - Monitor Pipeline Execution (Priority: P4)

As a Nexus operator, I need to monitor pipeline execution status and identify failures so that I can ensure information sheets are being processed and published successfully.

**Why this priority**: Operational visibility is important but not blocking for MVP. Can initially rely on database queries and logs.

**Independent Test**: Can be tested by running the pipeline and verifying operators can view current status, identify failed programs, and access error details.

**Acceptance Scenarios**:

1. **Given** programs being processed, **When** an operator views the monitoring dashboard, **Then** they see current status of all programs (stage, success/failure, processing time)
2. **Given** a program that failed at a specific stage, **When** an operator views the failure details, **Then** they see the error message, input data, and stage metadata
3. **Given** pipeline performance metrics, **When** an operator views the dashboard, **Then** they see processing time per stage, throughput, and error rates
4. **Given** a failed program, **When** an operator triggers a manual retry, **Then** the program resumes from the failed stage

---

### Edge Cases

- **What happens when source data is deleted?** System marks the information sheet as archived and does not publish updates
- **What happens when a program is updated multiple times rapidly?** System processes updates sequentially, with later updates superseding earlier ones
- **What happens when the editorial team is unavailable to review diffs?** Diffs queue up in the review interface, sorted by priority; low-risk updates auto-approve after a configurable delay
- **What happens when a stage times out?** System retries with exponential backoff; after max retries, marks stage as failed and alerts operators
- **What happens when database connection is lost?** System queues operations in memory and retries; if connection not restored, fails gracefully with error logged
- **What happens when two editors review the same diff simultaneously?** System uses optimistic locking; first approval wins, second editor sees "already reviewed" message
- **What happens when a program is stuck in manual review queue for >7 days?** System sends notification to editorial team and marks as "review_overdue" but keeps in queue
- **What happens when editorial policy rules conflict?** System applies rules in priority order (defined by editorial team) and records which rule triggered rejection
- **What happens when a program matches multiple rejection criteria?** System records all matching criteria in audit trail and returns primary reason to user
- **What happens when Carif-Oref CSV is unavailable?** System retries with exponential backoff (up to 24 hours); if unavailable, proceeds with Data Inclusion data only and flags for manual reconciliation
- **What happens when Carif-Oref website URL scraping fails?** System records failure and proceeds with CSV data; flags for manual review if critical data is missing
- **What happens when Data Inclusion and Carif-Oref have conflicting data on policy-relevant fields?** System flags conflict for editorial review and does not auto-proceed

## Requirements *(mandatory)*

### Functional Requirements

#### Pipeline Orchestration
- **FR-001**: System MUST execute pipeline stages sequentially in order: ingestion → editorial policy validation → reconciliation → enrichment → langage clair → translation → validation → publication
- **FR-002**: System MUST track the current stage of each program being processed
- **FR-003**: System MUST persist program state after each stage completion to enable recovery from failures
- **FR-004**: System MUST retry failed stages automatically with exponential backoff (up to 24 hours for external API failures)
- **FR-005**: System MUST isolate stage failures so that one program's failure does not affect other programs
- **FR-006**: System MUST support partial replay (re-running specific stages without full pipeline restart)
- **FR-007**: System MUST route programs to manual review queues when quality checks fail
- **FR-008**: System MUST support concurrent processing of multiple programs
- **FR-009a**: System MUST queue programs when Data Inclusion or Carif Oref APIs are temporarily unavailable and retry until APIs recover

#### Editorial Policy Validation
- **FR-009b**: System MUST validate each ingested program against editorial policy rules immediately after ingestion, before proceeding to reconciliation
- **FR-009c**: System MUST reject programs that violate policy rules with specific rejection reason and audit trail
- **FR-009d**: System MUST support 15+ distinct editorial policy categories as defined in Réfugiés.info policy document (for-profit initiatives, temporary programs, out-of-scope publics, specialized structures, etc.)
- **FR-009e**: System MUST support policy rule exceptions (e.g., subsidized for-profit initiatives, state-funded initiatives for specific nationalities in crisis contexts)
- **FR-009f**: System MUST flag programs with ambiguous policy status for manual editorial review rather than auto-rejecting
- **FR-009g**: System MUST maintain audit trail of all validation decisions including: program ID, policy rule applied, decision (pass/reject/review), timestamp, and editor (if manual review)
- **FR-009h**: System MUST allow editorial team to update policy rules without code deployment
- **FR-009i**: System MUST version policy rules and track which rule version was applied to each program

#### Enhanced Data Reconciliation with Carif-Oref
- **FR-009j**: System MUST fetch Carif-Oref CSV export from https://www.intercariforef.org/dian/?...&excsv=1 on a configurable schedule (daily recommended)
- **FR-009k**: System MUST reconcile Data Inclusion records with Carif-Oref CSV data using structure_id and id fields as matching keys
- **FR-009l**: System MUST construct Carif-Oref website URLs from Data Inclusion structure_id and id fields following format: https://www.intercariforef.org/dian/[dept]_[structure_id]/[dept]_[service_id]/[...]/[encoded_name]
- **FR-009m**: System MUST scrape additional program details from Carif-Oref website URLs (e.g., detailed descriptions, contact information, schedule)
- **FR-009n**: System MUST merge Data Inclusion and Carif-Oref data, with Carif-Oref data taking precedence for overlapping fields
- **FR-009o**: System MUST handle programs with Data Inclusion source only (no Carif-Oref match) by proceeding with Data Inclusion data and recording reconciliation status
- **FR-009p**: System MUST detect conflicts between Data Inclusion and Carif-Oref data (e.g., different program names, different costs) and flag for editorial review
- **FR-009q**: System MUST retry Carif-Oref CSV fetch and website scraping with exponential backoff (up to 24 hours) on transient failures
- **FR-009r**: System MUST record reconciliation status for each program: fully_reconciled, partially_reconciled (missing Carif-Oref data), data_conflict, or reconciliation_failed

#### Update Detection
- **FR-009**: System MUST detect when source data has been updated by comparing checksums
- **FR-010**: System MUST distinguish between new programs, updated programs, and unchanged programs
- **FR-011**: System MUST route updates based on the original program's current stage (full reprocess vs smart catch-up)
- **FR-012**: System MUST preserve original program data when processing updates

#### Smart Catch-Up
- **FR-013**: System MUST process updates through pipeline stages until reaching the original program's current stage
- **FR-014**: System MUST generate diffs comparing original program data (with human work) vs updated program data
- **FR-015**: System MUST classify changes by type (addition, deletion, minor edit, major edit)
- **FR-016**: System MUST calculate risk scores for updates based on change characteristics
- **FR-017**: System MUST auto-approve low-risk updates without human review
- **FR-018**: System MUST flag high-risk updates for mandatory human review
- **FR-019**: System MUST sample medium-risk updates for human review based on configurable sampling rate

#### Diff Review Interface
- **FR-020**: System MUST provide a review interface for editorial team to view pending update diffs
- **FR-021**: System MUST display diffs sorted by priority (high-risk first)
- **FR-022**: System MUST show side-by-side comparison of original vs updated content with changes highlighted
- **FR-023**: System MUST allow editors to approve all changes, reject all changes, or manually edit changes
- **FR-024**: System MUST record which editor reviewed each diff and when
- **FR-025**: System MUST prevent concurrent editing of the same diff by multiple editors
- **FR-026**: System MUST authenticate editorial team users via Supabase Auth with email/password
- **FR-027**: System MUST implement role-based access control (RBAC) to restrict diff review interface access to authorized editors

#### State Management
- **FR-028**: System MUST store workflow execution state (program ID, current stage, status, timestamps)
- **FR-029**: System MUST store stage execution details (input data, output data, retry count, errors)
- **FR-030**: System MUST store data source state (source ID, last fetched timestamp, checksum)
- **FR-031**: System MUST store information sheet state with progressive enhancement (data added at each stage)
- **FR-032**: System MUST store update events (original checksum, updated checksum, update strategy)
- **FR-033**: System MUST store update diffs (original data, updated data, changes, risk score, review status)

### Constitution-Aligned Requirements

#### Principle II: Pipeline Modularity
- **CAR-001**: Each pipeline stage MUST be independently executable and testable
- **CAR-002**: Stages MUST communicate via well-defined contracts (input/output schemas)
- **CAR-003**: Stage failures MUST be contained and not cascade to other stages
- **CAR-004**: System MUST support partial execution and replay from any stage

#### Principle VI: Observability & Traceability
- **CAR-005**: System MUST log every data transformation with input, output, and transformation metadata
- **CAR-006**: System MUST emit structured logs in machine-readable format for monitoring
- **CAR-007**: System MUST track data lineage from source (Data Inclusion/Carif Oref) to publication (Réfugiés.info)
- **CAR-008**: System MUST collect performance metrics per pipeline stage (processing time, throughput, error rates)
- **CAR-009**: System MUST alert operators on pipeline failures, data quality issues, and SLA violations (including programs stuck in manual review >7 days)

#### Principle VII: Incremental Delivery
- **CAR-010**: Pipeline orchestration MUST be deliverable and demonstrable independently of stage implementations
- **CAR-011**: Update handling MUST be deliverable incrementally (Phase 1: detection, Phase 2: smart catch-up, Phase 3: risk-based sampling)
- **CAR-012**: Each user story (P1, P2, P3, P4) MUST be independently testable and deployable

#### Principle IX: User-Centered Development
- **CAR-013**: Diff review interface MUST be validated with Réfugiés.info editorial team through usability testing
- **CAR-014**: Risk scoring thresholds MUST be iteratively adjusted based on editorial team feedback
- **CAR-015**: System MUST track metrics on diff review efficiency (time per review, approval rates) to optimize workflow

#### TDD Compliance (NON-NEGOTIABLE)
- **CAR-016**: All orchestration logic MUST be developed using test-driven development (tests written first)
- **CAR-017**: Each pipeline stage MUST have unit tests validating isolated behavior
- **CAR-018**: System MUST have integration tests validating end-to-end pipeline execution
- **CAR-019**: Update handling MUST have contract tests ensuring diff generation accuracy

### Key Entities

- **Workflow Run**: Represents a single execution of the pipeline for a program. Tracks program ID (Data Inclusion unique ID), current stage, status (pending/running/completed/failed), timestamps, and error messages.
- **Stage Execution**: Represents execution of a single pipeline stage. Tracks stage name, status, retry count, input/output data, and execution metadata.
- **Data Source State**: Represents the state of external data sources (Data Inclusion, Carif Oref). Tracks source ID, last fetched timestamp, checksum for change detection, and raw data.
- **Information Sheet**: Represents a program's information sheet with progressive enhancement. Tracks program ID (Data Inclusion unique ID as primary key), current stage, status (draft/in_review/approved/published), and data added at each stage (ingested, validated_policy, reconciled, enriched, langage_clair, translated, validated, published).
- **Update Event**: Represents detection of a source data update. Tracks program ID (Data Inclusion unique ID), original checksum, updated checksum, original stage, update strategy (full_reprocess/smart_catchup), and processing status.
- **Update Diff**: Represents a diff awaiting editorial review. Tracks program ID (Data Inclusion unique ID), stage, original data, updated data, structured changes, risk score, priority, review status, and reviewer information.
- **Editorial Policy Rule**: Represents a single editorial policy validation rule. Tracks rule ID, category (for-profit, temporary, out-of-scope, etc.), criteria (conditions to match), decision (accept/reject/review), exceptions, version, created/updated timestamps, and created_by editor.
- **Policy Validation Decision**: Represents the result of validating a program against editorial policy. Tracks program ID, rule applied, decision (pass/reject/review), reason, audit trail (timestamp, editor if manual), and version of policy rules used.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: System successfully processes a new program through all 9 pipeline stages (including editorial policy validation and enhanced reconciliation) and publishes an information sheet to Réfugiés.info within 24 hours
- **SC-002**: System handles 100 concurrent programs without degradation in processing time
- **SC-003**: Stage failures are automatically retried and 95% of transient errors recover without manual intervention
- **SC-004**: System detects 100% of source data updates via checksum comparison within 1 hour of update
- **SC-005**: Smart catch-up processes updates to match original stage in under 5 minutes per update
- **SC-006**: Risk-based sampling reduces editorial review workload to under 1 hour per week (from ~5 hours without sampling)
- **SC-007**: High-risk updates (>0.8 risk score) are flagged for review with 100% accuracy (no false negatives)
- **SC-008**: Low-risk updates (<0.5 risk score) are auto-approved with <5% false positive rate (requiring later manual correction)
- **SC-009**: Editorial team can review and approve a diff in under 3 minutes on average
- **SC-010**: System tracks complete data lineage from source to publication for 100% of programs
- **SC-011**: Operators can identify and diagnose pipeline failures within 5 minutes using monitoring dashboard
- **SC-012**: System maintains 99% uptime for pipeline processing (excluding planned maintenance)
- **SC-013**: Editorial policy validation rejects 100% of non-compliant programs (no false negatives) with <5% false positive rate (compliant programs incorrectly rejected)
- **SC-014**: Editorial policy validation decisions are recorded with complete audit trail for 100% of programs
- **SC-015**: Carif-Oref reconciliation successfully matches and merges data for 90%+ of programs with Carif-Oref source IDs
- **SC-016**: Carif-Oref CSV is fetched and updated daily with <1 hour latency from publication
- **SC-017**: Data conflicts between Data Inclusion and Carif-Oref are detected and flagged for 100% of conflicting records
- **SC-018**: Editorial team can update policy rules and have them applied to new programs within 5 minutes

## Assumptions

- Data Inclusion and Carif Oref APIs are available and return data in expected formats
- ~100 source data updates per week (based on historical patterns)
- Réfugiés.info editorial team has capacity to review ~20 diffs per week (with risk-based sampling)
- Pipeline stages (ingestion, editorial policy validation, reconciliation, enrichment, langage clair, translation, validation, publication) will be implemented as separate features following this orchestration infrastructure
- Editorial policy rules are maintained in an official document and updated regularly by Réfugiés.info editorial team
- Carif-Oref CSV export is available and updated regularly at https://www.intercariforef.org/dian/?...&excsv=1
- Carif-Oref website is accessible for scraping additional program details
- Managed database service (Supabase) is available and provides sufficient performance for state management
- Network connectivity is generally reliable; transient failures are handled via retry logic
- Editorial team has basic technical literacy to use web-based diff review interface

## Out of Scope

- Implementation of individual pipeline stages (ingestion, reconciliation, etc.) - these are separate features
- Complex DAG dependencies (pipeline is linear for MVP)
- Distributed execution across multiple workers (single-process execution sufficient for MVP scale)
- Real-time streaming (batch processing is sufficient)
- Advanced scheduling features (simple cron-like triggers sufficient)
- Machine learning-based risk scoring (Phase 3 enhancement, not MVP)
- Batch diff review (reviewing multiple similar changes together - Phase 3 enhancement)
- Integration with external monitoring services (Datadog, New Relic, etc.)
- Slack notifications for API failures (to be specified in separate alerting feature)
- SSO integration with existing Réfugiés.info authentication system (to be specified in separate feature)

## Clarifications

### Session 2025-10-20

- Q: What should happen when Data Inclusion or Carif Oref APIs are temporarily unavailable during ingestion? → A: Queue programs and retry with exponential backoff until APIs recover (up to 24 hours). Slack notification should be sent (feature to be specified later).
- Q: How should the system identify unique programs when the same program appears in both Data Inclusion and Carif Oref with potentially different IDs? → A: Use source ID as primary key; treat each source as independent (no deduplication). Data Inclusion schema includes unique ID that guarantees deduplication (https://gip-inclusion.github.io/data-inclusion-schema/latest/service/#id).
- Q: What is the maximum acceptable processing time for a single program to complete all 7 pipeline stages (end-to-end latency)? → A: 24 hours (1 day) for complete pipeline execution.
- Q: What should happen when a program is stuck in a manual review queue (enrichment, validation) for more than a configurable threshold (e.g., 7 days)? → A: Send notification to editorial team and mark as "review_overdue" but keep in queue.
- Q: What authentication/authorization mechanism should the diff review interface use for editorial team access? → A: Supabase Auth with email/password + role-based access control (RBAC). SSO integration with existing Réfugiés.info system to be resolved at a later stage.

### Session 2025-10-21

- Q: Where should editorial policy validation fit in the pipeline? → A: Immediately after ingestion, before reconciliation. This ensures non-compliant programs are rejected early without wasting processing resources.
- Q: Should editorial policy validation be a separate stage or part of ingestion? → A: Separate stage. Semantically distinct from ingestion (which fetches data) and enables independent testing/deployment.
- Q: How should the system handle Carif-Oref data? → A: Fetch CSV export daily, reconcile with Data Inclusion records using structure_id and id fields, scrape additional details from Carif-Oref website URLs, and merge data with Carif-Oref taking precedence for overlapping fields.
- Q: What URL format should be used to construct Carif-Oref website links? → A: https://www.intercariforef.org/dian/[dept]_[structure_id]/[dept]_[service_id]/[...]/[encoded_name] (URL-encode the program name).
- Q: Should reconciliation be enhanced to include Carif-Oref, or is it a separate stage? → A: Enhance the existing reconciliation stage to include Carif-Oref data fetching, matching, scraping, and merging. This is part of the reconciliation responsibility.
