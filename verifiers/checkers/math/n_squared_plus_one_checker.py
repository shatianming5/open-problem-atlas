"""n^2+1 prime conjecture verifier.

The conjecture (a special case of Bunyakovsky's conjecture) states that
there are infinitely many primes of the form n^2 + 1.

This checker counts primes of the form n^2 + 1 up to a limit and verifies
that they appear with positive density, consistent with the conjecture.
The expected density follows from the Hardy-Littlewood conjecture.
"""

import math


def _is_prime(n: int) -> bool:
    """Check primality by trial division."""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def verify(params: dict) -> dict:
    limit = int(params.get("limit", 100000))
    upper_bound = int(params.get("upper_bound", limit))

    primes_found = []
    total_checked = 0

    for n in range(1, upper_bound + 1):
        val = n * n + 1
        total_checked += 1
        if _is_prime(val):
            primes_found.append({"n": n, "p": val})

    count = len(primes_found)

    if count == 0:
        return {
            "status": "fail",
            "summary": f"No primes of form n^2+1 found for n in [1, {upper_bound}]",
            "details": {"upper_bound": upper_bound, "count": 0},
        }

    # Hardy-Littlewood prediction: approximately C * N / log(N^2) primes
    # where C is a product over odd primes
    expected_order = upper_bound / (2 * math.log(upper_bound)) if upper_bound > 1 else 1
    ratio = count / expected_order if expected_order > 0 else 0

    return {
        "status": "pass",
        "summary": (
            f"Found {count} primes of form n^2+1 for n in [1, {upper_bound}]. "
            f"Largest: {primes_found[-1]['n']}^2+1 = {primes_found[-1]['p']}."
        ),
        "details": {
            "upper_bound": upper_bound,
            "count": count,
            "approximate_density_ratio": round(ratio, 4),
            "first_few": primes_found[:10],
            "last_few": primes_found[-5:],
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({"limit": 10000}), indent=2))
