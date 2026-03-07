"""Goldbach conjecture checker.

Goldbach's conjecture: every even integer >= 4 is the sum of two primes.
Verifies for all even numbers up to `upper_bound`.
"""


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
    upper_bound = int(params.get("upper_bound", 10**7))

    is_prime = _sieve(upper_bound)
    checked = 0

    for n in range(4, upper_bound + 1, 2):
        found = False
        for p in range(2, n // 2 + 1):
            if is_prime[p] and is_prime[n - p]:
                found = True
                break
        if not found:
            return {
                "status": "fail",
                "summary": f"Goldbach conjecture fails for n={n}",
                "details": {"counterexample": n},
            }
        checked += 1

    return {
        "status": "pass",
        "summary": f"Goldbach conjecture verified for all even numbers in [4, {upper_bound}] ({checked} checked)",
        "details": {"upper_bound": upper_bound, "checked": checked},
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({"upper_bound": 100000}), indent=2))
