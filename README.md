# OpenProblemAtlas

[![Validate Data](https://github.com/OpenProblemAtlas/open-problem-atlas/actions/workflows/validate-data.yml/badge.svg)](https://github.com/OpenProblemAtlas/open-problem-atlas/actions/workflows/validate-data.yml)
[![Build Site](https://github.com/OpenProblemAtlas/open-problem-atlas/actions/workflows/build-site.yml/badge.svg)](https://github.com/OpenProblemAtlas/open-problem-atlas/actions/workflows/build-site.yml)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/Data-CC%20BY--SA%204.0-blue.svg)](LICENSE)
[![License: MIT](https://img.shields.io/badge/Code-MIT-green.svg)](LICENSE-CODE)
[![Problems](https://img.shields.io/badge/problems-50%2B-orange.svg)](data/problems/)

> A living, machine-readable atlas of open problems for researchers, AI agents, and theorem provers.

Discover verified open problems, mine fresh leads from the literature, and track reproducible AI/human attempts — all in one open dataset.

[**Explore the Atlas**](https://openproblem-atlas.org) | [**Browse Radar**](https://openproblem-atlas.org/radar.html) | [**Contribute a Problem**](.github/ISSUE_TEMPLATE/add-problem.yml) | [**Download Data**](data/snapshots/)

---

## What's Inside

| Layer | Description | Count |
|-------|-------------|-------|
| **Atlas** | Human-verified open problems with canonical sources | 50+ |
| **Radar** | Machine-mined candidate problems awaiting review | growing |
| **Lab** | Reproducible AI/human attempts on open problems | growing |
| **Explorer** | Searchable, filterable web interface | [coming soon] |

## Key Features

- **Verified Problems** — Every entry has a canonical statement, source, status evidence, and review record
- **Fresh Radar Leads** — Automated pipelines mine arXiv, surveys, and problem lists for new candidates
- **Formalization Links** — Filter for problems with Lean/Coq formalizations or `formalization-wanted` tags
- **Solver-Ready Tags** — Find problems amenable to SAT, SMT, computational search, or LLM reasoning
- **Underexplored Filter** — Discover important problems that haven't received enough attention
- **Reproducible Attempts** — Track AI and human attempts with full provenance (model, prompt, tools, date)
- **JSON / Parquet Snapshots** — Download structured data for your own analysis

## Quick Start

```bash
# Clone the repo
git clone https://github.com/OpenProblemAtlas/open-problem-atlas.git
cd open-problem-atlas

# Install dependencies
pip install -e ".[dev]"

# Validate all data
python -m review.validators.validate_all

# Build the site locally
cd site && npm install && npm run dev
```

## Directory Structure

```
open-problem-atlas/
├── data/
│   ├── problems/         # Verified open problems (YAML)
│   │   ├── mathematics/
│   │   ├── theoretical-cs/
│   │   └── mathematical-physics/
│   ├── leads/            # Unverified candidate problems
│   ├── attempts/         # AI/human attempt records
│   ├── collections/      # Curated problem collections
│   └── snapshots/        # Frozen monthly releases
├── schema/               # JSON Schema for all data types
├── ingestion/            # Source adapters and parsers
├── extraction/           # Candidate extraction & dedup
├── review/               # Validation and review tools
├── site/                 # Static site / explorer
├── api/                  # Read-only API
├── docs/                 # Project documentation
├── tests/                # Test suite
└── notebooks/            # Analysis notebooks
```

## Domains (v1)

1. **Mathematics** — Number theory, combinatorics, algebra, analysis, geometry, topology
2. **Theoretical Computer Science** — Complexity theory, algorithms, graph theory, cryptography
3. **Mathematical Physics** — Quantum information, statistical mechanics, quantum field theory

## Data Model

Every verified problem includes:

- Canonical title and statement
- Domain and subdomain tags
- Status (open / partially_solved / solved / disproved / conditional / independent / ambiguous)
- Source references with locators
- Status evidence
- Review metadata (reviewer, date, confidence)
- Scores (impact, underexplored, toolability, formality, ai_fit)
- Formalization status
- AI/tool readiness tags

See [docs/taxonomy.md](docs/taxonomy.md) for the full taxonomy and [schema/](schema/) for JSON Schemas.

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Ways to contribute:**

- Add a verified problem via [issue form](.github/ISSUE_TEMPLATE/add-problem.yml)
- Propose a radar lead via [issue form](.github/ISSUE_TEMPLATE/propose-lead.yml)
- Report a status change via [issue form](.github/ISSUE_TEMPLATE/report-status-change.yml)
- Submit an AI/human attempt via [issue form](.github/ISSUE_TEMPLATE/add-ai-attempt.yml)
- Improve data quality by reviewing existing entries
- Add formalization links (Lean/Coq)

## Source Policy

We distinguish three tiers of sources:

1. **Tier 1 (Canonical):** Problem lists, original papers, surveys, textbooks, expert-maintained pages
2. **Tier 2 (Supporting):** Community discussions, benchmark papers, authoritative databases
3. **Tier 3 (Lead only):** News, blogs, social media — never used as canonical sources

See [docs/source-policy.md](docs/source-policy.md) for details.

## License

Data: [CC BY-SA 4.0](LICENSE)
Code: [MIT](LICENSE-CODE)

## Citation

```bibtex
@misc{openproblem-atlas,
  title  = {OpenProblemAtlas: A Living Atlas of Open Problems},
  year   = {2026},
  url    = {https://github.com/OpenProblemAtlas/open-problem-atlas}
}
```
