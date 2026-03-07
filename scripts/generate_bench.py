"""Generate OPA-Bench: a curated subset of problems suitable for AI attempts."""

import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROBLEMS_DIR = ROOT / "data" / "problems"
COLLECTIONS_DIR = ROOT / "data" / "collections"
CONTRACTS_DIR = ROOT / "verifiers" / "contracts"


def main():
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

        scored.append((bench_score, p))

    scored.sort(key=lambda x: -x[0])

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
    collection = {
        "id": "opa-bench-v1",
        "title": "OPA-Bench v1: AI Theorem Proving Benchmark",
        "description": (
            "A curated subset of 50 open problems selected for AI theorem proving "
            "evaluation. Every problem has a machine-verifiable contract."
        ),
        "version": "1.0.0",
        "problems": selected,
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


if __name__ == "__main__":
    main()
