"""SAT/SMT backend using Z3.

Checker scripts for this backend are still Python files, but they
internally use the z3-solver library for constraint solving.
"""

import json
import subprocess
import sys
import time
from pathlib import Path

from ..config import ROOT, DEFAULT_TIMEOUT
from ..verdict import Verdict
from . import register
from .base import Backend


@register("sat_smt")
class SatSmtBackend(Backend):

    @property
    def name(self) -> str:
        return "sat_smt"

    def is_available(self) -> bool:
        """Check if z3-solver is installed."""
        try:
            subprocess.run(
                [sys.executable, "-c", "import z3"],
                capture_output=True,
                timeout=10,
            )
            return True
        except Exception:
            return False

    def run(self, contract: dict) -> Verdict:
        problem_id = contract["problem_id"]
        checker_file = ROOT / contract["checker"]["file"]
        function_name = contract["checker"]["function"]
        params = contract.get("parameters", {})
        timeout = contract.get("resource_limits", {}).get("timeout_seconds", DEFAULT_TIMEOUT)

        if not checker_file.exists():
            return Verdict(
                problem_id=problem_id,
                backend="sat_smt",
                status="error",
                summary=f"Checker file not found: {checker_file}",
            )

        params_json = json.dumps(params)
        wrapper = (
            f"import json, sys; sys.path.insert(0, {str(ROOT)!r}); "
            f"sys.path.insert(0, {str(checker_file.parent)!r}); "
            f"from {checker_file.stem} import {function_name}; "
            f"result = {function_name}(json.loads({params_json!r})); "
            f"print(json.dumps(result))"
        )

        start = time.monotonic()
        try:
            proc = subprocess.run(
                [sys.executable, "-c", wrapper],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(ROOT),
            )
            elapsed = time.monotonic() - start

            if proc.returncode != 0:
                return Verdict(
                    problem_id=problem_id,
                    backend="sat_smt",
                    status="error",
                    summary=f"Checker exited with code {proc.returncode}",
                    details={"stderr": proc.stderr[:2000], "stdout": proc.stdout[:2000]},
                    elapsed_seconds=round(elapsed, 3),
                )

            try:
                result = json.loads(proc.stdout.strip())
            except json.JSONDecodeError:
                return Verdict(
                    problem_id=problem_id,
                    backend="sat_smt",
                    status="error",
                    summary="Checker produced invalid JSON",
                    details={"stdout": proc.stdout[:2000]},
                    elapsed_seconds=round(elapsed, 3),
                )

            return Verdict(
                problem_id=problem_id,
                backend="sat_smt",
                status=result.get("status", "unknown"),
                summary=result.get("summary", ""),
                details=result.get("details", {}),
                elapsed_seconds=round(elapsed, 3),
            )

        except subprocess.TimeoutExpired:
            elapsed = time.monotonic() - start
            return Verdict(
                problem_id=problem_id,
                backend="sat_smt",
                status="timeout",
                summary=f"Checker timed out after {timeout}s",
                elapsed_seconds=round(elapsed, 3),
            )
