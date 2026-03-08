"""OPA-Bench: curated benchmark subset for AI evaluation."""

import yaml
from pathlib import Path
from .atlas import get

_PACKAGE_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _PACKAGE_DIR.parent.parent
_COLLECTIONS_DIR = _PROJECT_ROOT / "data" / "collections"


def load_bench(version: str = "v1") -> list[dict]:
    """Load the OPA-Bench benchmark problem set.

    Args:
        version: Bench version (default "v1")

    Returns:
        List of full problem dicts in the benchmark.
        For v2+, each dict includes a ``_difficulty`` key (bronze/silver/gold).
    """
    bench_file = _COLLECTIONS_DIR / f"opa-bench-{version}.yaml"
    if not bench_file.exists():
        raise FileNotFoundError(f"OPA-Bench {version} not found at {bench_file}")

    with open(bench_file) as f:
        collection = yaml.safe_load(f)

    raw_problems = collection.get("problems", [])
    problems = []
    for entry in raw_problems:
        if isinstance(entry, str):
            # Legacy format: plain list of problem ID strings
            p = get(entry)
            if p:
                problems.append(p)
        elif isinstance(entry, dict):
            # Standard format: list of dicts with problem_id (and optional difficulty)
            pid = entry.get("problem_id", entry.get("id", ""))
            p = get(pid)
            if p:
                p = dict(p)  # copy to avoid mutating cache
                if "difficulty" in entry:
                    p["_difficulty"] = entry["difficulty"]
                problems.append(p)
    return problems
