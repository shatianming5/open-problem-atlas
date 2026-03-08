# Phase 2: Scale to 1000+ Problems Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Scale OpenProblemAtlas from 511 to 1000+ problems, expand checkers to 100+, add difficulty-graded OPA-Bench v2, create REST API and AI leaderboard, prepare arXiv paper statistics.

**Architecture:** Reuse existing scripts (promote_leads.py, generate_contracts.py, generate_bench.py) with adjusted parameters. Static JSON API already exists in build.py — enhance with CORS headers and proper structure. Leaderboard is a new Jinja2 template integrated into the existing site build pipeline.

**Tech Stack:** Python 3, PyYAML, Jinja2, pytest, HuggingFace Hub

---

## Current State (Post Phase 1)

| Metric | Value |
|--------|-------|
| Verified problems | 511 (math: 229, TCS: 117, physics: 165) |
| Remaining leads | 944 (≥0.7 conf: 247, 0.5-0.69: 526, 0.3-0.49: 171) |
| Verification contracts | 511 |
| Python checkers | 50 |
| AI attempt records | 3 |
| OPA-Bench | v1, 50 problems, no difficulty levels |

## Task Dependency Graph

```
Task 1 (promote leads) → Task 2 (contracts) → Task 3 (checkers, parallel-safe)
                                              → Task 5 (OPA-Bench v2)
Task 4 (leaderboard) — independent
Task 6 (REST API enhancement) — depends on Task 1,2
Task 7 (arXiv stats) — depends on Task 1,2,3
Task 8 (HuggingFace republish) — depends on all above
```

---

### Task 1: Promote Remaining Leads to 1000+ Problems

**Files:**
- Modify: `scripts/promote_leads.py:20` (lower threshold)
- Output: ~500 new YAML files in `data/problems/{mathematics,theoretical-cs,mathematical-physics}/`
- Test: `tests/test_schema_validation.py`

**Step 1: Lower confidence threshold and run promotion**

Change `CONFIDENCE_THRESHOLD = 0.7` to `CONFIDENCE_THRESHOLD = 0.5` in `scripts/promote_leads.py:20`, then run:

```bash
python scripts/promote_leads.py
```

Expected: ~500+ new problems promoted (the 526 leads with confidence 0.5-0.69 minus duplicates).

**Step 2: Verify all new problems pass schema validation**

```bash
python -m pytest tests/test_schema_validation.py -v
```

Expected: All PASS. Total problems should be ~1000+.

**Step 3: Count and verify**

```bash
find data/problems -name "*.yaml" | wc -l
```

Expected: 1000+ files.

**Step 4: Commit**

```bash
git add data/problems/ scripts/promote_leads.py
git commit -m "feat: scale to 1000+ problems by promoting 0.5+ confidence leads"
```

---

### Task 2: Generate Contracts for All New Problems

**Files:**
- Run: `scripts/generate_contracts.py`
- Output: ~500 new YAML files in `verifiers/contracts/`
- Test: `tests/test_contracts_coverage.py`

**Step 1: Run contract generation**

```bash
python scripts/generate_contracts.py
```

Expected: ~500 new contracts generated, 0 errors.

**Step 2: Verify 100% coverage**

```bash
python -m pytest tests/test_contracts_coverage.py -v
```

Expected: All 3 tests PASS — every problem has a contract, all contracts valid, all IDs match.

**Step 3: Commit**

```bash
git add verifiers/contracts/
git commit -m "feat: generate verification contracts for all 1000+ problems"
```

---

### Task 3: Expand Python Checkers to 100+

**Files:**
- Create: 50+ new files in `verifiers/checkers/math/`
- Test: `tests/test_checkers.py`

**Context:** Each checker is a Python file with a `verify(params: dict) -> dict` function that returns `{"status": "pass"|"fail", "summary": str, "details": dict}`. Checkers do finite verification of conjectures (e.g., checking Collatz for first N numbers).

**Checker categories to cover (50 new):**

