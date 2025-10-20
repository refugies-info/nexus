<!--
Sync Impact Report:
- Version: 0.0.0 → 1.0.0 (Initial constitution, amended to clarify Réfugiés.info API design requirement)
- New principles: Data Quality First, Pipeline Modularity, Multilingual by Design, Editorial Compliance, Integration Independence
- Amendment: Clarified that Réfugiés.info publication API does not exist and MUST be designed/specified by Nexus MVP
- Templates requiring updates:
  ✅ plan-template.md (Constitution Check section will reference these principles)
  ✅ spec-template.md (Requirements align with quality and compliance principles)
  ✅ tasks-template.md (Task categorization reflects pipeline stages and testing discipline)
- Follow-up: API specification design must be included as a deliverable in Carif Oref MVP planning
-->

# Nexus Constitution

## Core Principles

### I. Data Quality First

**MUST** validate and reconcile data at every pipeline stage:
- All input data from Data Inclusion MUST be validated against expected schemas
- Reconciliation with Carif Oref API is MANDATORY when discrepancies detected
- Web scraping for missing information MUST include source verification and timestamp
- Data quality metrics (completeness, accuracy, freshness) MUST be tracked and logged
- Invalid or incomplete data MUST be flagged and routed to manual review queue

**Rationale**: The pipeline transforms raw integration data into published information sheets that directly impact refugees and immigrants. Poor data quality undermines trust and can provide incorrect guidance on critical services like French language learning.

### II. Pipeline Modularity

**MUST** design each pipeline stage as an independent, testable component:
- Each stage (ingestion, reconciliation, enrichment, translation, publication) MUST be independently executable
- Stages communicate via well-defined contracts (schemas, APIs, message formats)
- Each stage MUST be testable in isolation with mock inputs/outputs
- Pipeline orchestration MUST support partial execution and replay from any stage
- Failure in one stage MUST NOT cascade to other stages; errors are contained and logged

**Rationale**: Modular design enables independent development, testing, and debugging. It allows the team to iterate on individual stages (e.g., improving translation quality) without affecting the entire pipeline.

### III. Multilingual by Design

**MUST** treat multilingual support as a first-class requirement, not an afterthought:
- All information sheets MUST support 8 languages (French + 7 others as per Réfugiés.info standards)
- Translation quality MUST meet Réfugiés.info editorial charter standards
- Language-specific validation MUST be applied (character encoding, right-to-left text, cultural appropriateness)
- Translation metadata (source language, translation date, translator/service used) MUST be preserved
- Untranslated or low-quality translations MUST be flagged for human review

**Rationale**: The target audience includes refugees and immigrants with diverse linguistic backgrounds. Quality multilingual content is essential for accessibility and impact, as documented in the Réfugiés.info impact report.

### IV. Editorial Compliance (NON-NEGOTIABLE)

**MUST** adhere to Réfugiés.info editorial charter for all published content:
- All generated information sheets MUST be validated against Réfugiés.info quality standards before publication
- Content structure, tone, and formatting MUST match Réfugiés.info dispositif sheets
- Automated quality checks MUST enforce charter compliance (readability, accessibility, accuracy)
- Content that fails editorial validation MUST be routed to human editorial review
- Publication to Réfugiés.info MUST include editorial approval workflow

**Rationale**: Nexus feeds content directly into Réfugiés.info, a trusted platform for vulnerable populations. Maintaining editorial standards is non-negotiable to preserve trust and ensure content quality matches existing Réfugiés.info dispositif sheets.

### V. Integration Independence

**MUST** operate independently from Réfugiés.info while maintaining clean integration:
- Nexus MUST function as a standalone system with its own data storage, processing, and APIs
- Integration with Réfugiés.info MUST be via well-defined API contracts (reference: github.com/refugies-info/karfur)
- **Nexus MVP MUST design and specify the Réfugiés.info publication API** (does not currently exist) to enable future implementation in the karfur repository
- Changes to Nexus MUST NOT require changes to Réfugiés.info core system (and vice versa)
- Nexus MUST support multiple output targets (not just Réfugiés.info) for future extensibility
- API versioning MUST be enforced to prevent breaking changes

**Rationale**: Independence ensures Nexus can evolve, scale, and serve other use cases without being tightly coupled to Réfugiés.info. It also reduces risk of disrupting the production Réfugiés.info platform. Since the publication API doesn't exist yet, Nexus must define the contract to guide its development.

### VI. Observability & Traceability

