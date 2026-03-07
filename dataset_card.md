---
license: cc-by-sa-4.0
task_categories:
  - text-generation
  - question-answering
language:
  - en
tags:
  - mathematics
  - open-problems
  - theorem-proving
  - benchmark
  - ai-for-math
size_categories:
  - n<1K
---

# OpenProblemAtlas: Open Problems Dataset

A structured, machine-readable dataset of **unsolved problems** in mathematics,
theoretical computer science, and mathematical physics.

## Why This Dataset?

Existing math benchmarks (MATH, GSM8K, MiniF2F) contain **solved** problems.
This dataset contains **unsolved** problems -- the frontier of human knowledge.

Use it to:
- Benchmark AI theorem proving systems on problems with **unknown** answers
- Train models to understand the structure of open problems
- Build tools for mathematical research navigation

## Dataset Structure

Each problem includes:
- `id`: Unique identifier (e.g., `opa.mathematics.number-theory.collatz-conjecture`)
- `title`: Canonical title
- `domain`: mathematics / theoretical-cs / mathematical-physics
- `statement_canonical`: Formal problem statement
- `statement_informal`: Accessible description
- `status`: open / partially_solved / solved / disproved
- `tier`: tier_1 (machine-ready) / tier_2 / tier_3
- `verification_profile`: statement precision, solution checkability, machine actionability
- `scores`: impact, underexplored, toolability, formality, ai_fit (0-1)
- `full_yaml`: Complete problem metadata in YAML format

## Quick Start

```python
from datasets import load_dataset

ds = load_dataset("OpenProblemAtlas/open-problems")

# Filter for machine-actionable problems
tier1 = ds.filter(lambda x: x["tier"] == "tier_1")

# Find high-impact underexplored problems
gems = ds.filter(lambda x: x["impact"] > 0.7 and x["underexplored"] > 0.5)
```

## Also Available

- **PyPI**: `pip install openproblem-atlas`
- **GitHub**: https://github.com/OpenProblemAtlas/open-problem-atlas
- **Website**: https://openproblem-atlas.org

## Citation

```bibtex
@misc{openproblem-atlas,
  title  = {OpenProblemAtlas: A Living Atlas of Open Problems},
  year   = {2026},
  url    = {https://github.com/OpenProblemAtlas/open-problem-atlas}
}
```
