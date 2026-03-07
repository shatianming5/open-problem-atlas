"""Load and validate verifier contracts."""

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from .config import CONTRACTS_DIR, SCHEMA_DIR


def _load_contract_schema() -> dict:
    schema_path = SCHEMA_DIR / "verifier-contract.schema.json"
    with open(schema_path) as f:
        return json.load(f)


_SCHEMA = None


def _get_validator() -> Draft202012Validator:
    global _SCHEMA
    if _SCHEMA is None:
        _SCHEMA = _load_contract_schema()
    return Draft202012Validator(_SCHEMA)


def load_contract(path: Path) -> dict:
    """Load and validate a single contract YAML file."""
    with open(path) as f:
        data = yaml.safe_load(f)
    validator = _get_validator()
    errors = list(validator.iter_errors(data))
    if errors:
        msg = "; ".join(e.message for e in errors)
        raise ValueError(f"Contract {path.name} validation failed: {msg}")
    return data


def load_all_contracts() -> list[dict]:
    """Load all contracts from the contracts directory."""
    contracts = []
    if not CONTRACTS_DIR.exists():
        return contracts
    for yaml_file in sorted(CONTRACTS_DIR.glob("*.yaml")):
        contracts.append(load_contract(yaml_file))
    return contracts


def get_contract_for_problem(problem_id: str) -> dict | None:
    """Find a contract for a given problem ID."""
    if not CONTRACTS_DIR.exists():
        return None
    for yaml_file in CONTRACTS_DIR.glob("*.yaml"):
        with open(yaml_file) as f:
            data = yaml.safe_load(f)
        if data and data.get("problem_id") == problem_id:
            return data
    return None
