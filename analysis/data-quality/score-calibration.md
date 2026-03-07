---
analyzer: codex/gpt-5.4
reasoning: xhigh
date: 2026-03-07
task: score calibration audit
scope: data/problems/
---

# Score Calibration Audit

## Executive summary

- Parsed **all 312/312 YAML files** under `data/problems/` and extracted all five score dimensions.
- Every file had a complete `scores` block; there were **no missing score values**.
- The overall score system is usable for rough filtering, but it is **not well calibrated for ranking**, especially on `underexplored` and `formality`.
- The strongest dataset-level signal is a **generation-style shift** between the first 50 files and the later 262:
  - the newer cohort is more compressed,
  - it uses fewer extreme values,
  - it contains all exact duplicate score vectors,
  - and it is markedly more templated.
- `impact` is the most believable dimension overall.
- `toolability` is directionally reasonable overall; I did **not** find any obvious “pure existence/topology problem with toolability > 0.7” failures after manual review.
- `underexplored` is the weakest semantic dimension: several very famous, heavily worked-on research programs are scored as if they were neglected.
- `formality` is mostly conservative, but a few broad research programs / meta-questions are scored as if they were crisp single conjectures.

## Method

1. Parsed every YAML file under `data/problems/` and extracted:
   - `impact`
   - `underexplored`
   - `toolability`
   - `formality`
   - `ai_fit`
2. Computed descriptive statistics for each dimension across all 312 files.
3. Looked for explicit rule violations and near-violations:
   - Millennium Prize problems with too-low `impact`
   - marquee / heavily studied problems with inflated `underexplored`
   - pure existence/topology problems with inflated `toolability`
   - vaguely scoped or bundled programs with inflated `formality`
   - suspiciously templated score bundles
4. Measured clustering / batch-generation signals:
   - exact duplicate 5D score vectors
   - entropy by dimension
   - nearest-neighbor L1 distance in score space
   - lattice usage (0.05-grid concentration)
   - correlation structure, especially `ai_fit`
5. Compared the original corpus vs the newer expansion.

### Cohort definition

The repository does **not** contain an explicit field that says which files are the original ~50 and which are the newer ~262. Git history also does not preserve a clean pre-expansion commit; all problem files arrived in the initial imported commit.

I therefore used the only concrete split available in the working tree: **file birth time** (`stat -f %B`). The largest timestamp discontinuity is a **630-second gap between files 50 and 51**, which aligns with the repo’s public “50+” claim in `README.md`. I use:

- **Original 50** = earliest 50 files by birth time
- **Newer 262** = remaining 262 files

This is an operational cohort split, not an explicit project-maintained label.

## Distribution statistics

### Overall distribution

| Dimension | Mean | Median | SD | Min | Q1 | Q3 | Max | Unique values | Mode (count) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| impact | 0.798 | 0.80 | 0.111 | 0.50 | 0.75 | 0.90 | 1.00 | 21 | 0.80 (51) |
| underexplored | 0.387 | 0.40 | 0.097 | 0.10 | 0.30 | 0.45 | 0.70 | 12 | 0.40 (70) |
| toolability | 0.394 | 0.40 | 0.141 | 0.15 | 0.30 | 0.50 | 0.85 | 15 | 0.40 (51) |
| formality | 0.805 | 0.85 | 0.103 | 0.40 | 0.80 | 0.85 | 0.95 | 11 | 0.85 (131) |
| ai_fit | 0.281 | 0.25 | 0.119 | 0.10 | 0.20 | 0.35 | 0.60 | 12 | 0.15 (57) |

### Immediate observations

- `impact` is centered tightly around **0.80**.
- `underexplored` is centered tightly around **0.35-0.40**.
- `formality` is highly concentrated near **0.85**:
  - **59.3%** of all files are within `0.05` of the modal value `0.85`
  - **82.1%** are within `0.10`
- The score vocabulary is coarse:
  - **100%** of `underexplored`, `toolability`, and `formality` values are on a **0.05 lattice**
  - `ai_fit` is on that same lattice for **311/312** files
  - `impact` is also mostly lattice-based, with only a few bespoke values (`0.68`, `0.72`, `0.78`, `0.82`, `0.87`, `0.88`, `0.92`, `0.93`, `0.98`, `0.99`)

## Sanity checks against the requested failure modes

