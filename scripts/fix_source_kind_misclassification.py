#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Iterable

from ruamel.yaml import YAML

PAPER_URL_SUBSTRINGS = (
    "arxiv.org",
    "doi.org",
    "jstor.org",
    "springer.com",
    "ams.org",  # exclude bookstore.ams.org
    "annals.math",
    "cambridge.org",
    "wiley.com",
)

EXCLUDE_URL_SUBSTRINGS = (
    "bookstore.ams.org",
)


def _as_str(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    try:
        return str(value)
    except Exception:
        return None


def url_looks_like_paper(url: str) -> bool:
    lower_url = url.lower()
    if any(excl in lower_url for excl in EXCLUDE_URL_SUBSTRINGS):
        return False
    return any(substr in lower_url for substr in PAPER_URL_SUBSTRINGS)


def iter_sources_nodes(doc: Any) -> Iterable[dict[str, Any]]:
    if not isinstance(doc, dict):
        return
    sources = doc.get("sources")
    if not isinstance(sources, dict):
        return
    for list_name in ("canonical", "status_evidence"):
        items = sources.get(list_name)
        if items is None:
            continue
        if isinstance(items, dict):
            candidates = (items,)
        elif isinstance(items, list):
            candidates = items
        else:
            continue
        for item in candidates:
            if isinstance(item, dict):
                yield item


def fix_file(path: Path, *, yaml: YAML, dry_run: bool) -> tuple[bool, int]:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:
        print(f"[WARN] Failed to read {path}: {exc}", file=sys.stderr)
        return False, 0

    try:
        doc = yaml.load(text)
    except Exception as exc:
        print(f"[WARN] Failed to parse {path}: {exc}", file=sys.stderr)
        return False, 0

    if doc is None:
        return False, 0

    lines = text.splitlines(keepends=True)
    replacements: list[tuple[int, int]] = []

    for source in iter_sources_nodes(doc):
        kind_raw = source.get("kind")
        kind = _as_str(kind_raw)
        if kind is None or kind.strip().lower() != "website":
            continue

        url_raw = source.get("url")
        url = _as_str(url_raw)
        if url is None or not url_looks_like_paper(url):
            continue

        try:
            line_no, col_no = source.lc.value("kind")
        except Exception:
            continue

        if line_no is None or col_no is None:
            continue
        if line_no < 0 or line_no >= len(lines):
            continue
        if col_no < 0 or col_no > len(lines[line_no]):
            continue

        replacements.append((line_no, col_no))

    if not replacements:
        return False, 0

    kinds_changed = 0
    for line_no, col_no in replacements:
        line = lines[line_no]
        rest = line[col_no:]
        if not rest.startswith("website"):
            # Safety check: avoid unintended edits if positions don't align.
            continue
        lines[line_no] = f"{line[:col_no]}paper{rest[len('website'):]}"
        kinds_changed += 1

    if kinds_changed == 0:
        return False, 0

    if not dry_run:
        path.write_text("".join(lines), encoding="utf-8")

    return True, kinds_changed


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Reclassify sources.kind from 'website' to 'paper' when URL indicates an academic paper/preprint."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("data/problems"),
        help="Root directory to scan (default: data/problems).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Scan and report changes without writing files.",
    )
    args = parser.parse_args(argv)

    root: Path = args.root
    if not root.exists():
        print(f"[ERROR] Root path does not exist: {root}", file=sys.stderr)
        return 2

    yaml = YAML(typ="rt")
    yaml.preserve_quotes = True

    problem_dirs = (
        root / "mathematics",
        root / "theoretical-cs",
        root / "mathematical-physics",
    )
    yaml_files: list[Path] = []
    for d in problem_dirs:
        if not d.exists():
            continue
        yaml_files.extend(d.rglob("*.yaml"))

    files_modified = 0
    total_kind_changes = 0

    for path in sorted(yaml_files):
        changed, kinds_changed = fix_file(path, yaml=yaml, dry_run=args.dry_run)
        if changed:
            files_modified += 1
            total_kind_changes += kinds_changed

    mode = "Dry run" if args.dry_run else "Applied"
    print(
        f"{mode}: modified {files_modified} file(s); updated {total_kind_changes} source kind value(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
