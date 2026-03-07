"""Reviewer queue management for OpenProblemAtlas.

Tracks problems that need review, assigns reviewers, and manages the
review pipeline from needs_review -> human_verified.
"""

import datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"


def load_problem(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f) or {}


def get_needs_review() -> list[dict]:
    """Return all problems with review_state == 'needs_review'."""
    results = []
    problems_dir = DATA_DIR / "problems"
    if not problems_dir.exists():
        return results
    for yaml_file in sorted(problems_dir.rglob("*.yaml")):
        data = load_problem(yaml_file)
        if not data:
            continue
        status = data.get("status", {})
        if status.get("review_state") == "needs_review":
            results.append({
                "id": data.get("id", "unknown"),
                "title": data.get("title", ""),
                "path": str(yaml_file.relative_to(ROOT)),
                "status_label": status.get("label", ""),
                "confidence": status.get("confidence", ""),
                "last_reviewed_at": status.get("last_reviewed_at", ""),
            })
    return results


def get_stale_problems(as_of: str | None = None) -> list[dict]:
    """Return all problems whose stale_after date has passed."""
    if as_of is None:
        as_of = datetime.date.today().isoformat()
    results = []
    problems_dir = DATA_DIR / "problems"
    if not problems_dir.exists():
        return results
    for yaml_file in sorted(problems_dir.rglob("*.yaml")):
        data = load_problem(yaml_file)
        if not data:
            continue
        status = data.get("status", {})
        stale = status.get("stale_after", "")
        if stale and stale <= as_of:
            results.append({
                "id": data.get("id", "unknown"),
                "title": data.get("title", ""),
                "path": str(yaml_file.relative_to(ROOT)),
                "stale_after": stale,
                "last_reviewed_at": status.get("last_reviewed_at", ""),
                "reviewer": status.get("reviewer", ""),
            })
    return results


def get_auto_generated() -> list[dict]:
    """Return all problems with review_state == 'auto_generated' awaiting human review."""
    results = []
    problems_dir = DATA_DIR / "problems"
    if not problems_dir.exists():
        return results
    for yaml_file in sorted(problems_dir.rglob("*.yaml")):
        data = load_problem(yaml_file)
        if not data:
            continue
        status = data.get("status", {})
        if status.get("review_state") == "auto_generated":
            results.append({
                "id": data.get("id", "unknown"),
                "title": data.get("title", ""),
                "path": str(yaml_file.relative_to(ROOT)),
                "status_label": status.get("label", ""),
            })
    return results


def get_queue_summary() -> dict:
    """Return a summary of the entire review queue."""
    needs_review = get_needs_review()
    stale = get_stale_problems()
    auto_gen = get_auto_generated()
    return {
        "needs_review": len(needs_review),
        "stale": len(stale),
        "auto_generated": len(auto_gen),
        "total_actionable": len(needs_review) + len(stale) + len(auto_gen),
        "items_needs_review": needs_review,
        "items_stale": stale,
        "items_auto_generated": auto_gen,
    }


def print_queue():
    """Print a human-readable review queue report."""
    summary = get_queue_summary()
    print(f"Review Queue Summary")
    print(f"{'=' * 50}")
    print(f"  Needs review:   {summary['needs_review']}")
    print(f"  Stale:          {summary['stale']}")
    print(f"  Auto-generated: {summary['auto_generated']}")
    print(f"  Total:          {summary['total_actionable']}")

    if summary["items_needs_review"]:
        print(f"\n--- Needs Review ---")
        for item in summary["items_needs_review"]:
            print(f"  [{item['status_label']}] {item['id']} — {item['title']}")

    if summary["items_stale"]:
        print(f"\n--- Stale (past stale_after) ---")
        for item in summary["items_stale"]:
            print(f"  {item['id']} — stale_after: {item['stale_after']}, reviewer: {item['reviewer']}")

    if summary["items_auto_generated"]:
        print(f"\n--- Auto-Generated (awaiting human review) ---")
        for item in summary["items_auto_generated"]:
            print(f"  [{item['status_label']}] {item['id']} — {item['title']}")


if __name__ == "__main__":
    print_queue()