- **Millennium Prize problems with impact < 0.9:** **none**
  - Present prize-tagged files: `p-vs-np`, `riemann-hypothesis`, `navier-stokes-existence-and-smoothness`, `birch-swinnerton-dyer-conjecture`, `yang-mills-existence-and-mass-gap`
  - Their impacts are `1.00`, `1.00`, `1.00`, `0.98`, `0.99`
- **Famous, heavily studied problems with underexplored > 0.5:** **yes**
  - several broad, marquee mathematical-physics programs are overstated on `underexplored`
- **Pure existence/topology problems with toolability > 0.7:** **none obvious after manual review**
  - the `> 0.7` toolability cases are almost all discrete/computational search problems in number theory or combinatorics
- **Vaguely stated problems with formality > 0.9:** **one strong case, plus two 0.90 near-misses**
- **Problems with all scores identical:** **none**
  - in fact, no file had all five scores equal, and no file used only one or two unique values across the five dimensions

## Clustering and templating analysis

### Exact vector duplication

- There are **281 unique 5D score vectors** across 312 files.
- **58 files (18.6%)** share an exact score vector with at least one other file.
- **55/262 newer files** and **3/50 original files** participate in those duplicated vectors.
- The original 50 have **0 original-to-original duplicate vectors**; the 3 original duplicates are only duplicated against later files.

Examples of duplicated vectors across unrelated topics:

| Count | Exact score vector `(impact, underexplored, toolability, formality, ai_fit)` | Example files |
|---:|---|---|
| 3 | `(0.85, 0.30, 0.20, 0.90, 0.15)` | `nexp-vs-bpp`, `bqp-vs-ph`, `hardness-vs-randomness` |
| 3 | `(0.80, 0.40, 0.25, 0.85, 0.15)` | `chromatic-splitting-conjecture`, `shelah-categoricity-conjecture`, `kadison-similarity-problem` |
| 3 | `(0.80, 0.40, 0.35, 0.85, 0.30)` | `dowling-wilson-conjecture`, `keating-snaith-conjecture`, `leray-conjecture` |
| 3 | `(0.90, 0.30, 0.25, 0.85, 0.15)` | `baum-connes-conjecture`, `abundance-conjecture`, `elliott-classification-conjecture` |
| 2 | `(0.92, 0.40, 0.30, 0.55, 0.20)` | `universality-critical-exponents-proof`, `topological-order-classification-general` |

This is not proof of bad calibration by itself, but it is strong evidence of **template scoring** rather than independent case-by-case judgment.

### Within-cohort nearest-neighbor compression

Using L1 distance in the 5D score space, measured **within each cohort**:

- **Original 50**
  - mean nearest-neighbor distance: **0.165**
  - median nearest-neighbor distance: **0.150**
  - exact-duplicate share: **0.0%**
- **Newer 262**
  - mean nearest-neighbor distance: **0.070**
  - median nearest-neighbor distance: **0.050**
  - exact-duplicate share: **19.85%**

Interpretation: the newer cohort sits much more tightly on a small set of score archetypes.

### Entropy shrinkage

| Dimension | Original entropy (bits) | Newer entropy (bits) | Original top 3 values | Newer top 3 values |
|---|---:|---:|---|---|
| impact | 4.016 | 3.496 | `(0.90, 6)`, `(0.88, 5)`, `(0.75, 4)` | `(0.80, 47)`, `(0.85, 39)`, `(0.90, 36)` |
| underexplored | 3.283 | 2.731 | `(0.35, 9)`, `(0.40, 9)`, `(0.25, 6)` | `(0.40, 61)`, `(0.35, 59)`, `(0.30, 50)` |
| toolability | 3.553 | 3.362 | `(0.40, 7)`, `(0.55, 6)`, `(0.30, 6)` | `(0.40, 44)`, `(0.30, 40)`, `(0.25, 38)` |
| formality | 2.610 | 2.524 | `(0.85, 16)`, `(0.90, 13)`, `(0.80, 8)` | `(0.85, 115)`, `(0.80, 46)`, `(0.90, 37)` |
| ai_fit | 3.251 | 3.083 | `(0.25, 9)`, `(0.35, 8)`, `(0.20, 6)` | `(0.15, 52)`, `(0.30, 44)`, `(0.25, 44)` |

The entropy drop is strongest for `impact` and `underexplored`, consistent with the newer cohort relying on fewer, repeated calibration bins.

