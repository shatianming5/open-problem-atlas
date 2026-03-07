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

        # Verification profile consistency
        vp = data.get("verification_profile")
        tier = data.get("tier")
        if vp:
            sp = vp.get("statement_precision")
            sc = vp.get("solution_checkability")
            ma = vp.get("machine_actionability")
            # tier_1 requires high precision + checkable + actionable
            if tier == "tier_1":
                if sp != "high":
                    errors.append(f"{rel}: tier_1 but statement_precision is '{sp}' (expected 'high')")
                if sc not in ("proof_assistant", "computational"):
                    errors.append(f"{rel}: tier_1 but solution_checkability is '{sc}' (expected proof_assistant or computational)")
                if ma not in ("high", "medium"):
                    errors.append(f"{rel}: tier_1 but machine_actionability is '{ma}' (expected high or medium)")

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


def validate_contracts() -> list[str]:
    """Validate all verifier contracts and cross-reference with problems."""
    errors = []

    contracts_dir = ROOT / "verifiers" / "contracts"
    if not contracts_dir.exists():
        return []

    schema_path = SCHEMA_DIR / "verifier-contract.schema.json"
    if not schema_path.exists():
        return ["verifier-contract.schema.json not found"]

    with open(schema_path) as f:
        schema = json.load(f)
    validator = Draft202012Validator(schema)

    # Load all problem IDs
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

    seen_problem_ids = set()

    for yaml_file in sorted(contracts_dir.glob("*.yaml")):
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

        # Cross-reference: problem_id must exist
        pid = data.get("problem_id")
        if pid and pid not in problem_ids:
            errors.append(f"{rel}: contract references unknown problem_id '{pid}'")

        # Uniqueness: one contract per problem
        if pid:
            if pid in seen_problem_ids:
                errors.append(f"{rel}: duplicate contract for problem_id '{pid}'")
            seen_problem_ids.add(pid)

        # Checker file must exist
        checker = data.get("checker", {})
        checker_file = checker.get("file")
        if checker_file:
            full_path = ROOT / checker_file
            if not full_path.exists():
                errors.append(f"{rel}: checker file not found: {checker_file}")

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

    print("\n[1/5] Validating problems...")
    errs = validate_problems()
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")
    for e in errs:
        print(f"  - {e}")

    print("\n[2/5] Validating attempts...")
    errs = validate_attempts()
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")
    for e in errs:
        print(f"  - {e}")

    print("\n[3/5] Validating collections...")
    errs = validate_collections()
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")
    for e in errs:
        print(f"  - {e}")

    print("\n[4/5] Validating verifier contracts...")
    errs = validate_contracts()
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")
    for e in errs:
        print(f"  - {e}")

    print("\n[5/5] Validating cross-references...")
    errs = validate_cross_references()
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")
    for e in errs:
        print(f"  - {e}")

    # Tier distribution summary
    from collections import Counter
    tier_counts = Counter()
    problems_dir = DATA_DIR / "problems"
    if problems_dir.exists():
        for yaml_file in problems_dir.rglob("*.yaml"):
            try:
                d = load_yaml(yaml_file)
                if d and d.get("tier"):
                    tier_counts[d["tier"]] += 1
            except Exception:
                pass
    if tier_counts:
        print("\n[info] Tier distribution:")
        for t in ["tier_1", "tier_2", "tier_3"]:
            print(f"  {t}: {tier_counts.get(t, 0)}")

    print("\n" + "=" * 60)
    if all_errors:
        print(f"VALIDATION FAILED: {len(all_errors)} total errors")
        sys.exit(1)
    else:
        print("ALL VALIDATIONS PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
