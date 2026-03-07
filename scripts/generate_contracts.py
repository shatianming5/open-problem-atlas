#!/usr/bin/env python3
"""Generate L3 verification contracts for all problems missing one.

Reads every problem YAML under data/problems/, checks which already have
a contract in verifiers/contracts/, and generates a new contract for each
problem that lacks one.  Existing contracts are never modified.
"""

import os
import sys
import textwrap
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PROBLEMS_DIR = ROOT / "data" / "problems"
CONTRACTS_DIR = ROOT / "verifiers" / "contracts"


def load_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def slug_from_path(path: Path) -> str:
    """Return the file stem, e.g. 'collatz-conjecture'."""
    return path.stem


def determine_task_type_and_backend(problem: dict) -> tuple[str, str]:
    """Return (task_type, backend) based on verification_profile + problem_type."""
    vp = problem.get("verification_profile", {})
    checkability = vp.get("solution_checkability", "")
    ptype = problem.get("problem_type", "")

    if checkability == "computational":
        if ptype == "conjecture":
            return "conjecture_check_range", "python_checker"
        if ptype in ("existence", "computation"):
            return "counterexample_search", "python_checker"
        if ptype == "bound":
            return "bound_verification", "python_checker"
        # fallback for computational with other problem_types (e.g. open_question, classification)
        return "conjecture_check_range", "python_checker"

    if checkability == "proof_assistant":
        return "proof_check", "lean4"

    # mixed, expert_review, or anything else
    return "statement_verification", "python_checker"


def build_success_criteria(problem: dict) -> str:
    """Build a human-readable success_criteria string."""
    title = problem.get("title", "Unknown Problem")
    stmt = problem.get("statement", {})
    informal = stmt.get("informal", "")
    canonical = stmt.get("canonical", "")

    # Use informal if available, else canonical (truncated)
    description = informal.strip() if informal else canonical.strip()
    # Collapse whitespace
    description = " ".join(description.split())
    # Truncate to keep it readable (max ~300 chars)
    if len(description) > 300:
        description = description[:297] + "..."

    return f"Verify or advance progress on: {title}. {description}"


def build_contract(problem: dict, slug: str) -> dict:
    """Build a contract dict for the given problem."""
    problem_id = problem.get("id", "")
    task_type, backend = determine_task_type_and_backend(problem)

    checker_file = f"verifiers/checkers/auto/{slug.replace('-', '_')}_checker.py"

    criteria = build_success_criteria(problem)
    # Ensure minLength >= 10
    if len(criteria) < 10:
        criteria = f"Verify the open problem: {problem.get('title', slug)}"

    contract = {
        "problem_id": problem_id,
        "backend": backend,
        "task_type": task_type,
        "checker": {
            "file": checker_file,
            "function": "verify",
        },
        "resource_limits": {
            "timeout_seconds": 300,
            "memory_mb": 512,
        },
        "success_criteria": criteria,
        "parameters": {},
    }
    return contract


def write_contract(contract: dict, path: Path) -> None:
    """Write contract dict as YAML."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(
            contract,
            f,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            width=120,
        )


def main():
    # Collect existing contract slugs (by filename stem)
    existing_slugs: set[str] = set()
    if CONTRACTS_DIR.exists():
        for cf in CONTRACTS_DIR.glob("*.yaml"):
            existing_slugs.add(cf.stem)

    # Collect all problem files
    problem_files = sorted(PROBLEMS_DIR.rglob("*.yaml"))
    if not problem_files:
        print("ERROR: No problem YAML files found.", file=sys.stderr)
        sys.exit(1)

    generated = 0
    skipped = 0
    errors = 0

    for pf in problem_files:
        slug = slug_from_path(pf)
        if slug in existing_slugs:
            skipped += 1
            continue

        try:
            problem = load_yaml(pf)
        except Exception as e:
            print(f"ERROR reading {pf}: {e}", file=sys.stderr)
            errors += 1
            continue

        if not problem or not problem.get("id"):
            print(f"WARNING: No 'id' in {pf}, skipping.", file=sys.stderr)
            errors += 1
            continue

        contract = build_contract(problem, slug)
        out_path = CONTRACTS_DIR / f"{slug}.yaml"
        write_contract(contract, out_path)
        generated += 1

    total = generated + skipped + errors
    print(f"Total problems: {total}")
    print(f"  Generated new contracts: {generated}")
    print(f"  Skipped (already exist): {skipped}")
    print(f"  Errors: {errors}")

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
