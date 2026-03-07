# Benchmark Protocol

## Overview

OpenProblemAtlas can serve as a benchmark for evaluating AI reasoning systems on genuine open problems. This document describes the protocol for constructing fair, contamination-aware evaluation subsets.

## Principles

1. **Atlas first, benchmark second.** The primary goal is a reliable database. Benchmark use is a downstream application.
2. **Rolling subsets.** Evaluation subsets are drawn from the main atlas and frozen monthly. Fresh problems reduce contamination risk.
3. **No eval-washing.** Partial results or heuristic solutions do not count as "solved." Only verified status changes count.
4. **Reproducibility.** Every evaluation must record: model, version, prompt, tools, date, and exact snapshot used.

## Monthly Snapshot Process

1. On the 1st of each month, a frozen snapshot is generated from current canonical data.
2. The snapshot is tagged as a GitHub release: `snapshot-YYYY-MM-DD`.
3. The snapshot includes:
   - `problems.json` — all verified problems
   - `problems.parquet` — same data in Parquet format (if available)
   - `stats.json` — summary statistics
   - `changelog.md` — changes since last snapshot

## Evaluation Subset Construction

### Rolling Subset

A subset of problems selected for evaluation, refreshed monthly:

- **Size:** 50–100 problems
- **Selection criteria:**
  - Status: `open` only
  - Confidence: `high`
  - Formality score: ≥ 0.7
  - Has canonical statement
  - Not in any previous rolling subset within 3 months (anti-contamination)

### Contamination Awareness

- Problems appearing in popular training datasets (e.g., MATH, GSM8K, competition archives) are flagged.
- The `contamination_risk` field (future addition) will indicate:
  - `low` — Problem is niche, unlikely in training data
  - `medium` — Problem is well-known but statement is original
  - `high` — Problem and solution widely available online

### Difficulty Tiers

| Tier | Description | Typical time for expert |
|------|-------------|------------------------|
| 1 | Research-level, unknown solution | Hours to years |
| 2 | Known hard, partial results exist | Hours to days |
| 3 | Accessible with tools, unclear if open | Minutes to hours |

## Evaluation Metrics

For AI systems attempting open problems:

| Metric | Description |
|--------|-------------|
| `progress_rate` | Fraction of problems with meaningful partial progress |
| `decomposition_quality` | Quality of problem decomposition (expert-rated) |
| `formalization_rate` | Fraction of problems with valid formal statements |
| `false_claim_rate` | Fraction of attempts with incorrect claims (lower is better) |
| `reproducibility` | Fraction of attempts that are reproducible |

## Reporting

Benchmark results should include:
- Snapshot version used
- Complete list of problem IDs attempted
- Per-problem attempt records (following the attempt schema)
- Aggregate metrics
- Known limitations

## Anti-Gaming

- Do not evaluate on problems where the model's training data likely contains the solution.
- Do not claim "solved" without independent verification.
- Report negative results and failures — they are valuable data.