**MUST** provide complete visibility into pipeline execution and data lineage:
- Every data transformation MUST be logged with input, output, and transformation metadata
- Pipeline execution MUST emit structured logs (JSON format) for monitoring and debugging
- Data lineage MUST be traceable from source (Data Inclusion/Carif Oref) to publication (Réfugiés.info)
- Performance metrics (processing time, throughput, error rates) MUST be collected per pipeline stage
- Alerts MUST be configured for pipeline failures, data quality issues, and SLA violations

**Rationale**: AI pipelines are complex and opaque. Observability is essential for debugging, quality assurance, and continuous improvement. Traceability ensures accountability and enables root cause analysis.

### VII. Incremental Delivery

**MUST** deliver value incrementally, starting with the Carif Oref French learning use case:
- Initial scope: French language learning information sheets from Carif Oref (via Data Inclusion)
- Each pipeline stage MUST be deliverable and demonstrable independently
- MVP MUST process at least one complete information sheet end-to-end before expanding scope
- New data sources or content types MUST be added incrementally after MVP validation
- User stories MUST be prioritized to deliver the highest-value functionality first

**Rationale**: The Carif Oref French learning use case provides a concrete, bounded problem to validate the pipeline architecture. Incremental delivery reduces risk and enables early feedback from Réfugiés.info stakeholders.

## Data Sources & Integration

### Primary Data Sources

- **Data Inclusion**: Primary entry point for integration data (includes Carif Oref data)
- **Carif Oref API**: Direct reconciliation and enrichment source
- **Web Scraping**: Fallback for missing information (with source verification)
- **Réfugiés.info Publication API**: Publication target (TO BE DESIGNED - does not currently exist; Nexus MVP MUST produce API specification to facilitate development in github.com/refugies-info/karfur)

### Integration Contracts

- All external API integrations MUST have documented contracts (request/response schemas, error handling, rate limits)
- **Réfugiés.info Publication API**: Nexus MUST design and document the API specification (OpenAPI/Swagger) as a deliverable of the Carif Oref MVP to enable implementation in the karfur repository
- API client libraries MUST handle retries, timeouts, and circuit breaking
- API changes MUST be versioned and backward-compatible or require migration plan
- Mock services MUST be available for testing without external dependencies (including mock implementation of the to-be-developed Réfugiés.info publication API)

### Data Retention & Privacy

- Source data MUST be retained with timestamps and provenance metadata
- Personal data (if any) MUST comply with GDPR and French data protection regulations
- Data retention policies MUST be documented and enforced
- Audit logs MUST be retained for compliance and debugging

## Quality Standards

### Content Quality

- Information sheets MUST meet Réfugiés.info dispositif quality standards (see editorial charter)
- Automated quality checks MUST validate: completeness, accuracy, readability, accessibility
- Translation quality MUST be validated (automated + human review for critical content)
- Content MUST be reviewed against source material (Bonjour Bonjour sheets) for accuracy

### Technical Quality

- Code MUST follow language-specific best practices (linting, formatting, type safety)
- All pipeline stages MUST have integration tests validating end-to-end behavior
- Critical paths MUST have contract tests ensuring API compatibility
- Performance MUST meet defined SLAs (processing time, throughput) per pipeline stage

### Testing Discipline

- Tests MUST be written before implementation (test-first approach)
- Tests MUST fail before implementation (red-green-refactor)
- Breaking changes MUST be caught by contract tests before deployment
- Integration tests MUST validate real API contracts (not just mocks)

## Governance

### Constitution Authority

This constitution supersedes all other development practices and guidelines. When conflicts arise between this constitution and other documentation, the constitution takes precedence.

### Amendment Process

- Amendments MUST be proposed with clear rationale and impact analysis
- Version bumps follow semantic versioning:
  - **MAJOR**: Principle removal, redefinition, or backward-incompatible governance changes
  - **MINOR**: New principle added or material expansion of existing guidance
  - **PATCH**: Clarifications, wording improvements, non-semantic refinements
- Amendments MUST include Sync Impact Report documenting affected templates and artifacts
- All dependent templates (plan, spec, tasks) MUST be updated to reflect amendments

### Compliance Review

- All feature specifications MUST include Constitution Check section validating compliance
- Implementation plans MUST document any principle violations with justification
- Code reviews MUST verify adherence to principles (modularity, quality, observability)
- Complexity violations MUST be justified in Complexity Tracking section of plan.md

### Continuous Improvement

The constitution is a living document. As the project evolves and new patterns emerge, principles should be refined to reflect learned best practices. Amendments should be proposed proactively when gaps or conflicts are identified.

**Version**: 1.0.0 | **Ratified**: 2025-10-20 | **Last Amended**: 2025-10-20