### `ai_fit` is almost derived, not independently judged

Across the full dataset:

- Pearson correlation `toolability` vs `ai_fit`: **0.950**
- OLS `ai_fit ~ impact + underexplored + toolability + formality`: **R² = 0.918**

Interpretation: `ai_fit` behaves much more like a near-deterministic transform of the other dimensions, especially `toolability`, than like an independently calibrated label.

## Original 50 vs newer 262

### Domain composition

| Cohort | Mathematical physics | Mathematics | Theoretical CS |
|---|---:|---:|---:|
| Original 50 | 10 | 25 | 15 |
| Newer 262 | 50 | 142 | 70 |

### Between-cohort score shifts

| Dimension | Original 50 mean | Newer 262 mean | Δ (orig-new) | Mann-Whitney p | Levene p | Interpretation |
|---|---:|---:|---:|---:|---:|---|
| impact | 0.842 | 0.790 | +0.052 | 0.0011 | 0.3735 | newer set is lower-impact on average |
| underexplored | 0.342 | 0.395 | -0.053 | 0.0037 | 0.000085 | newer set is more “underexplored” and less variable |
| toolability | 0.438 | 0.386 | +0.052 | 0.0305 | 0.0367 | newer set is less toolable and more compressed |
| formality | 0.828 | 0.801 | +0.027 | 0.0104 | 0.8253 | newer set is slightly less formal |
| ai_fit | 0.311 | 0.276 | +0.036 | 0.0697 | 0.1909 | same direction, weaker evidence |

The newer cohort also uses a tighter score lattice:

- `impact` is on the 0.05 grid for **87.8%** of newer files vs **64.0%** of the original 50
- `ai_fit` is on the 0.05 grid for **100%** of newer files vs **98.0%** of the original 50
- `underexplored`, `toolability`, and `formality` are already fully 0.05-quantized in both cohorts

### Are those shifts only due to domain mix?

Not entirely.

Within-domain Mann-Whitney tests show the same directional pattern in multiple domains:

- **Mathematics**
  - `underexplored`: newer higher by **0.067** (`p = 0.021`)
  - `toolability`: newer lower by **0.088** (`p = 0.009`)
- **Theoretical CS**
  - `impact`: newer lower by **0.089** (`p = 0.00035`)
  - `underexplored`: newer higher by **0.055** (`p = 0.016`)
  - `formality`: newer lower by **0.048** (`p = 0.00027`)
- **Mathematical physics**
  - `impact`: newer lower by **0.082** (`p = 0.00047`)
  - `ai_fit`: newer lower by **0.080** (`p = 0.040`)

So the cohort shift is not just “more mathematics later”; there is a genuine calibration-style change.

## Miscalibrated scores (ALL file-level findings)

The table below is the complete set of file-level score corrections that were obvious enough to recommend confidently after a full pass through the 312 files. I intentionally did **not** inflate this list with borderline disagreements.

| File | Dimension | Current | Suggested | Reason |
|---|---|---:|---:|---|
| `data/problems/mathematical-physics/consistent-theory-of-quantum-gravity.yaml` | `underexplored` | 0.50 | 0.20 | Quantum gravity is one of the most heavily studied programs in modern theoretical physics; `0.50` misreads “hard and unsolved” as “neglected.” |
| `data/problems/mathematical-physics/yang-mills-existence-and-mass-gap.yaml` | `underexplored` | 0.40 | 0.20 | Millennium Prize problem with decades of concentrated attention; the field attention level is too high for `0.40`. |
| `data/problems/mathematical-physics/quantum-gravity-information-connections.yaml` | `underexplored` | 0.50 | 0.25 | ER=EPR / holography / QEC-in-spacetime is a major, crowded research theme, not a relatively neglected one. |
| `data/problems/mathematical-physics/classification-topological-phases-3d.yaml` | `underexplored` | 0.55 | 0.30 | The file itself describes this as a central modern condensed-matter problem with Nobel-era prominence and sustained literature; `0.55` is too high. |
| `data/problems/mathematical-physics/geometric-langlands-physics.yaml` | `underexplored` | 0.45 | 0.20 | Geometric Langlands via Kapustin-Witten is a major, highly visible program with substantial expert attention. |
| `data/problems/mathematical-physics/sle-conformal-invariance-3d-critical-phenomena.yaml` | `underexplored` | 0.70 | 0.35 | This is a famous frontier in probability / mathematical physics, not a neglected niche. `0.70` is the clearest `underexplored` overstatement in the dataset. |
| `data/problems/mathematical-physics/quantum-hamiltonian-complexity-qma.yaml` | `underexplored` | 0.45 | 0.25 | The alias is effectively “quantum PCP,” one of the flagship open problems in quantum complexity; it is heavily studied. |
| `data/problems/mathematics/large-cardinal-hierarchy.yaml` | `formality` | 0.95 | 0.70 | The statement bundles “construct an inner model for a supercompact cardinal” with a broader multi-part research program. That is important, but not a `0.95`-formal single conjecture. |
| `data/problems/theoretical-cs/natural-proofs-barrier.yaml` | `formality` | 0.90 | 0.70 | “Develop proof techniques that circumvent the barrier” is a meta-problem / research program, not a sharply formal yes/no statement. |
| `data/problems/theoretical-cs/hardness-vs-randomness.yaml` | `formality` | 0.90 | 0.80 | The file mixes one concrete converse question with a broader “more generally” program. It is fairly formal, but not as crisp as the 0.90–0.95 tier. |

