"""Tests for data schema validation."""

import json
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = ROOT / "schema"
DATA_DIR = ROOT / "data"


def load_schema(name):
    with open(SCHEMA_DIR / f"{name}.schema.json") as f:
        return json.load(f)


def collect_yaml_files(subdir):
    path = DATA_DIR / subdir
    if not path.exists():
        return []
    return sorted(path.rglob("*.yaml"))


class TestProblemSchema:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.schema = load_schema("problem")
        self.validator = Draft202012Validator(self.schema)

    @pytest.mark.parametrize("yaml_file", collect_yaml_files("problems"), ids=lambda f: f.name)
    def test_problem_validates(self, yaml_file):
        with open(yaml_file) as f:
            data = yaml.safe_load(f)
        assert data is not None, f"{yaml_file.name} is empty"
        errors = list(self.validator.iter_errors(data))
        if errors:
            msg = "\n".join(f"  - {e.json_path}: {e.message}" for e in errors[:5])
            pytest.fail(f"{yaml_file.name} has schema errors:\n{msg}")


class TestCollectionSchema:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.schema = load_schema("collection")
        self.validator = Draft202012Validator(self.schema)

    @pytest.mark.parametrize("yaml_file", collect_yaml_files("collections"), ids=lambda f: f.name)
    def test_collection_validates(self, yaml_file):
        with open(yaml_file) as f:
            data = yaml.safe_load(f)
        assert data is not None, f"{yaml_file.name} is empty"
        errors = list(self.validator.iter_errors(data))
        if errors:
            msg = "\n".join(f"  - {e.json_path}: {e.message}" for e in errors[:5])
            pytest.fail(f"{yaml_file.name} has schema errors:\n{msg}")


class TestUniqueIds:
    def test_no_duplicate_problem_ids(self):
        ids = {}
        for yaml_file in collect_yaml_files("problems"):
            with open(yaml_file) as f:
                data = yaml.safe_load(f)
            if data and "id" in data:
                pid = data["id"]
                assert pid not in ids, f"Duplicate id '{pid}': {yaml_file.name} and {ids[pid]}"
                ids[pid] = yaml_file.name

    def test_all_problems_have_canonical_source(self):
        for yaml_file in collect_yaml_files("problems"):
            with open(yaml_file) as f:
                data = yaml.safe_load(f)
            if data:
                sources = data.get("sources", {}).get("canonical", [])
                assert len(sources) > 0, f"{yaml_file.name} has no canonical source"

    def test_all_problems_have_status_evidence(self):
        for yaml_file in collect_yaml_files("problems"):
            with open(yaml_file) as f:
                data = yaml.safe_load(f)
            if data:
                evidence = data.get("sources", {}).get("status_evidence", [])
                assert len(evidence) > 0, f"{yaml_file.name} has no status evidence"
