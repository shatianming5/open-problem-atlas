"""CLI interface for the verification runner."""

import argparse
import sys

from .contract import load_all_contracts, get_contract_for_problem
from .backends import get_backend, list_backends
from .attempt_recorder import record_attempt


def cmd_verify(args):
    """Run verification for a single problem."""
    contract = get_contract_for_problem(args.problem_id)
    if contract is None:
        print(f"No contract found for problem: {args.problem_id}")
        sys.exit(1)

    backend = get_backend(contract["backend"])
    print(f"Running {contract['backend']} for {args.problem_id}...")
    verdict = backend.run(contract)

    print(f"Status: {verdict.status}")
    print(f"Summary: {verdict.summary}")
    print(f"Elapsed: {verdict.elapsed_seconds:.1f}s")

    if args.record:
        path = record_attempt(verdict)
        print(f"Attempt recorded: {path}")

    return 0 if verdict.status == "pass" else 1


def cmd_batch(args):
    """Run verification for multiple contracts."""
    contracts = load_all_contracts()
    if args.backend:
        contracts = [c for c in contracts if c["backend"] == args.backend]
    if args.limit:
        contracts = contracts[: args.limit]

    if not contracts:
        print("No contracts found matching criteria.")
        return 0

    results = {"pass": 0, "fail": 0, "error": 0, "timeout": 0, "unknown": 0}

    for contract in contracts:
        pid = contract["problem_id"]
        try:
            backend = get_backend(contract["backend"])
        except ValueError as e:
            print(f"  SKIP {pid}: {e}")
            continue

        print(f"  Running {pid}...", end=" ", flush=True)
        verdict = backend.run(contract)
        results[verdict.status] = results.get(verdict.status, 0) + 1
        status_icon = {"pass": "OK", "fail": "FAIL", "error": "ERR", "timeout": "TIME"}.get(
            verdict.status, "????"
        )
        print(f"{status_icon} ({verdict.elapsed_seconds:.1f}s) {verdict.summary[:80]}")

        if args.record:
            record_attempt(verdict)

    print(f"\nResults: {results}")
    return 0


def cmd_list(args):
    """List all available contracts."""
    contracts = load_all_contracts()
    if not contracts:
        print("No contracts found.")
        return 0

    print(f"{'Problem ID':<60} {'Backend':<16} {'Task Type'}")
    print("-" * 100)
    for c in contracts:
        print(f"{c['problem_id']:<60} {c['backend']:<16} {c['task_type']}")
    print(f"\nTotal: {len(contracts)} contracts")
    return 0


def cmd_check_backends(args):
    """Check which backends are available."""
    for name in list_backends():
        try:
            backend = get_backend(name)
            available = backend.is_available()
        except Exception:
            available = False
        status = "available" if available else "unavailable"
        print(f"  {name}: {status}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="runner",
        description="OpenProblemAtlas verification runner",
    )
    sub = parser.add_subparsers(dest="command")

    # verify
    p_verify = sub.add_parser("verify", help="Verify a single problem")
    p_verify.add_argument("problem_id", help="Problem ID (e.g. opa.mathematics.number-theory.collatz-conjecture)")
    p_verify.add_argument("--record", action="store_true", help="Record result as an attempt")
    p_verify.set_defaults(func=cmd_verify)

    # batch
    p_batch = sub.add_parser("batch", help="Run batch verification")
    p_batch.add_argument("--backend", help="Filter by backend")
    p_batch.add_argument("--limit", type=int, help="Max number of contracts to run")
    p_batch.add_argument("--record", action="store_true", help="Record results as attempts")
    p_batch.set_defaults(func=cmd_batch)

    # list
    p_list = sub.add_parser("list", help="List available contracts")
    p_list.set_defaults(func=cmd_list)

    # check-backends
    p_check = sub.add_parser("check-backends", help="Check backend availability")
    p_check.set_defaults(func=cmd_check_backends)

    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)
