"""Verdict dataclass for verification results."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Verdict:
    problem_id: str
    backend: str
    status: str  # "pass", "fail", "error", "timeout", "unknown"
    summary: str = ""
    details: dict = field(default_factory=dict)
    elapsed_seconds: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
