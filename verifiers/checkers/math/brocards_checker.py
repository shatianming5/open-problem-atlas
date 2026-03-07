"""Brocard's problem verifier.

Brocard's problem asks: for which n is n! + 1 a perfect square?
The only known solutions are n = 4, 5, 7 (giving 5^2, 11^2 - wait, let's
be precise: 4!+1=25=5^2, 5!+1=121=11^2, 7!+1=5041=71^2).
It is conjectured that no other solutions exist.

This checker verifies by searching for n where n! + 1 is a perfect square.
"""

import math


def _is_perfect_square(n: int) -> bool:
    """Check if n is a perfect square."""
    if n < 0:
        return False
    r = math.isqrt(n)
    return r * r == n


def verify(params: dict) -> dict:
    upper_bound = int(params.get("upper_bound", 200))

    known_solutions = {4, 5, 7}
    found_solutions = []
    factorial = 1

    for n in range(1, upper_bound + 1):
        factorial *= n
        val = factorial + 1
        if _is_perfect_square(val):
            sq = math.isqrt(val)
            found_solutions.append({"n": n, "n_factorial_plus_1": val, "sqrt": sq})

    found_ns = {s["n"] for s in found_solutions}

    # Check that we found exactly the known solutions (up to our search range)
    expected = known_solutions & set(range(1, upper_bound + 1))
    unexpected = found_ns - known_solutions

    if unexpected:
        return {
            "status": "fail",
            "summary": (
                f"New Brocard solutions found beyond {{4,5,7}}: {unexpected}. "
                "This would disprove the conjecture!"
            ),
            "details": {
                "upper_bound": upper_bound,
                "solutions": found_solutions,
                "unexpected": list(unexpected),
            },
        }

    if found_ns != expected:
        return {
            "status": "error",
            "summary": f"Missing expected known solutions; found {found_ns}, expected {expected}",
            "details": {"found": list(found_ns), "expected": list(expected)},
        }

    return {
        "status": "pass",
        "summary": (
            f"Brocard's problem checked for n in [1, {upper_bound}]. "
            f"Only known solutions (4, 5, 7) found."
        ),
        "details": {
            "upper_bound": upper_bound,
            "solutions": found_solutions,
            "checked": upper_bound,
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({"upper_bound": 200}), indent=2))
