<!--
Sync Impact Report:
- Version: 1.4.0 → 1.4.1 (PATCH: Clarified monorepo structure following dsfr-kit convention)
- Modified: Principle VIII (Technology Foundation)
  * Clarified language separation: Python packages in libs/, Node.js packages in packages/
  * Following dsfr-kit convention for cleaner separation
  * Updated all pipeline stage references to reflect libs/ location
- Templates requiring updates:
  ✅ plan-template.md (Updated monorepo structure: libs/ for Python, packages/ for Node.js)
  ✅ tasks-template.md (Updated path conventions to reflect libs/pipeline/src/)
  ✅ README.md (Updated architecture diagram with libs/ and packages/ separation)
- Follow-up: 
  * Create libs/ and packages/ directory structure when implementing first feature
  * Collect Réfugiés.info editorial corpus for model training
  * Define readability metrics and validation criteria
  * User research needed to determine AI transparency disclosure formulation
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
- **Translation source MUST be plain language French** (see Principle XI: Langage Clair) to ensure clarity is preserved across all languages
- Translation quality MUST meet Réfugiés.info editorial charter standards
- Language-specific validation MUST be applied (character encoding, right-to-left text, cultural appropriateness)
- Translation metadata (source language, translation date, translator/service used) MUST be preserved
- Untranslated or low-quality translations MUST be flagged for human review

**Rationale**: The target audience includes refugees and immigrants with diverse linguistic backgrounds. Quality multilingual content is essential for accessibility and impact, as documented in the Réfugiés.info impact report. Translating from plain language French (rather than complex source text) ensures clarity is maintained across all target languages.

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

### VIII. Technology Foundation

**MUST** maintain a polyglot monorepo architecture with Python-first pipeline development:
- **Monorepo Structure**: All Nexus components (pipeline, APIs, tooling) MUST reside in a single repository
- **Language Separation**: Python packages MUST be in `libs/` directory; Node.js packages MUST be in `packages/` directory (following dsfr-kit convention)
- **Python-First**: Data pipeline stages (ingestion, reconciliation, enrichment, langage_clair, translation, validation, publication) MUST be implemented in Python
- **Node.js for Tooling**: Developer tooling, build scripts, and auxiliary services MAY use Node.js when appropriate
- **Shared Standards**: Linting, formatting, and type checking MUST be enforced across all languages
- **Dependency Management**: Each language ecosystem MUST have clear dependency management (e.g., uv for Python, pnpm for Node.js)
- **Code Quality Tools**: Consistent tooling for linting and formatting (e.g., ruff for Python, biome for Node.js)
- **Monorepo Tooling**: Build orchestration and task running MUST support cross-language dependencies

**Rationale**: Python is the industry standard for data pipelines and AI/ML workflows, providing rich ecosystem support for data processing, API integration, and testing. A monorepo ensures atomic changes across components and simplifies dependency management. Node.js complements Python for developer tooling where JavaScript ecosystem tools excel.

### IX. User-Centered Development (NON-NEGOTIABLE)

**MUST** adopt iterative, user-centered practices to ensure information sheets meet real user needs:

**User Research Requirements**:
- Conduct user research with Réfugiés.info end users before building features (interviews, observations, usability testing)
- Identify and validate user needs with actual refugees and immigrants, not just Réfugiés.info staff
- Document user personas representing diverse linguistic backgrounds, tech literacy levels, and access contexts
- Test information sheet prototypes with representative users before full implementation
- Consider accessibility needs: multilingual users, low-literacy users, mobile-first access

**Iterative Development**:
- Release minimum viable products (MVPs) early for user feedback via Réfugiés.info
- Follow alpha → beta → production progression with user testing at each stage
- Iterate based on real user feedback from Réfugiés.info analytics and user research
- Be willing to pivot or discard features that don't meet validated user needs
- Validate translation quality and cultural appropriateness with native speakers

**Continuous Validation**:
- Implement analytics to understand how users interact with generated information sheets
- Monitor user behavior post-publication to identify comprehension issues or gaps
- Conduct regular usability testing with Réfugiés.info users
- Collect and act on user feedback through Réfugiés.info support channels
- Track key metrics: information sheet completion rates, user satisfaction, support ticket volume

**Data-Driven Decisions**:
- Base content and feature decisions on usage data, not assumptions
- Track metrics: sheet views, time-on-page, bounce rates, user satisfaction scores
- Use data to prioritize improvements (e.g., which topics need better translations)
- Validate hypotheses about user needs with actual usage patterns

**AI Transparency (MANDATORY)**:
- Disclose when content is AI-generated vs. human-written in information sheets
- Exact formulation MUST be determined through user research to avoid adoption barriers
- Provide clear explanations of AI's role in content generation and translation
- Enable Réfugiés.info editorial team to understand and override AI decisions
- Document AI limitations and known failure modes for editors

**Rationale**: Information sheets directly impact vulnerable populations making critical decisions about integration services. User-centered practices ensure content is comprehensible, culturally appropriate, and actionable. This is especially critical for refugees and immigrants who may be under stress, have varying tech literacy, or be accessing services in non-native languages. AI transparency builds trust while user research ensures disclosure doesn't create adoption barriers.

