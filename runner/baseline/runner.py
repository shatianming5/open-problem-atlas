"""Batch execution logic."""

from ..backends import get_backend
from ..attempt_recorder import record_attempt
from ..verdict import Verdict


def run_batch(
    contracts: list[dict],
    record: bool = False,
    verbose: bool = True,
) -> list[Verdict]:
    """Run a batch of contracts and return verdicts."""
    verdicts = []

    for contract in contracts:
        pid = contract["problem_id"]
        try:
            backend = get_backend(contract["backend"])
        except ValueError as e:
            v = Verdict(
                problem_id=pid,
                backend=contract["backend"],
                status="error",
                summary=f"Backend unavailable: {e}",
            )
            verdicts.append(v)
            if verbose:
                print(f"  SKIP {pid}: {e}")
            continue

        if verbose:
            print(f"  Running {pid}...", end=" ", flush=True)

        verdict = backend.run(contract)
        verdicts.append(verdict)

        if verbose:
            icon = {"pass": "OK", "fail": "FAIL", "error": "ERR", "timeout": "TIME"}.get(
                verdict.status, "????"
            )
            print(f"{icon} ({verdict.elapsed_seconds:.1f}s)")

        if record:
            record_attempt(verdict)

    return verdicts
