"""Generate OPA-Bench: curated subsets of problems suitable for AI attempts."""

import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROBLEMS_DIR = ROOT / "data" / "problems"
COLLECTIONS_DIR = ROOT / "data" / "collections"
CONTRACTS_DIR = ROOT / "verifiers" / "contracts"


def _compute_bench_score(p: dict) -> int:
    """Compute a bench score for a problem based on verification profile and scores."""
    vp = p.get("verification_profile", {})
    scores = p.get("scores", {})

    bench_score = 0
    if vp.get("statement_precision") == "high":
        bench_score += 3
    elif vp.get("statement_precision") == "medium":
        bench_score += 1
    if vp.get("solution_checkability") in ("computational", "proof_assistant"):
        bench_score += 3
    elif vp.get("solution_checkability") == "mixed":
        bench_score += 1
    if vp.get("machine_actionability") == "high":
        bench_score += 3
    elif vp.get("machine_actionability") == "medium":
        bench_score += 1
    bench_score += scores.get("toolability", 0) * 2
    bench_score += scores.get("ai_fit", 0) * 2
    bench_score += scores.get("impact", 0)

    return bench_score


def _load_scored_problems() -> list[tuple[int, dict]]:
    """Load all problems, filter to those with contracts and open status, score them."""
    problems = []
    for f in sorted(PROBLEMS_DIR.rglob("*.yaml")):
        with open(f) as fh:
            data = yaml.safe_load(fh)
            if data and "id" in data:
                problems.append(data)

    contract_ids = set()
    for f in CONTRACTS_DIR.glob("*.yaml"):
        with open(f) as fh:
            data = yaml.safe_load(fh)
            if data:
                contract_ids.add(data.get("problem_id"))

    scored = []
    for p in problems:
        pid = p["id"]
        if pid not in contract_ids:
            continue
        if p.get("status", {}).get("label") != "open":
            continue
        bench_score = _compute_bench_score(p)
        scored.append((bench_score, p))

    scored.sort(key=lambda x: -x[0])
    return scored


def generate_v1(scored: list[tuple[int, dict]]) -> None:
    """Generate OPA-Bench v1: 50 problems, domain-balanced."""
    selected = []
    domain_counts = {"mathematics": 0, "theoretical-cs": 0, "mathematical-physics": 0}
    domain_limits = {"mathematics": 25, "theoretical-cs": 15, "mathematical-physics": 10}

    for score, p in scored:
        domain = p.get("domain", "mathematics")
        if domain_counts.get(domain, 0) < domain_limits.get(domain, 10):
            selected.append(p["id"])
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        if len(selected) >= 50:
            break

    COLLECTIONS_DIR.mkdir(parents=True, exist_ok=True)
    problems_list = [{"problem_id": pid} for pid in selected]
    collection = {
        "collection_id": "col_opa-bench-v1",
        "title": "OPA-Bench v1: AI Theorem Proving Benchmark",
        "description": (
            "A curated subset of 50 open problems selected for AI theorem proving "
            "evaluation. Every problem has a machine-verifiable contract."
        ),
        "version": "1.0.0",
        "problems": problems_list,
        "metadata": {
            "total": len(selected),
            "domains": dict(domain_counts),
            "selection_criteria": (
                "Ranked by statement precision, solution checkability, "
                "machine actionability, and AI fitness scores"
            ),
        },
    }

    out_path = COLLECTIONS_DIR / "opa-bench-v1.yaml"
    with open(out_path, "w") as f:
        yaml.dump(collection, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f"Selected {len(selected)} problems for OPA-Bench v1")
    for d, c in sorted(domain_counts.items()):
        print(f"  {d}: {c}")
    print(f"Saved to {out_path}")


def generate_v2(scored: list[tuple[int, dict]]) -> None:
    """Generate OPA-Bench v2: 100 problems with Bronze/Silver/Gold difficulty."""
    selected = []  # list of (bench_score, problem_id)
    domain_counts = {"mathematics": 0, "theoretical-cs": 0, "mathematical-physics": 0}
    domain_limits = {"mathematics": 50, "theoretical-cs": 30, "mathematical-physics": 20}

    for score, p in scored:
        domain = p.get("domain", "mathematics")
        if domain_counts.get(domain, 0) < domain_limits.get(domain, 20):
            selected.append((score, p["id"]))
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        if len(selected) >= 100:
            break

    # Assign difficulty based on bench_score tertiles.
    # sorted descending by score; top 33% = Bronze (most machine-tractable),
    # middle 33% = Silver, bottom 33% = Gold (hardest).
    n = len(selected)
    bronze_cutoff = n // 3
    silver_cutoff = 2 * n // 3

    problems_with_difficulty = []
    difficulty_counts = {"bronze": 0, "silver": 0, "gold": 0}
    for i, (score, pid) in enumerate(selected):
        if i < bronze_cutoff:
            difficulty = "bronze"
        elif i < silver_cutoff:
            difficulty = "silver"
        else:
            difficulty = "gold"
        problems_with_difficulty.append({"problem_id": pid, "difficulty": difficulty})
        difficulty_counts[difficulty] += 1

    COLLECTIONS_DIR.mkdir(parents=True, exist_ok=True)
    collection = {
        "collection_id": "col_opa-bench-v2",
        "title": "OPA-Bench v2: AI Theorem Proving Benchmark",
        "description": (
            "A curated set of 100 open problems with Bronze/Silver/Gold difficulty "
            "grading based on machine-tractability scores. Bronze problems are the "
            "most machine-tractable; Gold problems are the hardest."
        ),
        "version": "2.0.0",
        "problems": problems_with_difficulty,
        "metadata": {
            "total": len(selected),
            "domains": dict(domain_counts),
            "difficulty_distribution": dict(difficulty_counts),
            "selection_criteria": (
                "Top 100 open problems ranked by bench_score (statement precision, "
                "solution checkability, machine actionability, AI fitness). "
                "Difficulty assigned by tertile: Bronze (top 33%), Silver (middle 33%), "
                "Gold (bottom 33%)."
            ),
        },
    }

    out_path = COLLECTIONS_DIR / "opa-bench-v2.yaml"
    with open(out_path, "w") as f:
        yaml.dump(collection, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f"\nSelected {len(selected)} problems for OPA-Bench v2")
    for d, c in sorted(domain_counts.items()):
        print(f"  {d}: {c}")
    for diff, cnt in sorted(difficulty_counts.items()):
        print(f"  {diff}: {cnt}")
    print(f"Saved to {out_path}")


def main():
    scored = _load_scored_problems()
    generate_v1(scored)
    generate_v2(scored)


if __name__ == "__main__":
    main()