**Number Theory (15):**
- `goldbach_checker.py` — verify even numbers 4..N are sum of two primes
- `cramers_checker.py` — check Cramér's conjecture gaps for primes up to N
- `hardy_littlewood_checker.py` — verify k-tuple conjecture for small cases
- `schanuel_checker.py` — check algebraic independence of exp values
- `artins_checker.py` — check primitive root conjecture for primes
- `grimms_checker.py` — verify Grimm's conjecture for consecutive composites
- `gilbreaths_checker.py` — check Gilbreath's conjecture on prime differences
- `sierpinski_number_checker.py` — verify known Sierpinski numbers
- `selfridges_checker.py` — check Selfridge's conjecture
- `singmasters_checker.py` — search for high-multiplicity binomial values
- `erdos_straus_extended_checker.py` — verify 4/n = 1/a+1/b+1/c for range
- `lehmer_checker.py` — check Lehmer's conjecture on Mahler measure
- `waring_exact_checker.py` — verify g(k) values for small k
- `abc_effective_checker.py` — check ABC triples with large quality
- `keating_snaith_checker.py` — verify moment conjecture numerics

**Combinatorics (15):**
- `hadamard_checker.py` — search for Hadamard matrices of given orders
- `ramsey_r55_checker.py` — verify lower/upper bounds for R(5,5)
- `graceful_tree_extended_checker.py` — verify graceful labeling for more tree types
- `frankl_specific_checker.py` — check Frankl's conjecture for specific family sizes
- `ringel_checker.py` — verify Ringel's conjecture for small complete graphs
- `erdos_hajnal_checker.py` — check Erdős-Hajnal for small tournaments
- `gyarfas_sumner_checker.py` — verify Gyárfás-Sumner for specific trees
- `list_coloring_checker.py` — check list coloring conjecture for small graphs
- `total_coloring_checker.py` — verify total coloring conjecture small cases
- `overfull_checker.py` — check overfull conjecture for multigraphs
- `rysers_checker.py` — verify Ryser's conjecture for small Latin squares
- `cerny_checker.py` — check Černý conjecture for small automata
- `rotas_basis_checker.py` — verify Rota's basis conjecture small cases
- `zarankiewicz_checker.py` — compute z(m,n;s,t) for small params
- `halpern_lauchli_checker.py` — verify partition theorem for small trees

**Geometry/Analysis/Algebra (10):**
- `hadwiger_nelson_extended_checker.py` — chromatic number bounds with unit distance
- `borsuk_checker.py` — verify Borsuk partition for small dimensions
- `bellman_forest_extended_checker.py` — optimize search paths
- `invariant_subspace_checker.py` — check specific operator classes
- `jacobian_checker.py` — verify Jacobian conjecture for low degree
- `sendov_checker.py` — check Sendov's conjecture for degree n polynomials
- `pierce_birkhoff_checker.py` — verify for small variable count
- `casas_alvero_checker.py` — check Casas-Alvero for specific degrees
- `neggers_stanley_checker.py` — verify for small posets
- `kls_checker.py` — KLS conjecture numerical check

**TCS/Physics (10):**
- `matrix_multiplication_checker.py` — verify tensor rank bounds
- `sorting_network_checker.py` — optimal depth for small n
- `rectilinear_steiner_checker.py` — check Steiner ratio bounds
- `online_matching_checker.py` — verify competitive ratio bounds
- `secretary_problem_checker.py` — optimal stopping verification
- `percolation_threshold_checker.py` — verify pc for lattice types
- `self_avoiding_walk_checker.py` — connective constant bounds
- `random_matrix_checker.py` — GOE/GUE spacing statistics
- `kpz_checker.py` — KPZ universality exponent checks
- `spin_glass_checker.py` — Parisi formula verification for small instances

**Step 1: Write all 50 checker files**

Each checker follows this template:
```python
"""<Problem> verifier.

<1-2 sentence description of what this checks.>
"""

def verify(params: dict) -> dict:
    max_n = int(params.get("max_n", <default>))
    max_n = min(max_n, <hard_cap>)  # safety cap

    # ... verification logic ...

    if violations:
        return {
            "status": "fail",
            "summary": f"<Problem> violated: {len(violations)} case(s)",
            "details": {"max_n": max_n, "violations": violations[:10]},
        }
    return {
        "status": "pass",
        "summary": f"<Problem> verified for n in [<range>]. Checked {count} cases.",
        "details": {"max_n": max_n, "total_checked": count},
    }

if __name__ == "__main__":
    import json
    print(json.dumps(verify({}), indent=2))
```

**Step 2: Run checker tests**

```bash
python -m pytest tests/test_checkers.py -v --timeout=120
```

Expected: All 100 checkers importable, all return valid format. Each should complete within 60s with default params.

**Step 3: Commit**

```bash
git add verifiers/checkers/math/
git commit -m "feat: expand checkers from 50 to 100+"
```

---

### Task 4: Create AI Leaderboard Page

**Files:**
- Create: `site/app/templates/leaderboard.html`
- Modify: `site/build/build.py` (add leaderboard build step)
- Modify: `site/app/templates/base.html` (add nav link)

**Step 1: Create leaderboard template**

Create `site/app/templates/leaderboard.html`:

```html
{% extends "base.html" %}
{% set page = 'leaderboard' %}
{% block title %}Leaderboard — OpenProblemAtlas{% endblock %}

{% block content %}
<div class="container" style="padding-top: 32px;">
  <h1 style="font-size: 28px; margin-bottom: 8px;">AI Leaderboard</h1>
  <p style="color: var(--text-muted); margin-bottom: 24px;">
    Tracking AI systems' attempts on open problems from OPA-Bench.
  </p>

  <!-- Summary stats -->
  <div class="stats-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 32px;">
    <div class="stat-card" style="background: var(--bg-secondary); padding: 20px; border-radius: var(--radius);">
      <div style="font-size: 28px; font-weight: bold; color: var(--accent);">{{ leaderboard_stats.total_attempts }}</div>
      <div style="font-size: 13px; color: var(--text-muted);">Total Attempts</div>
    </div>
    <div class="stat-card" style="background: var(--bg-secondary); padding: 20px; border-radius: var(--radius);">
      <div style="font-size: 28px; font-weight: bold; color: var(--accent);">{{ leaderboard_stats.unique_models }}</div>
      <div style="font-size: 13px; color: var(--text-muted);">AI Systems</div>
    </div>
    <div class="stat-card" style="background: var(--bg-secondary); padding: 20px; border-radius: var(--radius);">
      <div style="font-size: 28px; font-weight: bold; color: var(--accent);">{{ leaderboard_stats.problems_attempted }}</div>
      <div style="font-size: 13px; color: var(--text-muted);">Problems Attempted</div>
    </div>
    <div class="stat-card" style="background: var(--bg-secondary); padding: 20px; border-radius: var(--radius);">
      <div style="font-size: 28px; font-weight: bold; color: var(--accent);">{{ leaderboard_stats.verified_results }}</div>
      <div style="font-size: 13px; color: var(--text-muted);">Verified Results</div>
    </div>
  </div>

  <!-- Leaderboard table -->
  <h2 style="font-size: 20px; margin-bottom: 16px;">By AI System</h2>
  <div style="overflow-x: auto;">
    <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
      <thead>
        <tr style="border-bottom: 2px solid var(--border); text-align: left;">
          <th style="padding: 12px 8px;">Rank</th>
          <th style="padding: 12px 8px;">System</th>
          <th style="padding: 12px 8px;">Attempts</th>
          <th style="padding: 12px 8px;">Partial Progress</th>
          <th style="padding: 12px 8px;">Verified</th>
          <th style="padding: 12px 8px;">Best Result</th>
        </tr>
      </thead>
      <tbody>
        {% for entry in leaderboard %}
        <tr style="border-bottom: 1px solid var(--border);">
          <td style="padding: 12px 8px; color: var(--text-muted);">{{ loop.index }}</td>
          <td style="padding: 12px 8px; font-weight: 500;">{{ entry.system }}</td>
          <td style="padding: 12px 8px;">{{ entry.attempts }}</td>
          <td style="padding: 12px 8px;">{{ entry.partial }}</td>
          <td style="padding: 12px 8px;">{{ entry.verified }}</td>
          <td style="padding: 12px 8px;">
            {% if entry.best_result %}
            <a href="/problem/{{ entry.best_problem_slug }}.html" style="color: var(--accent);">{{ entry.best_result }}</a>
            {% else %}
            <span style="color: var(--text-muted);">—</span>
            {% endif %}
          </td>
        </tr>
        {% endfor %}
        {% if leaderboard | length == 0 %}
        <tr>
          <td colspan="6" style="padding: 32px; text-align: center; color: var(--text-muted);">
            No attempts recorded yet. Submit yours via the <a href="https://github.com/OpenProblemAtlas/open-problem-atlas/issues/new" style="color: var(--accent);">issue form</a>.
          </td>
        </tr>
        {% endif %}
      </tbody>
    </table>
  </div>

  <!-- Recent attempts -->
  <h2 style="font-size: 20px; margin-top: 32px; margin-bottom: 16px;">Recent Attempts</h2>
  <div class="problem-list">
    {% for att in recent_attempts[:10] %}
    <div class="problem-card">
      <div style="display: flex; justify-content: space-between; align-items: flex-start;">
        <div class="title">
          <a href="/problem/{{ att.problem_id | replace('.', '-') }}.html" style="color: var(--accent);">{{ att.problem_title | default(att.problem_id) }}</a>
        </div>
        <span style="color: var(--text-muted); font-size: 13px;">{{ att.date | default('') }}</span>
      </div>
      <div class="meta" style="margin-top: 8px;">
        <span>{{ att.actor | default('Unknown') }}</span>
        <span class="tag tag-domain">{{ att.model | default('') }}</span>
        <span class="tag {% if att.verification_status == 'verified' %}tag-open{% else %}tag-type{% endif %}">{{ att.verification_status | default('pending') }}</span>
      </div>
      {% if att.method_summary %}
      <div style="margin-top: 8px; font-size: 14px; color: var(--text-muted);">{{ att.method_summary }}</div>
      {% endif %}
    </div>
    {% endfor %}
  </div>
</div>
{% endblock %}
```

