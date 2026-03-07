"""Lean 4 backend stub.

This backend will eventually invoke Lean 4 to check proofs.
Currently a stub that reports unavailability.
"""

import shutil

from ..verdict import Verdict
from . import register
from .base import Backend


@register("lean4")
class Lean4Backend(Backend):

    @property
    def name(self) -> str:
        return "lean4"

    def is_available(self) -> bool:
        """Check if lean4 (lake) is installed."""
        return shutil.which("lean") is not None or shutil.which("lake") is not None

    def run(self, contract: dict) -> Verdict:
        problem_id = contract["problem_id"]

        if not self.is_available():
            return Verdict(
                problem_id=problem_id,
                backend="lean4",
                status="error",
                summary="Lean 4 is not installed",
            )

        # Stub: real implementation would invoke lean/lake on the checker file
        return Verdict(
            problem_id=problem_id,
            backend="lean4",
            status="unknown",
            summary="Lean 4 backend not yet implemented",
        )
