# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]  
**Primary Dependencies**: [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION]  
**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]  
**Testing**: [e.g., pytest, XCTest, cargo test or NEEDS CLARIFICATION]  
**Target Platform**: [e.g., Linux server, iOS 15+, WASM or NEEDS CLARIFICATION]
**Project Type**: [single/web/mobile - determines source structure]  
**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]  
**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]  
**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Validate compliance with Nexus Constitution (`.specify/memory/constitution.md`):

- [ ] **Data Quality First**: Data validation and reconciliation strategy defined for all pipeline stages
- [ ] **Pipeline Modularity**: Each stage designed as independent, testable component with clear contracts
- [ ] **Multilingual by Design**: 8-language support planned with translation quality validation
- [ ] **Editorial Compliance**: Réfugiés.info editorial charter compliance checks integrated
- [ ] **Integration Independence**: Clean API contracts with Réfugiés.info (reference: karfur repo)
- [ ] **Observability & Traceability**: Structured logging, metrics, and data lineage tracking planned
- [ ] **Incremental Delivery**: MVP scope clearly defined, user stories prioritized for value delivery
- [ ] **Technology Foundation**: Monorepo structure defined; Python for pipeline, Node.js for tooling; dependency management specified
- [ ] **User-Centered Development (NON-NEGOTIABLE)**: User research plan with Réfugiés.info end users; iterative testing strategy; analytics implementation; AI transparency disclosure approach
- [ ] **Notebook Governance**: Notebooks organized in notebooks/ directory; categories defined; nbstripout configured; security review for credentials
- [ ] **Langage Clair (NON-NEGOTIABLE)**: AI model training on Réfugiés.info corpus; readability validation; editorial review workflow; feedback loop for model improvement
- [ ] **TDD Compliance (NON-NEGOTIABLE)**: Test-first approach planned; red-green-refactor cycle enforced; test coverage strategy defined
- [ ] **GDPR Compliance (NON-NEGOTIABLE)**: Data minimization strategy; legal basis documented; user rights mechanisms; DPIA conducted if needed; DPAs with third parties

*If any principle cannot be satisfied, document justification in Complexity Tracking section.*

## Project Structure

### Documentation (this feature)

```
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]

# [REMOVE IF UNUSED] Option 4: Polyglot Monorepo (Nexus: Python pipeline + Node.js tooling)
# Constitution Principles VIII (Technology Foundation) + XI (Langage Clair)
packages/
├── pipeline/              # Python: Data pipeline stages
│   ├── src/
│   │   ├── ingestion/
│   │   ├── reconciliation/
│   │   ├── enrichment/
│   │   ├── langage_clair/     # ⭐ AI-assisted plain language transformation
│   │   ├── translation/
│   │   ├── validation/
│   │   └── publication/
│   ├── tests/
│   │   ├── contract/
│   │   ├── integration/
│   │   └── unit/
│   ├── pyproject.toml     # uv dependency management
│   └── pytest.ini
│
├── api/                   # Python: REST API (if needed)
│   ├── src/
│   ├── tests/
│   └── pyproject.toml
│
└── tooling/               # Node.js: Build scripts, dev tools
    ├── src/
    ├── package.json
    └── tsconfig.json

# Monorepo root files
├── pyproject.toml         # Root Python workspace config (uv workspaces)
├── package.json           # Root Node.js workspace config (pnpm workspaces)
├── .github/
│   └── workflows/         # CI/CD pipelines
└── docs/                  # Shared documentation
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |

