# Nexus

> AI pipeline transforming integration data into multilingual information sheets for refugees and immigrants

[![Constitution](https://img.shields.io/badge/constitution-v1.5.0-blue.svg)](.specify/memory/constitution.md)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 🎯 Mission

Nexus is an AI-powered data pipeline that processes integration services data and generates high-quality, multilingual information sheets for [Réfugiés.info](https://refugies.info) — a trusted platform serving refugees and immigrants in France.

### The Challenge

Information about integration services (French language learning, employment support, housing assistance) exists across fragmented sources but often fails to meet the needs of vulnerable populations:

- **Language barriers**: Content rarely available in the 8+ languages refugees speak
- **Quality inconsistency**: Information sheets vary wildly in clarity and completeness
- **Manual overhead**: Creating and maintaining multilingual content is time-intensive
- **Accessibility gaps**: Content not optimized for low-literacy or mobile-first users

### Our Solution

Nexus automates the pipeline from raw data to publication-ready information sheets:

```
Data Sources → Ingestion → Reconciliation → Enrichment → Langage Clair → Translation → Validation → Publication
   (Carif Oref,      ↓            ↓              ↓            ↓              ↓            ↓            ↓
   Data Inclusion)  Clean      Merge data    Fill gaps   AI-assisted    8 languages  Editorial    Réfugiés.info
                    & validate  from APIs    via web      transformation + quality    charter      API
                                             scraping     to plain       checks       compliance
                                                          language
```

**Key Innovation**: The **Langage Clair** stage uses AI to transform bureaucratic/technical source text into clear, accessible French—reifying the expertise of Réfugiés.info's editorial team. This AI-assisted process dramatically increases throughput compared to purely manual editorial work while maintaining quality standards.

**Example Transformation**:
- **Before**: "Dispositif d'apprentissage du français : permet de gagner en autonomie au quotidien grâce à des ateliers sociolinguistiques et cours de français langue professionnelle"
- **After**: "Des ateliers 2 fois par semaine pour progresser en français, mieux communiquer au quotidien et dans le milieu professionnel."

## ✨ Key Features

- **✨ Langage Clair AI**: Transforms bureaucratic text into clear, accessible French using AI trained on Réfugiés.info editorial expertise
- **🌍 Multilingual by Design**: Generates content in 8 languages with quality validation
- **📊 Data Quality First**: Validates and reconciles data at every pipeline stage
- **🔍 Observability**: Complete traceability from source data to published content
- **🧩 Modular Architecture**: Independent, testable pipeline stages
- **👥 User-Centered**: Built with mandatory user research and iterative testing
- **🔒 Privacy-First**: GDPR-compliant with AI-specific privacy safeguards
- **📝 Editorial Compliance**: Adheres to Réfugiés.info editorial charter standards

## 🏗️ Architecture

### Technology Stack

**Polyglot Monorepo** (Python-first + Node.js tooling):

Following [dsfr-kit](https://github.com/betagouv/dsfr-kit) convention: Python packages in `libs/`, Node.js packages in `packages/`

```
nexus/
├── libs/                  # Python packages (independent libraries)
│   ├── common/            # Shared utilities and types
│   │   ├── src/
│   │   └── tests/
│   ├── ingestion/         # Data ingestion stage
│   │   ├── src/
│   │   └── tests/
│   │       ├── contract/
│   │       ├── integration/
│   │       └── unit/
│   ├── reconciliation/    # Data reconciliation stage
│   │   ├── src/
│   │   └── tests/
│   ├── enrichment/        # Data enrichment stage
│   │   ├── src/
│   │   └── tests/
│   ├── langage_clair/     # ⭐ AI plain language transformation
│   │   ├── src/
│   │   └── tests/
│   ├── translation/       # Multilingual translation stage
│   │   ├── src/
│   │   └── tests/
│   ├── validation/        # Quality validation stage
│   │   ├── src/
│   │   └── tests/
│   └── publication/       # Publication to Réfugiés.info
│       ├── src/
│       └── tests/
├── packages/              # Node.js packages
│   └── tooling/           # Build scripts, dev tools
├── notebooks/             # Jupyter: Exploratory analysis
└── docs/                  # Documentation
```

**Core Technologies**:
- **Python 3.12+**: Pipeline implementation (data processing, AI/ML)
- **uv**: Fast Python package management and workspace configuration
- **ruff**: Python linting and formatting
- **Node.js 22+**: Developer tooling
- **pnpm**: Node.js package management
- **biome**: JavaScript/TypeScript linting
- **pytest**: Testing framework (contract, integration, unit tests)
- **just**: Command runner for common development tasks

### Pipeline Stages

Each stage is implemented as an independent Python library in `libs/`, enabling:
- **Independent development**: Teams can work on different stages simultaneously
- **Independent testing**: Each stage has its own test suite (contract, integration, unit)
- **Independent deployment**: Stages can be deployed and scaled separately
- **Clear dependencies**: Shared code lives in `libs/common/`

1. **Ingestion** (`libs/ingestion/`): Fetch data from Data Inclusion API (includes Carif Oref data)
2. **Reconciliation** (`libs/reconciliation/`): Merge and deduplicate data from multiple sources
3. **Enrichment** (`libs/enrichment/`): Fill gaps via Carif Oref API and web scraping
4. **Langage Clair** (`libs/langage_clair/`) ⭐: AI-assisted transformation of bureaucratic/technical text into clear, accessible French (reifying Réfugiés.info editorial expertise)
5. **Translation** (`libs/translation/`): Generate multilingual content (8 languages) from the plain language French
6. **Validation** (`libs/validation/`): Ensure editorial charter compliance and quality standards
7. **Publication** (`libs/publication/`): Push to Réfugiés.info via API (to be designed)

## 🚀 Getting Started

### Prerequisites

- **Python 3.12+** with [uv](https://github.com/astral-sh/uv) installed
- **Node.js 22+** with [pnpm](https://pnpm.io/) installed
- **just** command runner ([installation](https://github.com/casey/just#installation))
- **Git** for version control

### Installation

```bash
# Clone the repository
git clone git@github.com:refugies-info/nexus.git
cd nexus

# Install all dependencies (Python + Node.js + pre-commit hooks)
just install

# Or install manually:
uv sync                      # Install Python dependencies
pnpm install                 # Install Node.js dependencies
uv run pre-commit install    # Setup pre-commit hooks (includes nbstripout)
```

### Common Development Tasks

```bash
# List all available commands
just

# Run linting (Python + Node.js)
just lint

# Format code (Python + Node.js)
just format

# Run tests (all libraries)
just test

# Run tests for specific library
uv run pytest libs/ingestion/tests/

# Type checking
uv run mypy libs/

# Run notebooks (exploratory work)
jupyter lab notebooks/
```

### Running Pipeline Stages

Each pipeline stage is an independent library that can be developed and tested separately:

```bash
# Example: Run ingestion stage (once implemented)
uv run python -m libs.ingestion

# Example: Import shared utilities
uv run python -c "from libs.common import utils"
```

## 📋 Development Workflow

Nexus follows a **specification-driven development** approach with constitutional principles:

### 1. Feature Specification

```bash
# Create feature branch
git checkout -b 001-data-ingestion

# Generate specification
/speckit.specify "Implement data ingestion from Data Inclusion API"
```

### 2. Implementation Planning

```bash
# Generate implementation plan
/speckit.plan
```

### 3. Task Generation

```bash
# Generate actionable tasks
/speckit.tasks
```

### 4. Analysis & Validation

```bash
# Check for inconsistencies
/speckit.analyze
```

### 5. Implementation

```bash
# Execute tasks with TDD (test-first approach)
/speckit.implement
```

## 🧪 Testing

**Test-Driven Development (TDD) is mandatory** per our constitution:

```bash
# Write tests FIRST (red phase)
uv run pytest tests/contract/test_ingestion.py  # Should FAIL

# Implement feature (green phase)
# ... write code ...

# Tests should now PASS
uv run pytest tests/contract/test_ingestion.py

# Refactor while keeping tests green
# ... improve code quality ...
```

### Test Categories

- **Contract Tests**: Validate API contracts and interfaces
- **Integration Tests**: Test end-to-end pipeline stages
- **Unit Tests**: Test individual functions and classes

## 📚 Documentation

- **[Constitution](.specify/memory/constitution.md)**: Project principles and governance (v1.5.0)
- **[Contributing](CONTRIBUTING.md)**: Development guidelines and workflow
- **[Architecture](docs/architecture.md)**: Detailed system design
- **[API Specification](docs/api-spec.md)**: Réfugiés.info publication API design

## 🌟 Constitutional Principles

Nexus is governed by [12 core principles](.specify/memory/constitution.md):

1. **Data Quality First**: Validation and reconciliation at every stage
2. **Pipeline Modularity**: Independent, testable components
3. **Multilingual by Design**: 8-language support as first-class requirement
4. **Editorial Compliance** *(NON-NEGOTIABLE)*: Réfugiés.info charter adherence
5. **Integration Independence**: Standalone system with clean API contracts
6. **Observability & Traceability**: Complete pipeline visibility
7. **Incremental Delivery**: MVP-first with Carif Oref use case
8. **Technology Foundation**: Polyglot monorepo (Python-first)
9. **User-Centered Development** *(NON-NEGOTIABLE)*: Mandatory user research
10. **Notebook Governance**: Structured exploratory work with security
11. **Langage Clair** *(NON-NEGOTIABLE)* ⭐: AI-assisted plain language transformation
12. **Culturally-Aware Translation** *(NON-NEGOTIABLE)* ⭐: Cultural mediation with glossaries and annotations

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Code of conduct
- Development setup
- Pull request process
- Testing requirements
- Constitutional compliance

### Quick Contribution Guide

1. **Fork & Clone**: Fork the repo and clone locally
2. **Feature Branch**: Create branch following `###-feature-name` convention
3. **User Research**: Conduct user research if feature affects end users
4. **TDD**: Write tests first, ensure they fail, then implement
5. **Constitution Check**: Validate compliance with all principles
6. **Pull Request**: Submit PR with test evidence and documentation

## 📊 Project Status

### Current Phase: MVP Development

**Focus**: French language learning information sheets from Carif Oref

- [x] Constitution ratified (v1.5.0)
- [x] Project structure defined
- [x] Development templates created
- [ ] Data ingestion implementation
- [ ] Translation pipeline
- [ ] Editorial validation
- [ ] Réfugiés.info API design
- [ ] User research for AI transparency

### Roadmap

**Q4 2025**: MVP - Carif Oref French learning sheets
- Data ingestion from Data Inclusion
- Basic translation pipeline (8 languages)
- Editorial validation workflow
- Réfugiés.info API specification

**Q1 2026**: Expansion
- Additional data sources
- Enhanced translation quality
- User feedback integration
- Performance optimization

## 🔗 Related Projects

- **[Réfugiés.info](https://github.com/refugies-info/karfur)**: Main platform (publication target)
- **[Data Inclusion](https://www.data.inclusion.beta.gouv.fr/)**: Primary data source
- **[Carif Oref](https://www.intercariforef.org/)**: French learning data provider

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💬 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/refugies-info/nexus/issues)
- **Discussions**: [GitHub Discussions](https://github.com/refugies-info/nexus/discussions)
- **Email**: [contact@refugies.info](mailto:contact@refugies.info)

## 🙏 Acknowledgments

- **Réfugiés.info team**: For platform integration and user research access
- **Carif Oref**: For providing French learning data
- **Data Inclusion**: For integration data aggregation
- **ai-kit project**: For constitutional principles inspiration

---

**Built with ❤️ for refugees and immigrants in France**