### X. Notebook Governance

**MUST** maintain Jupyter notebooks and exploratory tools in a structured manner with clear governance:

**Notebook Organization**:
- Notebooks MUST be organized in a top-level `notebooks/` directory
- Notebooks MUST be categorized by purpose to clarify their role:
  - **Exploratory**: Rapid experimentation, data quality analysis, hypothesis testing
  - **Production-Informing**: Model evaluation, translation quality benchmarks, performance analysis
  - **Learning Materials**: Tutorials, examples, documentation of complex workflows
  - **Archive**: Completed work preserved for audit trail and historical reference

**Security Requirements (NON-NEGOTIABLE)**:
- Notebooks MUST NOT contain hardcoded credentials, API keys, or sensitive personal data
- Use environment variables or secure configuration management for secrets
- Implement `nbstripout` or equivalent to remove notebook outputs before commit
- Add notebook output patterns to `.gitignore` (keep source, ignore execution artifacts)
- Conduct security review before publishing notebooks to public repositories
- Ensure compliance with GDPR when processing personal data in notebooks

**Quality Standards**:
- **Reproducibility**: Notebooks MUST include dependency specifications (uv workspace via pyproject.toml)
- **Documentation**: Each notebook MUST include:
  - Purpose and context (what question does this answer?)
  - Author and date
  - Data sources and versions
  - Expected runtime and resource requirements
  - Known limitations or assumptions
- **Version Control**: Notebooks MUST be committed with outputs stripped (use `nbstripout` pre-commit hook)
- **Code Quality**: Notebook code SHOULD follow Python standards (ruff linting where practical)
- **Cell Organization**: Use markdown cells to structure narrative, avoid monolithic code cells

**Integration with Development Workflow**:
- **Exploratory work**: Not required to follow SpecKit workflow, but insights MUST be captured in specifications when productionized
- **Learning materials**: Should be referenced in feature specifications (spec.md) and quickstart guides
- **Production-informing work**: MUST be documented in `plan.md` research section and referenced in quality metrics

**Tooling Standards**:
- **nbstripout**: Pre-commit hook to remove outputs before commit
- **nbconvert**: Convert notebooks to scripts or documentation formats
- **papermill**: Parameterize and execute notebooks programmatically for reproducible reporting (optional)
- **ruff**: Lint notebook code cells via `nbqa` or similar tools

**Rationale**: AI pipeline work involves exploratory data analysis, translation quality assessment, and model evaluation. Structured notebook governance balances rapid experimentation with security, reproducibility, and compliance. Unlike high-risk AI systems, Nexus doesn't require extensive regulatory documentation, but notebooks still need discipline to prevent credential leaks and ensure insights are captured for production use.

### XI. Langage Clair (Plain Language) (NON-NEGOTIABLE)

**MUST** transform all source content into clear, accessible French before translation:

**Plain Language Requirements**:
- Source text (bureaucratic, technical, administrative) MUST be transformed into "langage clair" (plain language French)
- Transformation MUST follow Réfugiés.info editorial guidelines for clarity, accessibility, and tone
- AI models MUST be trained on Réfugiés.info's editorial corpus to reify expert knowledge
- Plain language output MUST be validated against readability standards (e.g., Flesch-Kincaid adapted for French, SMOG index)
- Complex administrative terms MUST be simplified without losing accuracy
- Output MUST be optimized for low-literacy readers, non-native speakers, and mobile reading

**Editorial Expertise Reification**:
- AI transformation MUST embody Réfugiés.info editorial team's expertise and style
- Training data MUST include before/after examples from Réfugiés.info dispositif sheets
- Model outputs MUST maintain consistency with existing Réfugiés.info content tone and structure
- Editorial team MUST review and validate AI-generated plain language transformations
- Feedback loop MUST continuously improve AI model based on editorial corrections
- Model performance MUST be tracked with metrics: readability scores, editorial approval rate, user comprehension

**Quality Standards**:
- **Clarity**: Remove jargon, use common vocabulary, short sentences (max 20 words recommended)
- **Concreteness**: Replace abstract concepts with specific examples and actions
- **Actionability**: Focus on what users can do, not just what exists
- **Accessibility**: Optimize for CEFR A2-B1 French level (intermediate learners)
- **Accuracy**: Preserve factual correctness while simplifying language
- **Structure**: Use bullet points, clear headings, logical flow

**Transformation Examples** (from Réfugiés.info corpus):
- **Before**: "Dispositif d'apprentissage du français : permet de gagner en autonomie au quotidien grâce à des ateliers sociolinguistiques et cours de français langue professionnelle"
- **After**: "Des ateliers 2 fois par semaine pour progresser en français, mieux communiquer au quotidien et dans le milieu professionnel."

- **Before**: "Comprendre les différentes démarches administratives de la vie quotidienne, savoir remplir à l'ordinateur, savoir utiliser le bon interlocuteur"
- **After**: "Comprendre les différentes démarches administratives au quotidien : documents, formulaires, services. Répondre à un courrier, savoir quel service contacter."

