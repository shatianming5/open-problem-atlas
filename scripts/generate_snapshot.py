#!/usr/bin/env python3
"""Generate a snapshot of all problem data as JSON (and optionally Parquet).

Reads every YAML file under ``data/problems/`` and writes:
- ``data/snapshots/<date>/problems.json``
- ``data/snapshots/<date>/problems.parquet``  (if pyarrow is available)

Usage::

    python scripts/generate_snapshot.py            # uses today's date
    python scripts/generate_snapshot.py 2026-03-07  # explicit date
"""

import json
import os
import sys
from datetime import date
from pathlib import Path

import yaml


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROBLEMS_DIR = PROJECT_ROOT / "data" / "problems"
SNAPSHOTS_DIR = PROJECT_ROOT / "data" / "snapshots"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_problems() -> list[dict]:
    """Walk ``data/problems/`` and load every YAML file."""
    problems: list[dict] = []
    for root, _dirs, files in os.walk(PROBLEMS_DIR):
        for fname in sorted(files):
            if not fname.endswith((".yaml", ".yml")):
                continue
            path = Path(root) / fname
            with open(path, "r", encoding="utf-8") as f:
                doc = yaml.safe_load(f)
            if doc:
                # Attach the relative source path for traceability.
                doc["_source_path"] = str(path.relative_to(PROJECT_ROOT))
                problems.append(doc)
    return problems


def _write_json(problems: list[dict], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(problems, f, ensure_ascii=False, indent=2, default=str)
    print(f"  JSON -> {out_path}  ({out_path.stat().st_size:,} bytes)")


def _write_parquet(problems: list[dict], out_path: Path) -> bool:
    """Attempt to write a Parquet file.  Returns True on success."""
    try:
        import pyarrow as pa       # noqa: F811
        import pyarrow.parquet as pq  # noqa: F811
    except ImportError:
        print("  Parquet skipped (pyarrow not installed). "
              "Install with: pip install 'open-problem-atlas[snapshot]'")
        return False

    # Flatten nested dicts to JSON strings for Parquet compatibility.
    flat_rows: list[dict] = []
    for p in problems:
        row: dict = {}
        for k, v in p.items():
            if isinstance(v, (dict, list)):
                row[k] = json.dumps(v, ensure_ascii=False, default=str)
            else:
                row[k] = v
        flat_rows.append(row)

    table = pa.Table.from_pylist(flat_rows)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, str(out_path))
    print(f"  Parquet -> {out_path}  ({out_path.stat().st_size:,} bytes)")
    return True


def _print_stats(problems: list[dict]) -> None:
    """Print summary statistics to stdout."""
    domains: dict[str, int] = {}
    statuses: dict[str, int] = {}
    for p in problems:
        d = p.get("domain", "unknown")
        domains[d] = domains.get(d, 0) + 1
        s = p.get("status", {})
        label = s.get("label", "unknown") if isinstance(s, dict) else "unknown"
        statuses[label] = statuses.get(label, 0) + 1

    print(f"\n  Total problems: {len(problems)}")
    print("  By domain:")
    for d, n in sorted(domains.items()):
        print(f"    {d}: {n}")
    print("  By status:")
    for s, n in sorted(statuses.items()):
        print(f"    {s}: {n}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    snapshot_date = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()
    out_dir = SNAPSHOTS_DIR / snapshot_date

    print(f"Generating snapshot for {snapshot_date} ...")
    problems = _load_problems()
    if not problems:
        print("ERROR: No problem YAML files found under data/problems/")
        sys.exit(1)

    _write_json(problems, out_dir / "problems.json")
    _write_parquet(problems, out_dir / "problems.parquet")
    _print_stats(problems)
    print("\nDone.")


if __name__ == "__main__":
    main()