**Step 2: Add leaderboard build logic to build.py**

In `site/build/build.py`, add after the attempts page build (~line 285):

```python
# Build leaderboard
def build_leaderboard(attempts):
    """Aggregate attempts by AI system for leaderboard."""
    systems = {}
    for att in attempts:
        model = att.get("model", att.get("actor", "Unknown"))
        if model not in systems:
            systems[model] = {"system": model, "attempts": 0, "partial": 0, "verified": 0, "best_result": None, "best_problem_slug": ""}
        systems[model]["attempts"] += 1
        if att.get("result_type") == "partial":
            systems[model]["partial"] += 1
        if att.get("verification_status") == "verified":
            systems[model]["verified"] += 1
        if att.get("result_type") in ("proof", "partial") and not systems[model]["best_result"]:
            systems[model]["best_result"] = att.get("result_type", "")
            systems[model]["best_problem_slug"] = att.get("problem_id", "").replace(".", "-")
    ranked = sorted(systems.values(), key=lambda x: (x["verified"], x["partial"], x["attempts"]), reverse=True)
    return ranked

leaderboard = build_leaderboard(attempts)
leaderboard_stats = {
    "total_attempts": len(attempts),
    "unique_models": len(set(a.get("model", a.get("actor", "")) for a in attempts)),
    "problems_attempted": len(set(a.get("problem_id", "") for a in attempts)),
    "verified_results": sum(1 for a in attempts if a.get("verification_status") == "verified"),
}

template = env.get_template("leaderboard.html")
(OUTPUT_DIR / "leaderboard.html").write_text(template.render(
    leaderboard=leaderboard,
    leaderboard_stats=leaderboard_stats,
    recent_attempts=attempts,
))
```

**Step 3: Add nav link in base.html**

Find the nav section in `site/app/templates/base.html` and add leaderboard link.

**Step 4: Test build**

```bash
python site/build/build.py
```

Expected: Site builds successfully, `site/build/output/leaderboard.html` exists.

**Step 5: Commit**

```bash
git add site/
git commit -m "feat: add AI leaderboard page to static site"
```

---

### Task 5: OPA-Bench v2 with Difficulty Levels

**Files:**
- Modify: `scripts/generate_bench.py`
- Create: `data/collections/opa-bench-v2.yaml`
- Modify: `src/opa/bench.py` (support v2)
- Test: `tests/test_opa_package.py`

**Step 1: Update generate_bench.py to support v2**

Add difficulty grading logic based on:
- **Bronze** (easiest): high machine_actionability + computational checkability + high toolability
- **Silver** (medium): medium precision + mixed checkability
- **Gold** (hardest): high impact + low machine_actionability + expert_review

Score thresholds:
- Top 33% of bench_score → Bronze (most machine-tractable)
- Middle 33% → Silver
- Bottom 33% → Gold (hardest, most theoretical)

Generate 100 problems (up from 50), balanced: 50 math, 30 TCS, 20 physics.

```python
# In generate_bench.py, add v2 generation after v1:

def assign_difficulty(score, thresholds):
    if score >= thresholds["bronze"]:
        return "bronze"
    elif score >= thresholds["silver"]:
        return "silver"
    return "gold"

# ... select 100 problems with new domain limits ...
# domain_limits_v2 = {"mathematics": 50, "theoretical-cs": 30, "mathematical-physics": 20}
# For each selected problem, assign difficulty based on bench_score percentile
```

**Step 2: Update bench.py to return difficulty metadata**

```python
def load_bench(version: str = "v1") -> list[dict]:
    # ... existing code ...
    # For v2, also attach difficulty level from collection metadata
```

