"""Validate all data files against their JSON schemas."""

import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parent.parent.parent
SCHEMA_DIR = ROOT / "schema"
DATA_DIR = ROOT / "data"

URL_PATTERN = re.compile(r"^https?://[^\s]+$")


def load_schema(name: str) -> dict:
    path = SCHEMA_DIR / f"{name}.schema.json"
    with open(path) as f:
        return json.load(f)


def load_yaml(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def validate_problems() -> list[str]:
    """Validate all problem YAML files against problem.schema.json."""
    schema = load_schema("problem")
    validator = Draft202012Validator(schema)
    errors = []
    seen_ids = set()
    seen_slugs = set()

    problems_dir = DATA_DIR / "problems"
    if not problems_dir.exists():
        return ["data/problems/ directory not found"]

    for yaml_file in sorted(problems_dir.rglob("*.yaml")):
        rel = yaml_file.relative_to(ROOT)
        try:
            data = load_yaml(yaml_file)
        except Exception as e:
            errors.append(f"{rel}: YAML parse error: {e}")
            continue

        if data is None:
            errors.append(f"{rel}: empty file")
            continue

        # Schema validation
        for err in validator.iter_errors(data):
            path_str = ".".join(str(p) for p in err.absolute_path)
            errors.append(f"{rel}: {path_str}: {err.message}")

        # Uniqueness checks
        pid = data.get("id")
        if pid:
            if pid in seen_ids:
                errors.append(f"{rel}: duplicate id '{pid}'")
            seen_ids.add(pid)

            # Slug uniqueness (last segment of id)
            slug = pid.rsplit(".", 1)[-1] if "." in pid else pid
            if slug in seen_slugs:
                errors.append(f"{rel}: duplicate slug '{slug}'")
            seen_slugs.add(slug)

        # Required content checks
        if not data.get("statement", {}).get("canonical"):
            errors.append(f"{rel}: missing canonical statement")

        sources = data.get("sources", {})
        canonical_sources = sources.get("canonical", [])
        if not canonical_sources:
            errors.append(f"{rel}: no canonical source")

        status_evidence = sources.get("status_evidence", [])
        if not status_evidence:
            errors.append(f"{rel}: no status evidence")

        status = data.get("status", {})
        if not status.get("last_reviewed_at"):
            errors.append(f"{rel}: missing last_reviewed_at")

        # Machine-generated fields must have disclaimer
        mg = data.get("machine_generated")
        if mg and mg.get("disclaimer") != "unverified":
            errors.append(f"{rel}: machine_generated section missing disclaimer: unverified")

        # URL format validation in sources
        for src_list_key in ["canonical", "status_evidence"]:
            for src in sources.get(src_list_key, []):
                url = src.get("url")
                if url and not URL_PATTERN.match(url):
                    errors.append(f"{rel}: invalid URL format in {src_list_key}: '{url}'")

    return errors


def validate_attempts() -> list[str]:
    """Validate all attempt YAML files against attempt.schema.json."""
    schema = load_schema("attempt")
    validator = Draft202012Validator(schema)
    errors = []

    attempts_dir = DATA_DIR / "attempts"
    if not attempts_dir.exists():
        return []

    for yaml_file in sorted(attempts_dir.rglob("*.yaml")):
        rel = yaml_file.relative_to(ROOT)
        try:
            data = load_yaml(yaml_file)
        except Exception as e:
            errors.append(f"{rel}: YAML parse error: {e}")
            continue

        if data is None:
            continue

        for err in validator.iter_errors(data):
            path_str = ".".join(str(p) for p in err.absolute_path)
            errors.append(f"{rel}: {path_str}: {err.message}")

    return errors


def validate_collections() -> list[str]:
    """Validate all collection YAML files against collection.schema.json."""
    schema = load_schema("collection")
    validator = Draft202012Validator(schema)
    errors = []

    collections_dir = DATA_DIR / "collections"
    if not collections_dir.exists():
        return []

    for yaml_file in sorted(collections_dir.rglob("*.yaml")):
        rel = yaml_file.relative_to(ROOT)
        try:
            data = load_yaml(yaml_file)
        except Exception as e:
            errors.append(f"{rel}: YAML parse error: {e}")
            continue

        if data is None:
            continue

        for err in validator.iter_errors(data):
            path_str = ".".join(str(p) for p in err.absolute_path)
            errors.append(f"{rel}: {path_str}: {err.message}")

    return errors


def validate_cross_references() -> list[str]:
    """Check that relation references and attempt problem_ids point to existing problems."""
    errors = []
    problem_ids = set()

    problems_dir = DATA_DIR / "problems"
    if problems_dir.exists():
        for yaml_file in problems_dir.rglob("*.yaml"):
            try:
                data = load_yaml(yaml_file)
                if data and data.get("id"):
                    problem_ids.add(data["id"])
            except Exception:
                pass

    # Check relations in problems
    if problems_dir.exists():
        for yaml_file in problems_dir.rglob("*.yaml"):
            rel = yaml_file.relative_to(ROOT)
            try:
                data = load_yaml(yaml_file)
            except Exception:
                continue
            if not data:
                continue

            relations = data.get("relations", {})
            for rel_type in ["equivalent_to", "generalizes", "special_cases", "related"]:
                for ref_id in (relations.get(rel_type) or []):
                    if ref_id not in problem_ids:
                        errors.append(f"{rel}: relation {rel_type} references unknown id '{ref_id}'")

    # Check attempt problem_ids
    attempts_dir = DATA_DIR / "attempts"
    if attempts_dir.exists():
        for yaml_file in attempts_dir.rglob("*.yaml"):
            rel = yaml_file.relative_to(ROOT)
            try:
                data = load_yaml(yaml_file)
            except Exception:
                continue
            if not data:
                continue
            pid = data.get("problem_id")
            if pid and pid not in problem_ids:
                errors.append(f"{rel}: attempt references unknown problem_id '{pid}'")

    # Check collection problem_ids
    collections_dir = DATA_DIR / "collections"
    if collections_dir.exists():
        for yaml_file in collections_dir.rglob("*.yaml"):
            rel = yaml_file.relative_to(ROOT)
            try:
                data = load_yaml(yaml_file)
            except Exception:
                continue
            if not data:
                continue
            for entry in data.get("problems", []):
                pid = entry.get("problem_id")
                if pid and pid not in problem_ids:
                    errors.append(f"{rel}: collection references unknown problem_id '{pid}'")

    return errors


def main():
    print("=" * 60)
    print("OpenProblemAtlas Data Validation")
    print("=" * 60)

    all_errors = []

    print("\n[1/4] Validating problems...")
    errs = validate_problems()
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")
    for e in errs:
        print(f"  - {e}")

    print("\n[2/4] Validating attempts...")
    errs = validate_attempts()
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")
    for e in errs:
        print(f"  - {e}")

    print("\n[3/4] Validating collections...")
    errs = validate_collections()
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")
    for e in errs:
        print(f"  - {e}")

    print("\n[4/4] Validating cross-references...")
    errs = validate_cross_references()
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")
    for e in errs:
        print(f"  - {e}")

    print("\n" + "=" * 60)
    if all_errors:
        print(f"VALIDATION FAILED: {len(all_errors)} total errors")
        sys.exit(1)
    else:
        print("ALL VALIDATIONS PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
