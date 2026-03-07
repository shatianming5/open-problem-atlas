"""Tests ensuring every problem has a valid verification contract."""

import json
from pathlib import Path

import pytest
import yaml
import jsonschema

ROOT = Path(__file__).resolve().parent.parent
PROBLEMS_DIR = ROOT / "data" / "problems"
CONTRACTS_DIR = ROOT / "verifiers" / "contracts"
SCHEMA_PATH = ROOT / "schema" / "verifier-contract.schema.json"


def _load_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _all_problem_slugs() -> set[str]:
    """Return the set of file-stem slugs for all problem YAMLs."""
    return {p.stem for p in PROBLEMS_DIR.rglob("*.yaml")}


def _all_contract_slugs() -> set[str]:
    """Return the set of file-stem slugs for all contract YAMLs."""
    return {c.stem for c in CONTRACTS_DIR.glob("*.yaml")}


def _all_problem_ids() -> dict[str, str]:
    """Return a mapping from slug -> problem id."""
    result = {}
    for p in PROBLEMS_DIR.rglob("*.yaml"):
        data = _load_yaml(p)
        if data and data.get("id"):
            result[p.stem] = data["id"]
    return result


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_every_problem_has_contract():
    """Every problem YAML in data/problems/ must have a matching contract."""
    problem_slugs = _all_problem_slugs()
    contract_slugs = _all_contract_slugs()
    missing = problem_slugs - contract_slugs
    assert not missing, (
        f"{len(missing)} problem(s) have no contract:\n"
        + "\n".join(sorted(missing)[:20])
        + ("\n..." if len(missing) > 20 else "")
    )


def test_contracts_valid_schema():
    """All contract YAMLs must validate against verifier-contract.schema.json."""
    schema = _load_json(SCHEMA_PATH)
    contract_files = sorted(CONTRACTS_DIR.glob("*.yaml"))
    assert contract_files, "No contract files found"

    errors = []
    for cf in contract_files:
        contract = _load_yaml(cf)
        try:
            jsonschema.validate(instance=contract, schema=schema)
        except jsonschema.ValidationError as e:
            errors.append(f"{cf.name}: {e.message}")

    assert not errors, (
        f"{len(errors)} contract(s) failed schema validation:\n"
        + "\n".join(errors[:20])
        + ("\n..." if len(errors) > 20 else "")
    )


def test_contract_problem_ids_match():
    """Each contract's problem_id must match the id in the corresponding problem YAML."""
    problem_ids = _all_problem_ids()
    contract_files = sorted(CONTRACTS_DIR.glob("*.yaml"))

    mismatches = []
    for cf in contract_files:
        slug = cf.stem
        contract = _load_yaml(cf)
        contract_pid = contract.get("problem_id", "")
        expected_pid = problem_ids.get(slug)
        if expected_pid and contract_pid != expected_pid:
            mismatches.append(
                f"{slug}: contract has '{contract_pid}', problem has '{expected_pid}'"
            )

    assert not mismatches, (
        f"{len(mismatches)} contract(s) have mismatched problem_id:\n"
        + "\n".join(mismatches[:20])
    )
