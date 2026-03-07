"""Generate JSON and Markdown reports from batch verdicts."""

import json
from datetime import datetime
from pathlib import Path

from ..verdict import Verdict


def generate_report(verdicts: list[Verdict], output_dir: Path | None = None) -> dict:
    """Generate a report dict from a list of verdicts."""
    report = {
        "generated_at": datetime.utcnow().isoformat(),
        "total": len(verdicts),
        "summary": {},
        "verdicts": [],
    }

    counts = {}
    for v in verdicts:
        counts[v.status] = counts.get(v.status, 0) + 1
        report["verdicts"].append({
            "problem_id": v.problem_id,
            "backend": v.backend,
            "status": v.status,
            "summary": v.summary,
            "elapsed_seconds": v.elapsed_seconds,
        })

    report["summary"] = counts

    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)

        # JSON report
        json_path = output_dir / "report.json"
        with open(json_path, "w") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # Markdown report
        md_path = output_dir / "report.md"
        with open(md_path, "w") as f:
            f.write(f"# Verification Report\n\n")
            f.write(f"Generated: {report['generated_at']}\n\n")
            f.write(f"## Summary\n\n")
            f.write(f"| Status | Count |\n|--------|-------|\n")
            for status, count in sorted(counts.items()):
                f.write(f"| {status} | {count} |\n")
            f.write(f"| **total** | **{len(verdicts)}** |\n\n")
            f.write(f"## Details\n\n")
            f.write(f"| Problem | Backend | Status | Time | Summary |\n")
            f.write(f"|---------|---------|--------|------|----------|\n")
            for v in report["verdicts"]:
                f.write(
                    f"| {v['problem_id']} | {v['backend']} | {v['status']} "
                    f"| {v['elapsed_seconds']:.1f}s | {v['summary'][:60]} |\n"
                )

    return report
