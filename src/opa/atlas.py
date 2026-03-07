"""Load and query open problems from the OpenProblemAtlas dataset."""

import yaml
from pathlib import Path
from functools import lru_cache

_PACKAGE_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _PACKAGE_DIR.parent.parent
_PROBLEMS_DIR = _PROJECT_ROOT / "data" / "problems"


@lru_cache(maxsize=1)
def _load_all() -> tuple:
    """Load all problems from YAML files. Returns tuple for cacheability."""
    problems = []
    if not _PROBLEMS_DIR.exists():
        return tuple()
    for yaml_file in sorted(_PROBLEMS_DIR.rglob("*.yaml")):
        with open(yaml_file) as f:
            data = yaml.safe_load(f)
            if data and isinstance(data, dict) and "id" in data:
                problems.append(data)
    return tuple(problems)


def load(
    domain: str | None = None,
    status: str | None = None,
    tier: str | None = None,
    problem_type: str | None = None,
) -> list[dict]:
    """Load problems with optional filters.

    Args:
        domain: Filter by domain (mathematics, theoretical-cs, mathematical-physics)
        status: Filter by status label (open, solved, partially_solved, etc.)
        tier: Filter by tier (tier_1, tier_2, tier_3)
        problem_type: Filter by problem type (conjecture, existence, etc.)

    Returns:
        List of problem dicts matching all filters.
    """
    problems = list(_load_all())
    if domain:
        problems = [p for p in problems if p.get("domain") == domain]
    if status:
        problems = [p for p in problems if p.get("status", {}).get("label") == status]
    if tier:
        problems = [p for p in problems if p.get("tier") == tier]
    if problem_type:
        problems = [p for p in problems if p.get("problem_type") == problem_type]
    return problems


def get(problem_id: str) -> dict | None:
    """Get a single problem by its full ID."""
    for p in _load_all():
        if p.get("id") == problem_id:
            return p
    return None


def search(query: str) -> list[dict]:
    """Search problems by title or statement text."""
    query_lower = query.lower()
    results = []
    for p in _load_all():
        title = p.get("title", "").lower()
        statement = p.get("statement", {}).get("canonical", "").lower()
        informal = p.get("statement", {}).get("informal", "").lower()
        if query_lower in title or query_lower in statement or query_lower in informal:
            results.append(p)
    return results


def list_domains() -> list[str]:
    """List all unique domains."""
    return sorted(set(p.get("domain", "") for p in _load_all()))


def list_subdomains(domain: str | None = None) -> list[str]:
    """List all unique subdomains, optionally filtered by domain."""
    problems = list(_load_all())
    if domain:
        problems = [p for p in problems if p.get("domain") == domain]
    subs = set()
    for p in problems:
        for sd in p.get("subdomains", []):
            subs.add(sd)
    return sorted(subs)


def stats() -> dict:
    """Get summary statistics about the atlas."""
    problems = list(_load_all())
    domains = {}
    tiers = {"tier_1": 0, "tier_2": 0, "tier_3": 0}
    statuses = {}

    for p in problems:
        d = p.get("domain", "unknown")
        domains[d] = domains.get(d, 0) + 1
        t = p.get("tier", "tier_3")
        tiers[t] = tiers.get(t, 0) + 1
        s = p.get("status", {}).get("label", "unknown")
        statuses[s] = statuses.get(s, 0) + 1

    return {
        "total": len(problems),
        "domains": domains,
        "tiers": tiers,
        "statuses": statuses,
    }
