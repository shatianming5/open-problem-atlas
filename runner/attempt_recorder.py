"""Record verification verdicts as attempt YAML files."""

import hashlib
from datetime import date
from pathlib import Path

import yaml

from .config import ATTEMPTS_DIR
from .verdict import Verdict


def _make_attempt_id(verdict: Verdict) -> str:
    slug = verdict.problem_id.rsplit(".", 1)[-1]
    today = date.today().strftime("%Y%m%d")
    h = hashlib.sha256(
        f"{verdict.problem_id}{verdict.backend}{verdict.timestamp}".encode()
    ).hexdigest()[:6]
    return f"att_{slug}_{verdict.backend}_{today}_{h}"


def record_attempt(verdict: Verdict) -> Path:
    """Write a verdict as an attempt YAML file. Returns the path written."""
    ATTEMPTS_DIR.mkdir(parents=True, exist_ok=True)

    attempt_id = _make_attempt_id(verdict)

    # Map verdict status to verification_status
    verification_status = "verified" if verdict.status == "pass" else "unverified"

    # Map verdict status to result_type
    result_type_map = {
        "pass": "computational_evidence",
        "fail": "counterexample_candidate",
        "error": "no_progress",
        "timeout": "no_progress",
        "unknown": "no_progress",
    }
    result_type = result_type_map.get(verdict.status, "no_progress")

    attempt = {
        "attempt_id": attempt_id,
        "problem_id": verdict.problem_id,
        "actor": "opa-runner-v1",
        "actor_type": "ai",
        "date": date.today().isoformat(),
        "method_summary": f"Automated verification via {verdict.backend} backend: {verdict.summary}",
        "outcome": {
            "summary": verdict.summary,
            "result_type": result_type,
        },
        "verification_status": verification_status,
        "labels": ["machine-generated", "reproducible"],
        "auto_generated": True,
        "verifier_verdict": {
            "backend": verdict.backend,
            "status": verdict.status,
            "summary": verdict.summary,
            "elapsed_seconds": verdict.elapsed_seconds,
            "timestamp": verdict.timestamp,
        },
    }

    path = ATTEMPTS_DIR / f"{attempt_id}.yaml"
    with open(path, "w") as f:
        yaml.dump(attempt, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    return path
