#!/usr/bin/env python3
"""Generate Lean4 formalization stubs for open problems."""

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PROBLEMS_DIR = ROOT / "data" / "problems"
CONTRACTS_DIR = ROOT / "verifiers" / "contracts"
LEAN_DIR = ROOT / "formalization" / "lean4"


def make_lean_name(title: str) -> str:
    """Convert problem title to valid Lean4 identifier."""
    words = re.sub(r"[^a-zA-Z0-9\s]", "", title).split()
    return "".join(w.capitalize() for w in words[:6])


def generate_stub(problem: dict) -> str:
    """Generate a Lean4 stub for a problem."""
    title = problem.get("title", "Unknown")
    lean_name = make_lean_name(title)
    statement = problem.get("statement", {})
    if isinstance(statement, dict):
        canonical = statement.get("canonical", "")
        informal = statement.get("informal", canonical)
    else:
        canonical = str(statement)
        informal = canonical
    domain = problem.get("domain", "mathematics")
    pid = problem.get("id", "")

    comment = (informal or canonical)[:300].replace("*/", "* /").replace("/-", "/ -")

    return f'''/-
  {title}

  Domain: {domain}
  ID: {pid}
  Status: Open

  {comment}
-/

-- This is a formalization stub. The actual proof is an open problem.
-- See: https://openproblem-atlas.org/problem/{pid.replace(".", "-")}.html

/-- {title} -/
axiom {lean_name} : True  -- OPEN PROBLEM: formal statement needed
'''


def should_include(problem: dict, slug: str) -> bool:
    """Determine whether a problem should get a Lean4 stub.

    Selection criteria (in priority order):
    1. Contract backend is lean4
    2. Statement precision is high
    3. Statement precision is medium AND formality score >= 0.5
    4. Solution checkability is computational or proof_assistant
    5. Formality score >= 0.3
    6. Tier 1 or tier 2 problem
    """
    vp = problem.get("verification_profile", {})
    if not isinstance(vp, dict):
        vp = {}
    scores = problem.get("scores", {})
    if not isinstance(scores, dict):
        scores = {}
    tier = problem.get("tier", "")

    # 1. Check contract backend
    contract_file = CONTRACTS_DIR / f"{slug}.yaml"
    if contract_file.exists():
        with open(contract_file) as cf:
            cd = yaml.safe_load(cf)
            if cd and cd.get("backend") == "lean4":
                return True

    # 2. High precision statement
    if vp.get("statement_precision") == "high":
        return True

    # 3. Medium precision with decent formality
    if (
        vp.get("statement_precision") == "medium"
        and scores.get("formality", 0) >= 0.5
    ):
        return True

    # 4. Computationally or proof-assistant checkable
    if vp.get("solution_checkability") in ("computational", "proof_assistant"):
        return True

    # 5. Reasonable formality score
    if scores.get("formality", 0) >= 0.3:
        return True

    # 6. High-importance tiers
    if tier in ("tier_1", "tier_2"):
        return True

    return False


def main():
    problems = []
    for f in sorted(PROBLEMS_DIR.rglob("*.yaml")):
        with open(f) as fh:
            d = yaml.safe_load(fh)
            if not d or "id" not in d:
                continue

        slug = f.stem
        if should_include(d, slug):
            d["_slug"] = slug
            problems.append(d)

    LEAN_DIR.mkdir(parents=True, exist_ok=True)

    generated = 0
    for p in problems:
        slug = p["id"].replace(".", "_")
        filename = f"{slug}.lean"
        path = LEAN_DIR / filename

        stub = generate_stub(p)
        with open(path, "w") as f:
            f.write(stub)
        generated += 1

    total = sum(1 for _ in PROBLEMS_DIR.rglob("*.yaml"))
    pct = (generated / total * 100) if total else 0
    print(f"Generated {generated} Lean4 stubs ({pct:.1f}% of {total} problems)")
    print(f"Output: {LEAN_DIR}")


if __name__ == "__main__":
    main()
