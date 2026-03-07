"""Lehmer's totient problem verifier.

Lehmer's totient problem asks whether there exists a composite number n
such that Euler's totient function phi(n) divides n-1.
It is known that if such n exists, it must be a Carmichael number and
must be odd and squarefree with at least 14 prime factors.

No such composite number is known. This checker searches for one up to
upper_bound.
"""

import math


def _sieve(limit: int) -> list[bool]:
    """Sieve of Eratosthenes."""
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False
    return is_prime


def _euler_totient(n: int) -> int:
    """Compute Euler's totient function phi(n)."""
    result = n
    p = 2
    temp = n
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            result -= result // p
        p += 1
    if temp > 1:
        result -= result // temp
    return result


def verify(params: dict) -> dict:
    upper_bound = int(params.get("upper_bound", 100000))

    is_prime = _sieve(upper_bound)
    checked = 0
    lehmer_numbers = []

    for n in range(2, upper_bound + 1):
        if is_prime[n]:
            continue  # Skip primes; for primes, phi(p) = p-1 always divides p-1
        checked += 1
        phi_n = _euler_totient(n)
        if (n - 1) % phi_n == 0:
            lehmer_numbers.append({"n": n, "phi_n": phi_n})

    if lehmer_numbers:
        return {
            "status": "fail",
            "summary": (
                f"Found composite n where phi(n) | (n-1): "
                f"{[x['n'] for x in lehmer_numbers]}"
            ),
            "details": {
                "upper_bound": upper_bound,
                "composites_checked": checked,
                "lehmer_numbers": lehmer_numbers,
            },
        }

    return {
        "status": "pass",
        "summary": (
            f"No composite n with phi(n) | (n-1) found up to {upper_bound}. "
            f"Checked {checked} composites."
        ),
        "details": {
            "upper_bound": upper_bound,
            "composites_checked": checked,
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({"upper_bound": 100000}), indent=2))
