# Tasks: Polyglot Monorepo Setup

**Input**: Design documents from `/specs/001-monorepo-setup/`
**Prerequisites**: spec.md, plan.md, research.md, quickstart.md

**Issue Tracking**: Map phases to Linear sub-issues under [RI-909](https://linear.app/refugiesinfo/issue/RI-909/setup-polyglot-monorepo-structure)

**TDD Compliance**: Test infrastructure tasks must be completed before any pipeline implementation. This feature establishes the testing foundation itself.

**Organization**: Tasks grouped by developer story (DS1, DS2, DS3) to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which developer story this task belongs to (DS1, DS2, DS3)
- Include exact file paths in descriptions

## Path Conventions
- **Polyglot monorepo**: Python packages in `libs/`, Node.js packages in `packages/`
- **Python namespace**: `nexus.*` (e.g., `from nexus.common import utils`)
- **Test organization**: `tests/contract/`, `tests/integration/`, `tests/unit/` per library

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Create foundational monorepo structure and root configuration files

**Independent Test**: Directory structure exists and root configs are valid

### Tasks

- [X] T001 Create root directory structure: `libs/`, `packages/`, `notebooks/`, `docs/`
- [X] T002 Create `.gitignore` with Python cache, Node.js, notebook outputs, and env file exclusions
- [X] T003 [P] Create root `pyproject.toml` with uv workspace configuration for all 8 libs
- [X] T004 [P] Create root `package.json` with pnpm workspace configuration
- [X] T005 [P] Create `pnpm-workspace.yaml` defining packages/* workspace
- [X] T006 [P] Create `README.md` updates (already done, verify completeness)
- [X] T007 [P] Create `CONTRIBUTING.md` with developer setup instructions per FR-042 through FR-047

**Checkpoint**: Root structure ready - can now create individual libraries

---

## Phase 2: Developer Story 1 - Python Package Management (Priority: P1)

**Story Goal**: Set up Python package management with uv so developers can install dependencies and manage the Python workspace efficiently

**Why P1**: Foundation for all Python development - absolute minimum to start development

**Independent Test**: 
- `uv sync` installs all dependencies successfully
- `uv run python -c "import nexus.common"` resolves imports
- All 8 libraries are recognized by uv workspace

### DS1 Tasks

- [ ] T008 [DS1] Create `libs/common/` directory structure with `src/nexus/common/`, `tests/{contract,integration,unit}/`
- [ ] T009 [P] [DS1] Create `libs/common/pyproject.toml` with minimal dependencies (ruff, pytest, mypy, pre-commit, nbstripout)
- [ ] T010 [P] [DS1] Create `libs/common/src/nexus/common/__init__.py` with package marker
- [ ] T011 [P] [DS1] Create `libs/ingestion/` directory structure with `src/nexus/ingestion/`, `tests/{contract,integration,unit}/`
- [ ] T012 [P] [DS1] Create `libs/ingestion/pyproject.toml` with common dependency
- [ ] T013 [P] [DS1] Create `libs/ingestion/src/nexus/ingestion/__init__.py`
- [ ] T014 [P] [DS1] Create `libs/reconciliation/` directory structure with `src/nexus/reconciliation/`, `tests/{contract,integration,unit}/`
- [ ] T015 [P] [DS1] Create `libs/reconciliation/pyproject.toml` with common dependency
- [ ] T016 [P] [DS1] Create `libs/reconciliation/src/nexus/reconciliation/__init__.py`
- [ ] T017 [P] [DS1] Create `libs/enrichment/` directory structure with `src/nexus/enrichment/`, `tests/{contract,integration,unit}/`
- [ ] T018 [P] [DS1] Create `libs/enrichment/pyproject.toml` with common dependency
- [ ] T019 [P] [DS1] Create `libs/enrichment/src/nexus/enrichment/__init__.py`
- [ ] T020 [P] [DS1] Create `libs/langage_clair/` directory structure with `src/nexus/langage_clair/`, `tests/{contract,integration,unit}/`
- [ ] T021 [P] [DS1] Create `libs/langage_clair/pyproject.toml` with common dependency
- [ ] T022 [P] [DS1] Create `libs/langage_clair/src/nexus/langage_clair/__init__.py`
- [ ] T023 [P] [DS1] Create `libs/translation/` directory structure with `src/nexus/translation/`, `tests/{contract,integration,unit}/`
- [ ] T024 [P] [DS1] Create `libs/translation/pyproject.toml` with common dependency
- [ ] T025 [P] [DS1] Create `libs/translation/src/nexus/translation/__init__.py`
- [ ] T026 [P] [DS1] Create `libs/validation/` directory structure with `src/nexus/validation/`, `tests/{contract,integration,unit}/`
- [ ] T027 [P] [DS1] Create `libs/validation/pyproject.toml` with common dependency
- [ ] T028 [P] [DS1] Create `libs/validation/src/nexus/validation/__init__.py`
- [ ] T029 [P] [DS1] Create `libs/publication/` directory structure with `src/nexus/publication/`, `tests/{contract,integration,unit}/`
- [ ] T030 [P] [DS1] Create `libs/publication/pyproject.toml` with common dependency
- [ ] T031 [P] [DS1] Create `libs/publication/src/nexus/publication/__init__.py`
- [ ] T032 [DS1] Configure root `pyproject.toml` with pytest settings (testpaths, markers for contract/integration/unit)
- [ ] T033 [DS1] Configure root `pyproject.toml` with ruff settings (target py312, line-length 100, src=["libs"])
- [ ] T034 [DS1] Configure root `pyproject.toml` with mypy settings
- [ ] T035 [DS1] Run `uv sync` and verify all 8 libraries are installed
- [ ] T036 [DS1] Test import resolution: `uv run python -c "import nexus.common"`
- [ ] T037 [DS1] Test workspace: `uv run python -c "from nexus.common import *; from nexus.ingestion import *"`

**DS1 Checkpoint**: Python workspace functional - developers can add dependencies and import across libraries

---

## Phase 3: Developer Story 2 - Directory Structure & Tooling (Priority: P2)

**Story Goal**: Complete monorepo directory structure with linting and formatting tools so developers can write quality code following project standards

**Why P2**: Establishes code quality standards and complete workspace structure. Builds on P1 by adding quality gates and Node.js tooling.

**Independent Test**:
- `just lint` completes successfully with zero configuration errors
- `just format` formats both Python and Node.js code
- All required directories exist and are properly structured

### DS2 Tasks

- [ ] T038 [DS2] Create `packages/tooling/` directory structure with `src/`, `package.json`, `tsconfig.json`
- [ ] T039 [DS2] Configure `packages/tooling/package.json` with biome dependency
- [ ] T040 [DS2] Create `biome.json` at root with linting and formatting rules
- [ ] T041 [DS2] Create `notebooks/` directory for Jupyter notebooks
- [ ] T042 [DS2] Create `docs/` directory for shared documentation
- [ ] T043 [DS2] Create `justfile` at root with default recipe listing all commands
- [ ] T044 [P] [DS2] Add `install` recipe to `justfile` with prerequisite checks (uv, pnpm, just)
- [ ] T045 [P] [DS2] Add `lint` recipe to `justfile` running ruff and biome
- [ ] T046 [P] [DS2] Add `format` recipe to `justfile` running ruff format and biome format
- [ ] T047 [P] [DS2] Add `test` recipe to `justfile` running pytest
- [ ] T048 [P] [DS2] Add `test-lib` recipe to `justfile` for running tests on specific library
- [ ] T049 [DS2] Implement fail-fast error handling in `justfile` for missing prerequisites with specific error messages:
  - Check uv: "Error: uv not found. Install: curl -LsSf https://astral.sh/uv/install.sh | sh"
  - Check pnpm: "Error: pnpm not found. Install: npm install -g pnpm"
- [ ] T050 [DS2] Run `pnpm install` to verify Node.js workspace setup
- [ ] T051 [DS2] Test `just` command lists all available recipes
- [ ] T052 [DS2] Test `just lint` runs successfully (may have no violations yet)
- [ ] T053 [DS2] Test `just format` formats code without errors
- [ ] T054 [DS2] Verify directory structure matches plan.md specification

**DS2 Checkpoint**: Full tooling operational - developers have quality gates and command runner

---

## Phase 4: Developer Story 3 - Pre-commit Hooks & Testing (Priority: P3)

**Story Goal**: Pre-commit hooks and testing infrastructure so code quality is automatically enforced and developers can write tests

**Why P3**: Automates quality enforcement and enables TDD. Builds on P1 and P2 by adding automation and testing capabilities.

**Independent Test**:
- Pre-commit hooks run automatically on commit
- `just test` executes successfully (even with zero tests)
- Creating a test file in any library's tests/ directory is discovered by pytest

### DS3 Tasks

- [ ] T055 [DS3] Create `.pre-commit-config.yaml` at root
- [ ] T056 [P] [DS3] Add ruff hook to `.pre-commit-config.yaml` with --fix argument
- [ ] T057 [P] [DS3] Add ruff-format hook to `.pre-commit-config.yaml`
- [ ] T058 [P] [DS3] Add nbstripout hook to `.pre-commit-config.yaml` for notebook output removal
- [ ] T059 [P] [DS3] Add trailing-whitespace hook to `.pre-commit-config.yaml`
- [ ] T060 [P] [DS3] Add end-of-file-fixer hook to `.pre-commit-config.yaml`
- [ ] T061 [P] [DS3] Add check-yaml hook to `.pre-commit-config.yaml`
- [ ] T062 [P] [DS3] Add check-added-large-files hook to `.pre-commit-config.yaml`
- [ ] T063 [DS3] Run `uv run pre-commit install` to install hooks
- [ ] T064 [DS3] Test pre-commit hooks by running `uv run pre-commit run --all-files`
- [ ] T065 [DS3] Create sample test file `libs/common/tests/unit/test_sample.py` with passing test
- [ ] T066 [DS3] Run `just test` and verify pytest discovers and runs the sample test
- [ ] T067 [DS3] Test pytest markers: `uv run pytest -m unit` runs only unit tests
- [ ] T068 [DS3] Create sample notebook in `notebooks/` directory
- [ ] T069 [DS3] Add outputs to sample notebook and commit - verify nbstripout removes outputs
- [ ] T070 [DS3] Test commit with Python code - verify ruff runs automatically
- [ ] T071 [DS3] Remove sample test and notebook (cleanup)

**DS3 Checkpoint**: Automation complete - quality enforced automatically, TDD infrastructure ready

---

## Phase 5: Polish & Documentation

**Purpose**: Final touches and verification

### Tasks

- [ ] T072 Update `CONTRIBUTING.md` with actual setup experience and troubleshooting
- [ ] T073 [P] Verify all success criteria from spec.md are met (SC-001 through SC-008)
- [ ] T074 [P] Test complete setup flow: fresh clone → `just install` → verify under 3 minutes
- [ ] T075 [P] Test developer workflow: create feature branch → make change → commit → hooks run
- [ ] T076 [P] Document any deviations from plan.md in implementation notes
- [ ] T077 Create quickstart video or animated GIF showing setup process (optional)
- [ ] T078 Final review: all constitutional requirements (CAR-001 through CAR-012) satisfied

**Final Checkpoint**: Monorepo infrastructure complete and documented

---

## Dependencies & Execution Strategy

### Story Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (DS1: Python Package Management) ← MUST complete first
    ↓
Phase 3 (DS2: Directory Structure & Tooling) ← Depends on DS1
    ↓
Phase 4 (DS3: Pre-commit Hooks & Testing) ← Depends on DS1 + DS2
    ↓
Phase 5 (Polish)
```

### Parallel Execution Opportunities

**Phase 1**: T003, T004, T005, T006, T007 can run in parallel after T001-T002

**Phase 2 (DS1)**: 
- T009-T031 (all library creation) can run in parallel after T008
- T032-T034 (config files) can run in parallel
- T035-T037 must run sequentially at end

**Phase 3 (DS2)**:
- T044-T048 (justfile recipes) can run in parallel after T043
- T038-T042 can run in parallel

**Phase 4 (DS3)**:
- T056-T062 (pre-commit hooks) can run in parallel after T055
- T065-T071 (testing) must run sequentially

**Phase 5**: T073-T076 can run in parallel

### MVP Scope Recommendation

**Minimum Viable Product**: Complete Phase 1 + Phase 2 (DS1)

This provides:
- ✅ Directory structure
- ✅ Python workspace with uv
- ✅ All 8 libraries created
- ✅ Import resolution working
- ✅ Basic development capability

Developers can then:
- Add dependencies to libraries
- Write Python code
- Import across libraries

**Full Feature**: Complete all phases for production-ready infrastructure

---

## Implementation Strategy

### Incremental Delivery

1. **Sprint 1**: Phase 1 + Phase 2 (DS1) - Python workspace functional
2. **Sprint 2**: Phase 3 (DS2) - Tooling and quality gates
3. **Sprint 3**: Phase 4 (DS3) - Automation and testing
4. **Sprint 4**: Phase 5 - Polish and documentation

### Testing Approach

Since this is infrastructure setup, testing is primarily **verification testing**:

- **After each phase**: Run independent test criteria
- **Acceptance scenarios**: From spec.md developer stories
- **Success criteria**: All SC-001 through SC-008 from spec.md

No unit tests needed for configuration files themselves - the "tests" are successful execution of the tools.

### Risk Mitigation

**Risk**: Tool version incompatibilities
- **Mitigation**: Pin exact versions in configs, document in research.md

**Risk**: Developer machine doesn't have prerequisites
- **Mitigation**: justfile fail-fast with clear installation instructions

**Risk**: Import resolution issues across libraries
- **Mitigation**: Test imports early (T036-T037), verify workspace config

---

## Task Summary

- **Total Tasks**: 78
- **Phase 1 (Setup)**: 7 tasks
- **Phase 2 (DS1)**: 30 tasks
- **Phase 3 (DS2)**: 17 tasks
- **Phase 4 (DS3)**: 17 tasks
- **Phase 5 (Polish)**: 7 tasks

**Parallel Opportunities**: 45 tasks can run in parallel (marked with [P])

**Estimated Effort**:
- Phase 1: 2-3 hours
- Phase 2: 4-6 hours
- Phase 3: 3-4 hours
- Phase 4: 3-4 hours
- Phase 5: 2-3 hours
- **Total**: 14-20 hours

**MVP Effort**: 6-9 hours (Phase 1 + Phase 2 only)
