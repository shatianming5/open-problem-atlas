"""Legendre's conjecture verifier.

Legendre's conjecture: for every positive integer n, there exists a prime
between n^2 and (n+1)^2. This checker verifies the conjecture for all n
up to upper_bound by sieving primes and checking each interval.
"""

import math


def _sieve(limit: int) -> list[bool]:
    """Sieve of Eratosthenes returning boolean array."""
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False
    return is_prime


def verify(params: dict) -> dict:
    upper_bound = int(params.get("upper_bound", 1000))

    # We need primes up to (upper_bound+1)^2
    sieve_limit = (upper_bound + 1) ** 2
    is_prime = _sieve(sieve_limit)

    checked = 0
    primes_found = []

    for n in range(1, upper_bound + 1):
        lo = n * n
        hi = (n + 1) * (n + 1)
        found = False
        for k in range(lo + 1, hi):
            if is_prime[k]:
                found = True
                if len(primes_found) < 10:
                    primes_found.append({"n": n, "prime": k, "interval": [lo, hi]})
                break
        if not found:
            return {
                "status": "fail",
                "summary": f"Legendre's conjecture fails: no prime in ({lo}, {hi}) for n={n}",
                "details": {"counterexample_n": n, "interval": [lo, hi]},
            }
        checked += 1

    return {
        "status": "pass",
        "summary": (
            f"Legendre's conjecture verified for n in [1, {upper_bound}]. "
            f"All {checked} intervals contain a prime."
        ),
        "details": {
            "upper_bound": upper_bound,
            "checked": checked,
            "sample_primes": primes_found,
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({"upper_bound": 500}), indent=2))