**Translation Dependency**:
- Multilingual translation (Principle III) MUST use plain language French as source
- Translating from plain language ensures clarity is preserved across all 8 languages
- Complex source text translated directly would produce unclear multilingual content
- Plain language transformation MUST occur before translation stage in pipeline

**Human Oversight**:
- Editorial team MUST have final approval authority over AI-generated plain language content
- AI suggestions MUST be clearly marked as requiring editorial review
- Editorial corrections MUST be captured and used to retrain/fine-tune models
- High-stakes content (legal rights, safety information) MUST have mandatory human review

**Rationale**: Bureaucratic and technical source data is incomprehensible to vulnerable populations. Réfugiés.info's core value proposition is transforming this complexity into clear, actionable information. AI-assisted "langage clair" transformation scales this editorial expertise, enabling higher throughput while maintaining quality. This is the key innovation that differentiates Nexus from simple translation pipelines—it reifies years of editorial expertise into a scalable AI system.

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

**GDPR Compliance (NON-NEGOTIABLE)**:
- **Data Minimization**: Collect only data necessary for pipeline operation and information sheet generation
- **Legal Basis**: Document legal basis for processing personal data (legitimate interest, consent, etc.)
- **User Rights**: Implement mechanisms to support GDPR rights (access, rectification, erasure, portability)
- **Privacy Notices**: Provide clear information about data processing activities
- **Data Protection Impact Assessment (DPIA)**: Conduct DPIA if processing high-risk personal data
- **Data Processing Agreements**: Establish DPAs with third-party processors (translation APIs, etc.)

**Data Retention**:
- Source data MUST be retained with timestamps and provenance metadata
- Retention periods MUST be documented and justified (operational needs, legal requirements)
- Implement automatic deletion of data after retention period expires
- Personal data MUST NOT be retained longer than necessary
- Audit logs MUST be retained per compliance requirements (minimum periods TBD)

**AI-Specific Privacy**:
- Document what data is used for AI model training vs. inference
- Implement safeguards to prevent sensitive personal data leakage in AI-generated content
- Validate that translation APIs do not retain or train on user data
- Monitor AI outputs for inadvertent disclosure of personal information
- Provide transparency about AI decision-making processes to data subjects

**Security**:
- Encrypt personal data at rest and in transit (TLS 1.3+)
- Implement access controls and authentication for systems processing personal data
- Sanitize and validate all inputs to prevent injection attacks
- Conduct regular security assessments of data processing systems
- Document and test incident response procedures for data breaches

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

### Testing Discipline (NON-NEGOTIABLE)

**Test-Driven Development (TDD) is MANDATORY**:
- Tests MUST be written before implementation begins (test-first approach)
- Tests MUST fail initially, demonstrating they test the right behavior (red phase)
- Implementation MUST make tests pass with minimal code (green phase)
- Code MUST be refactored for quality while keeping tests green (refactor phase)
- **Red-Green-Refactor cycle is strictly enforced** - no implementation without failing tests first
- Breaking changes MUST be caught by contract tests before deployment
- Integration tests MUST validate real API contracts (not just mocks)
- Test coverage MUST be tracked and maintained at acceptable levels per component type

**Rationale**: TDD ensures code correctness, prevents regressions, and produces maintainable, well-designed code. For an AI pipeline handling critical refugee information, test discipline is non-negotiable to ensure reliability and quality.

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

### Development Workflow

**Issue Tracking & Planning**:
- All work MUST be tracked in an issue tracking system
- Features MUST be broken down into phases, with each phase represented as a sub-issue or task
- Sub-issues MUST correspond to implementation phases (Setup, Foundational, User Story 1, User Story 2, etc.)
- Issues MUST include acceptance criteria and links to relevant design documents
- Issue IDs MUST be traceable from branches, commits, and PRs

**Branch Naming Convention**:
- Feature branches: `feat/<issue-id>-<short-description>` (e.g., `feat/NEX-123-data-ingestion`)
- Bug fixes: `fix/<issue-id>-<short-description>`
- Documentation: `docs/<issue-id>-<short-description>`
- Branch names MUST include issue ID for traceability

**Pull Request Process**:
- PRs MUST reference the issue ID in title and description
- PRs MUST include test evidence (test output, coverage reports)
- PRs MUST pass all CI checks (linting, type checking, tests)
- PRs MUST be reviewed by at least one team member
- PRs MUST demonstrate TDD compliance (tests written first, initially failing)

**Commit Messages**:
- Follow conventional commits format: `<type>(<scope>): <description>`
- Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`
- Include issue ID in commit body or footer (e.g., `Refs: NEX-123`)

### Compliance Review

- All feature specifications MUST include Constitution Check section validating compliance
- Implementation plans MUST document any principle violations with justification
- Code reviews MUST verify adherence to principles (modularity, quality, observability, TDD)
- Complexity violations MUST be justified in Complexity Tracking section of plan.md

### Continuous Improvement

The constitution is a living document. As the project evolves and new patterns emerge, principles should be refined to reflect learned best practices. Amendments should be proposed proactively when gaps or conflicts are identified.

**Version**: 1.4.1 | **Ratified**: 2025-10-20 | **Last Amended**: 2025-10-20
