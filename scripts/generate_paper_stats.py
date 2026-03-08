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

    # Score distributions
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
