"""Select contracts for batch runs by tier, backend, or domain."""

import yaml

from ..config import PROBLEMS_DIR
from ..contract import load_all_contracts


def _load_problem(problem_id: str) -> dict | None:
    """Load a problem YAML by its ID."""
    for yaml_file in PROBLEMS_DIR.rglob("*.yaml"):
        with open(yaml_file) as f:
            data = yaml.safe_load(f)
        if data and data.get("id") == problem_id:
            return data
    return None


def select_contracts(
    backend: str | None = None,
    tier: str | None = None,
    domain: str | None = None,
    task_type: str | None = None,
    limit: int | None = None,
) -> list[dict]:
    """Filter contracts by criteria, optionally enriched with problem data."""
    contracts = load_all_contracts()

    if backend:
        contracts = [c for c in contracts if c["backend"] == backend]

    if task_type:
        contracts = [c for c in contracts if c["task_type"] == task_type]

    if tier or domain:
        filtered = []
        for c in contracts:
            problem = _load_problem(c["problem_id"])
            if problem is None:
                continue
            if tier and problem.get("tier") != tier:
                continue
            if domain and problem.get("domain") != domain:
                continue
            filtered.append(c)
        contracts = filtered

    if limit:
        contracts = contracts[:limit]

    return contracts
