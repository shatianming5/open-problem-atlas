# OpenProblemAtlas

[![Validate Data](https://github.com/OpenProblemAtlas/open-problem-atlas/actions/workflows/validate-data.yml/badge.svg)](https://github.com/OpenProblemAtlas/open-problem-atlas/actions/workflows/validate-data.yml)
[![Build Site](https://github.com/OpenProblemAtlas/open-problem-atlas/actions/workflows/build-site.yml/badge.svg)](https://github.com/OpenProblemAtlas/open-problem-atlas/actions/workflows/build-site.yml)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/Data-CC%20BY--SA%204.0-blue.svg)](LICENSE)
[![License: MIT](https://img.shields.io/badge/Code-MIT-green.svg)](LICENSE-CODE)
[![Problems](https://img.shields.io/badge/problems-1000%2B-orange.svg)](data/problems/)
[![Checkers](https://img.shields.io/badge/checkers-100%2B-brightgreen.svg)](verifiers/checkers/)
[![OPA-Bench](https://img.shields.io/badge/OPA--Bench-100%20problems-purple.svg)](data/collections/opa-bench-v2.yaml)

> A living, machine-readable atlas of open problems for researchers, AI agents, and theorem provers.

**The only structured dataset of unsolved problems with machine verification.** Unlike existing benchmarks (MATH, GSM8K, MiniF2F) that test solved problems, OpenProblemAtlas targets the frontier of human knowledge -- problems with unknown answers.

[**Explore the Atlas**](https://openproblem-atlas.org) | [**Browse Radar**](https://openproblem-atlas.org/radar.html) | [**Contribute a Problem**](.github/ISSUE_TEMPLATE/add-problem.yml) | [**Download Data**](data/snapshots/)

---

## What's Inside

| Layer | Description | Count |
|-------|-------------|-------|
| **Atlas** | Verified open problems with canonical sources and verification contracts | 500+ |
| **Radar** | Machine-mined candidate problems awaiting review | 900+ |
| **Lab** | Reproducible AI/human attempts on open problems | growing |
| **Checkers** | Python verification scripts for computational problems | 50 |
| **OPA-Bench** | Curated AI theorem-proving benchmark subset | 50 |

## Quick Start (Python)

```python
pip install -e .

from opa import atlas

# Load all open problems
problems = atlas.load(status="open")

# Get a specific problem
p = atlas.get("opa.mathematics.number-theory.collatz-conjecture")

# Search by keyword
results = atlas.search("Riemann")

# Filter by domain and tier
tier1_math = atlas.load(domain="mathematics", tier="tier_1")

# Get statistics
stats = atlas.stats()
```

## Quick Start (HuggingFace)

```python
from datasets import load_dataset
ds = load_dataset("OpenProblemAtlas/open-problems")

# Filter for machine-actionable problems
tier1 = ds.filter(lambda x: x["tier"] == "tier_1")

# Find high-impact underexplored problems
gems = ds.filter(lambda x: x["impact"] > 0.7 and x["underexplored"] > 0.5)
```

## Machine Verification

Every problem has a verification contract. 50 problems have executable Python checkers:

```bash
# Run a single checker
python -m runner verify opa.mathematics.number-theory.collatz-conjecture

# Run all checkers
python -m runner batch --backend python_checker

# List available contracts
python -m runner list
```

Checker types: `conjecture_check_range`, `counterexample_search`, `bound_verification`, `witness_search`, `proof_check`, `statement_verification`.

## OPA-Bench: AI Theorem Proving Benchmark

A curated subset of 50 problems selected for AI evaluation, balanced across domains:

```python
from opa.bench import load_bench
bench = load_bench()  # 50 problems with verification contracts
```

| vs. Existing Benchmarks | Problem Type | Answers Known? | Verification |
|------------------------|-------------|----------------|-------------|
| MATH / GSM8K | Competition math | Yes | Answer matching |
| MiniF2F / PutnamBench | Formal theorems | Yes | Lean/Isabelle |
| **OPA-Bench** | **Open problems** | **No** | **Multi-layer** |

## Key Features

- **Verified Problems** -- Canonical statement, source, status evidence, review record
- **Machine Verification** -- Every problem has a verification contract; 50 have executable checkers
- **Fresh Radar Leads** -- Automated pipelines mine arXiv, surveys, and problem lists
- **Formalization Links** -- Filter for problems with Lean/Coq formalizations or `formalization-wanted` tags
- **Solver-Ready Tags** -- Find problems amenable to SAT, SMT, computational search, or LLM reasoning
- **Underexplored Filter** -- Discover important problems that haven't received enough attention
- **JSON / Parquet Snapshots** -- Download structured data for your own analysis

## Directory Structure

```
open-problem-atlas/
├── data/
│   ├── problems/         # Verified open problems (YAML, 500+)
│   │   ├── mathematics/
│   │   ├── theoretical-cs/
│   │   └── mathematical-physics/
│   ├── leads/            # Unverified candidate problems (900+)
│   ├── attempts/         # AI/human attempt records
│   ├── collections/      # Curated collections (OPA-Bench)
│   └── snapshots/        # Frozen monthly releases
├── src/opa/              # Python SDK (atlas, bench)
├── verifiers/
│   ├── checkers/math/    # 50 Python verification scripts
│   └── contracts/        # 500+ verification contracts
├── runner/               # Verification runner (CLI + backends)
├── schema/               # JSON Schema for all data types
├── ingestion/            # Source adapters and parsers
├── site/                 # Static site / explorer
├── docs/                 # Project documentation
└── tests/                # Test suite
```

## Domains (v1)

1. **Mathematics** -- Number theory, combinatorics, algebra, analysis, geometry, topology
2. **Theoretical Computer Science** -- Complexity theory, algorithms, graph theory, cryptography
3. **Mathematical Physics** -- Quantum information, statistical mechanics, quantum field theory

## Data Model

Every verified problem includes:

- Canonical title and statement
- Domain and subdomain tags
- Status (open / partially_solved / solved / disproved / conditional / independent / ambiguous)
- Verification profile (statement precision, solution checkability, machine actionability)
- Source references with locators
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
- Write a new Python checker for a problem
- Add formalization links (Lean/Coq)

## Source Policy

We distinguish three tiers of sources:

1. **Tier 1 (Canonical):** Problem lists, original papers, surveys, textbooks, expert-maintained pages
2. **Tier 2 (Supporting):** Community discussions, benchmark papers, authoritative databases
3. **Tier 3 (Lead only):** News, blogs, social media -- never used as canonical sources

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
