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
    """
    bench_file = _COLLECTIONS_DIR / f"opa-bench-{version}.yaml"
    if not bench_file.exists():
        raise FileNotFoundError(f"OPA-Bench {version} not found at {bench_file}")

    with open(bench_file) as f:
        collection = yaml.safe_load(f)

    problem_ids = collection.get("problems", [])
    problems = []
    for pid in problem_ids:
        p = get(pid)
        if p:
            problems.append(p)
    return problems