**Step 3: Run generation**

```bash
python scripts/generate_bench.py
```

Expected: Both v1 (50 problems) and v2 (100 problems with difficulty) generated.

**Step 4: Run tests**

```bash
python -m pytest tests/test_opa_package.py -v
```

**Step 5: Commit**

```bash
git add scripts/generate_bench.py data/collections/ src/opa/bench.py tests/
git commit -m "feat: add OPA-Bench v2 with 100 problems and Bronze/Silver/Gold difficulty"
```

---

### Task 6: Enhance REST API

**Files:**
- Modify: `site/build/build.py` (enhance API output)
- Create: `site/build/output/api/v1/` structure

**Step 1: Enhance the static JSON API in build.py**

Add versioned API structure and per-problem endpoints:

```python
# In build.py, replace the existing API section:
api_v1 = OUTPUT_DIR / "api" / "v1"
api_v1.mkdir(parents=True)

# Full problem list with pagination metadata
with open(api_v1 / "problems.json", "w") as f:
    json.dump({
        "total": len(problems),
        "problems": problems,
    }, f, indent=2, ensure_ascii=False)

# Per-domain endpoints
for domain in ["mathematics", "theoretical-cs", "mathematical-physics"]:
    domain_problems = [p for p in problems if p.get("domain") == domain]
    with open(api_v1 / f"problems-{domain}.json", "w") as f:
        json.dump({"total": len(domain_problems), "problems": domain_problems}, f, indent=2, ensure_ascii=False)

# Stats endpoint
with open(api_v1 / "stats.json", "w") as f:
    json.dump(stats, f, indent=2, ensure_ascii=False)

# Collections endpoint
with open(api_v1 / "collections.json", "w") as f:
    json.dump(collections, f, indent=2, ensure_ascii=False)

# Attempts endpoint
with open(api_v1 / "attempts.json", "w") as f:
    json.dump(attempts, f, indent=2, ensure_ascii=False)

# Bench endpoint (v1 + v2)
for bench_file in (DATA_DIR / "collections").glob("opa-bench-*.yaml"):
    with open(bench_file) as bf:
        bench_data = yaml.safe_load(bf)
    bench_name = bench_file.stem
    with open(api_v1 / f"{bench_name}.json", "w") as f:
        json.dump(bench_data, f, indent=2, ensure_ascii=False)
```

**Step 2: Keep backward-compatible /api/ endpoints**

Keep existing `/api/problems.json` etc. as-is for backward compatibility.

**Step 3: Test build**

```bash
python site/build/build.py
ls site/build/output/api/v1/
```

Expected: `problems.json`, `problems-mathematics.json`, `problems-theoretical-cs.json`, `problems-mathematical-physics.json`, `stats.json`, `collections.json`, `attempts.json`, `opa-bench-v1.json`, `opa-bench-v2.json`

**Step 4: Commit**

```bash
git add site/
git commit -m "feat: add versioned REST API (v1) with per-domain and bench endpoints"
```

---

### Task 7: Generate arXiv Paper Statistics

**Files:**
- Create: `scripts/generate_paper_stats.py`
- Output: `analysis/paper-statistics.json`

**Step 1: Write statistics generator**

