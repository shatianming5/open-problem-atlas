#!/usr/bin/env python3
"""Promote high-confidence leads to verified problem YAML files.

Reads all leads from data/leads/, filters those with confidence >= 0.7,
deduplicates against existing problems (case-insensitive title match),
and writes new problem YAML files to the appropriate subdirectory.
"""

import re
import sys
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
LEADS_DIR = ROOT / "data" / "leads"
PROBLEMS_DIR = ROOT / "data" / "problems"

CONFIDENCE_THRESHOLD = 0.7
TODAY = date.today().isoformat()

# Domain mapping: domain_hint -> (directory name, id prefix)
DOMAIN_MAP = {
    "mathematics": ("mathematics", "opa.mathematics"),
    "math": ("mathematics", "opa.mathematics"),
    "theoretical-cs": ("theoretical-cs", "opa.tcs"),
    "tcs": ("theoretical-cs", "opa.tcs"),
    "theoretical-computer-science": ("theoretical-cs", "opa.tcs"),
    "mathematical-physics": ("mathematical-physics", "opa.phys"),
    "physics": ("mathematical-physics", "opa.phys"),
}


def load_yaml(path: Path) -> dict | None:
    """Load a YAML file, returning None on error."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"WARNING: Could not read {path}: {e}", file=sys.stderr)
        return None


def collect_existing_titles() -> set[str]:
    """Return a set of lowercase titles from all existing problems."""
    titles = set()
    for yaml_file in PROBLEMS_DIR.rglob("*.yaml"):
        data = load_yaml(yaml_file)
        if data and "title" in data:
            titles.add(data["title"].strip().lower())
    return titles


def make_slug(title: str) -> str:
    """Generate a URL-friendly slug from a title.

    Lowercase, replace non-alphanumeric chars with hyphens,
    collapse runs of hyphens, strip leading/trailing hyphens,
    and truncate to 60 characters.
    """
    slug = title.lower()
    # Replace any non-alphanumeric character (except hyphen) with hyphen
    slug = re.sub(r"[^a-z0-9-]", "-", slug)
    # Collapse runs of hyphens
    slug = re.sub(r"-{2,}", "-", slug)
    # Strip leading/trailing hyphens
    slug = slug.strip("-")
    # Truncate to 60 chars, ensuring we don't cut in the middle
    if len(slug) > 60:
        slug = slug[:60].rstrip("-")
    return slug


def build_problem(lead: dict) -> dict:
    """Convert a lead dict into a full problem dict."""
    title = lead.get("title", "Untitled")
    statement_text = lead.get("statement", "")
    domain_hint = lead.get("domain_hint", "mathematics")
    subdomain_hint = lead.get("subdomain_hint", "general")
    source_id = lead.get("source_id", "")
    source_url = lead.get("source_url", "")

    # Resolve domain
    dir_name, id_prefix = DOMAIN_MAP.get(domain_hint, ("mathematics", "opa.mathematics"))

    # Build slug
    slug = make_slug(title)

    # Build the problem id: opa.<domain>.<subdomain>.<slug>
    problem_id = f"{id_prefix}.{subdomain_hint}.{slug}"

    # Build source entry
    source_entry = {
        "source_id": source_id if source_id else f"src_{slug.replace('-', '_')}",
        "kind": "website",
    }
    if source_url:
        source_entry["url"] = source_url

    # Build status evidence using the same source
    evidence_entry = {
        "source_id": source_entry["source_id"],
        "kind": "website",
    }
    if source_url:
        evidence_entry["url"] = source_url

    problem = {
        "id": problem_id,
        "kind": "problem",
        "title": title,
        "status": {
            "label": "open",
            "confidence": "medium",
            "last_reviewed_at": TODAY,
            "review_state": "auto_generated",
        },
        "domain": dir_name,
        "subdomains": [subdomain_hint],
        "verification_profile": {
            "statement_precision": "medium",
            "solution_checkability": "expert_review",
            "machine_actionability": "low",
        },
        "tier": "tier_3",
        "statement": {
            "canonical": statement_text,
        },
        "sources": {
            "canonical": [source_entry],
            "status_evidence": [evidence_entry],
        },
        "provenance": {
            "created_from": "radar_promotion",
            "parser_version": "0.3.1",
            "schema_version": "1.0.0",
        },
    }

    return problem, dir_name, slug


def main():
    # 1. Collect existing problem titles for dedup
    existing_titles = collect_existing_titles()
    print(f"Existing problems: {len(existing_titles)}")

    # 2. Read all leads
    lead_files = sorted(LEADS_DIR.glob("*.yaml"))
    if not lead_files:
        print("ERROR: No lead files found in data/leads/", file=sys.stderr)
        sys.exit(1)
    print(f"Total lead files: {len(lead_files)}")

    promoted = 0
    skipped_confidence = 0
    skipped_duplicate = 0
    skipped_error = 0

    for lf in lead_files:
        lead = load_yaml(lf)
        if not lead:
            skipped_error += 1
            continue

        # 3. Filter by confidence
        confidence = lead.get("confidence", 0)
        if not isinstance(confidence, (int, float)) or confidence < CONFIDENCE_THRESHOLD:
            skipped_confidence += 1
            continue

        # 4. Dedup: check title against existing problems (case-insensitive)
        title = lead.get("title", "").strip()
        if not title:
            skipped_error += 1
            continue

        if title.lower() in existing_titles:
            skipped_duplicate += 1
            continue

        # 5. Convert lead to problem
        problem, dir_name, slug = build_problem(lead)

        # 6. Write to appropriate subdirectory
        out_dir = PROBLEMS_DIR / dir_name
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{slug}.yaml"

        # If file already exists (e.g., different title but same slug), skip
        if out_path.exists():
            skipped_duplicate += 1
            existing_titles.add(title.lower())
            continue

        with open(out_path, "w", encoding="utf-8") as f:
            yaml.dump(
                problem,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
                width=120,
            )

        # Track the newly added title to avoid duplicates within leads
        existing_titles.add(title.lower())
        promoted += 1

    print(f"\nResults:")
    print(f"  Promoted to problems: {promoted}")
    print(f"  Skipped (low confidence): {skipped_confidence}")
    print(f"  Skipped (duplicate title): {skipped_duplicate}")
    print(f"  Skipped (errors): {skipped_error}")
    print(f"  Total processed: {promoted + skipped_confidence + skipped_duplicate + skipped_error}")


if __name__ == "__main__":
    main()