## What I did **not** flag

- No prize problem had an obviously too-low `impact`.
- No clearly pure-existence / topology problem had an obviously too-high `toolability`.
- I did **not** flag coarse rounding alone as a file-level error. The 0.05 lattice is a dataset-level calibration concern, but not enough to justify a per-file correction without semantic evidence.
- I did **not** flag every duplicated vector as a miscalibration. Some duplicates could happen naturally; the duplication pattern is better treated as evidence of **process drift**.

## Overall calibration assessment

### Dimension-by-dimension

- **Impact:** mostly credible. The ranking of flagship problems is broadly sane.
- **Underexplored:** weakest dimension. It often confuses “hard / unsolved / broad” with “neglected.” This is the main place where semantic calibration breaks.
- **Toolability:** directionally decent. High values mostly land on computational number theory, combinatorics, or explicit search/optimization problems. I found no clear catastrophic overstatement.
- **Formality:** generally conservative, but broad research programs are sometimes scored like crisp conjectures.
- **AI fit:** useful as a rough derivative score, but too correlated with `toolability` to interpret as an independent judgment.

### Bottom line

This score system looks like a **two-stage calibration**:

1. an earlier, more hand-tuned 50-problem seed set with broader spread and no exact duplicate vectors;
2. a later 262-problem expansion with noticeably more templating, narrower spacing, fewer extremes, and repeated score bundles.

That does **not** make the dataset unusable. It does mean:

- the scores are good enough for broad faceting and rough filtering,
- but they are **not trustworthy enough for fine-grained ranking**, especially by `underexplored` or `ai_fit`,
- and the newer 262 should not be treated as calibrated on the same scale as the original 50 without a rescore pass.

## Recommendations

1. **Re-anchor `underexplored` with explicit examples.**
   - Example anchors:
   - `0.10`: Riemann / P vs NP / similarly saturated canonical problems
   - `0.20`: Yang-Mills, quantum PCP, major Langlands / topological-phase programs
   - `0.40+`: truly niche, high-importance problems with little active literature

2. **Separate “single conjecture” from “research program.”**
   - If a file says “more broadly,” “connections,” “structure,” “general,” “program,” or bundles multiple subquestions, cap `formality` unless the file is split into narrower problems.

3. **Decide whether `ai_fit` is a derived score or an expert score.**
   - If derived, document the formula and stop presenting it as independently judged metadata.
   - If expert-scored, recalibrate it separately from `toolability`.

4. **Add automated calibration checks in CI.**
   - Fail or warn on:
   - prize problems with low `impact`
   - flagship problems with high `underexplored`
   - broad/meta-problems with very high `formality`
   - exact duplicate score vectors across unrelated topics above a threshold
   - cohort drift metrics (entropy floor, nearest-neighbor distance, duplicate-vector share)

5. **Preserve provenance for scoring batches.**
   - Add fields such as `score_version`, `score_method`, `score_reviewer`, and `score_reviewed_at`.
   - Right now the repo does not preserve enough metadata to reconstruct why the original 50 and newer 262 differ.

6. **Run a manual rescore pass on the newer 262 before using scores for ranking products.**
   - Priority order:
   - `underexplored`
   - `formality`
   - `ai_fit`