```python
#!/usr/bin/env python3
"""Generate statistics for the arXiv paper."""

import json
import yaml
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
PROBLEMS_DIR = ROOT / "data" / "problems"
CONTRACTS_DIR = ROOT / "verifiers" / "contracts"
CHECKERS_DIR = ROOT / "verifiers" / "checkers" / "math"
LEADS_DIR = ROOT / "data" / "leads"
ATTEMPTS_DIR = ROOT / "data" / "attempts"
COLLECTIONS_DIR = ROOT / "data" / "collections"


def main():
    # Load all problems
    problems = []
    for f in sorted(PROBLEMS_DIR.rglob("*.yaml")):
        with open(f) as fh:
            d = yaml.safe_load(fh)
            if d and "id" in d:
                problems.append(d)

    # Domain distribution
    domains = Counter(p.get("domain", "unknown") for p in problems)

    # Tier distribution
    tiers = Counter(p.get("tier", "unknown") for p in problems)

    # Status distribution
    statuses = Counter(p.get("status", {}).get("label", "unknown") for p in problems)

    # Verification profile stats
    precision = Counter(p.get("verification_profile", {}).get("statement_precision", "unknown") for p in problems)
    checkability = Counter(p.get("verification_profile", {}).get("solution_checkability", "unknown") for p in problems)
    actionability = Counter(p.get("verification_profile", {}).get("machine_actionability", "unknown") for p in problems)

    # Problem type distribution
    problem_types = Counter(p.get("problem_type", "unknown") for p in problems)

    # Score distributions (mean, median, std)
    score_fields = ["impact", "underexplored", "toolability", "formality", "ai_fit"]
    score_stats = {}
    for field in score_fields:
        values = [p.get("scores", {}).get(field, 0) for p in problems if p.get("scores", {}).get(field) is not None]
        if values:
            mean = sum(values) / len(values)
            sorted_v = sorted(values)
            median = sorted_v[len(sorted_v) // 2]
            score_stats[field] = {"mean": round(mean, 3), "median": median, "count": len(values)}

    # Subdomain distribution (top 20)
    all_subs = []
    for p in problems:
        all_subs.extend(p.get("subdomains", []))
    subdomain_counts = Counter(all_subs).most_common(20)

    # Contract stats
    contracts = list(CONTRACTS_DIR.glob("*.yaml")) if CONTRACTS_DIR.exists() else []
    contract_backends = Counter()
    contract_task_types = Counter()
    for cf in contracts:
        with open(cf) as fh:
            cd = yaml.safe_load(fh)
            if cd:
                contract_backends[cd.get("backend", "unknown")] += 1
                contract_task_types[cd.get("task_type", "unknown")] += 1

    # Checker count
    checkers = list(CHECKERS_DIR.glob("*.py")) if CHECKERS_DIR.exists() else []

    # Leads count
    leads = list(LEADS_DIR.glob("*.yaml")) if LEADS_DIR.exists() else []

    # Attempts count
    attempts = list(ATTEMPTS_DIR.glob("*.yaml")) if ATTEMPTS_DIR.exists() else []

    stats = {
        "total_problems": len(problems),
        "total_contracts": len(contracts),
        "total_checkers": len(checkers),
        "total_leads": len(leads),
        "total_attempts": len(attempts),
        "domains": dict(domains),
        "tiers": dict(tiers),
        "statuses": dict(statuses),
        "statement_precision": dict(precision),
        "solution_checkability": dict(checkability),
        "machine_actionability": dict(actionability),
        "problem_types": dict(problem_types),
        "score_distributions": score_stats,
        "top_subdomains": subdomain_counts,
        "contract_backends": dict(contract_backends),
        "contract_task_types": dict(contract_task_types),
    }

    out_dir = ROOT / "analysis"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "paper-statistics.json"
    with open(out_path, "w") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(json.dumps(stats, indent=2))
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
```

**Step 2: Run and verify**

```bash
python scripts/generate_paper_stats.py
```

Expected: JSON output with all statistics, saved to `analysis/paper-statistics.json`.

**Step 3: Commit**

```bash
git add scripts/generate_paper_stats.py analysis/paper-statistics.json
git commit -m "feat: add arXiv paper statistics generator"
```

---

### Task 8: Republish HuggingFace Dataset

**Files:**
- Run: `scripts/publish_huggingface.py`

**Step 1: Regenerate snapshots and upload**

```bash
python scripts/publish_huggingface.py
```

Expected: 1000+ problems exported to Parquet, uploaded to `Tommysha/open-problem-atlas`.

**Step 2: Update README badges**

In `README.md`, update badge from `500%2B` to `1000%2B`:

```markdown
[![Problems](https://img.shields.io/badge/problems-1000%2B-orange.svg)](data/problems/)
[![Checkers](https://img.shields.io/badge/checkers-100-brightgreen.svg)](verifiers/checkers/)
[![OPA-Bench](https://img.shields.io/badge/OPA--Bench-100%20problems-purple.svg)](data/collections/opa-bench-v2.yaml)
```

**Step 3: Commit**

```bash
git add README.md data/snapshots/
git commit -m "feat: update HuggingFace dataset to 1000+ problems, update badges"
```

---

## Success Criteria

| Metric | Phase 1 (done) | Phase 2 Target |
|--------|----------------|----------------|
| Verified problems | 511 | 1000+ |
| Verification contracts | 511 | 1000+ |
| Python checkers | 50 | 100+ |
| OPA-Bench problems | 50 | 100 (with difficulty) |
| AI leaderboard | none | live page |
| REST API | basic JSON | versioned v1 API |
| arXiv stats | none | generated |
| HuggingFace dataset | 511 problems | 1000+ problems |
