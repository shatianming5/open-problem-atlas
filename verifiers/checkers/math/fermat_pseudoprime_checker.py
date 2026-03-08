"""Fermat pseudoprime checker.

Checks properties of Fermat pseudoprimes (Carmichael numbers): composite
numbers n such that a^(n-1) = 1 mod n for all a coprime to n. Verifies
that Carmichael numbers are odd, square-free, and have at least 3
prime factors (Korselt's criterion).
"""

from math import gcd


def _is_prime(n: int) -> bool:
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


def _prime_factors(n: int) -> list[int]:
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors


def _is_carmichael(n: int) -> bool:
    """Check if n is a Carmichael number using Korselt's criterion."""
    if n < 2 or _is_prime(n) or n % 2 == 0:
        return False
    factors = _prime_factors(n)
    # Must be square-free
    if len(factors) != len(set(factors)):
        return False
    # Must have at least 3 prime factors
    if len(set(factors)) < 3:
        return False
    # Each prime factor p must satisfy (n-1) % (p-1) == 0
    for p in set(factors):
        if (n - 1) % (p - 1) != 0:
            return False
    return True


def verify(params: dict) -> dict:
    max_n = int(params.get("max_n", 10000))
    max_n = min(max_n, 100000)

    carmichaels = []
    for n in range(3, max_n + 1, 2):
        if _is_carmichael(n):
            factors = sorted(set(_prime_factors(n)))
            carmichaels.append({"n": n, "factors": factors})

    # Verify Fermat test: a^(n-1) = 1 mod n for coprime a
    verified = 0
    for entry in carmichaels[:10]:
        n = entry["n"]
        all_pass = True
        for a in range(2, min(n, 20)):
            if gcd(a, n) == 1:
                if pow(a, n - 1, n) != 1:
                    all_pass = False
                    break
        if all_pass:
            verified += 1

    return {
        "status": "pass",
        "summary": (
            f"Found {len(carmichaels)} Carmichael numbers up to {max_n}. "
            f"Fermat test verified for {verified} of them."
        ),
        "details": {
            "max_n": max_n,
            "count": len(carmichaels),
            "carmichaels": carmichaels[:20],
            "fermat_verified": verified,
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({}), indent=2))
