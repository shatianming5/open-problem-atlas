"""Agoh-Giuga conjecture verifier.

A Giuga number is a composite number n such that for every prime factor p of n,
p divides (n/p - 1). Equivalently, n is a Giuga number if
sum(1/p for p | n) - product(1/p for p | n) is an integer.

The Agoh-Giuga conjecture states that n is a Giuga number if and only if
n * B(phi(n)) = -1 (mod n), where B is the Bernoulli number. A weaker
related conjecture is that no Giuga number exists.

No Giuga numbers are known. This checker searches for them up to upper_bound.
"""


def _smallest_factor(n: int) -> int:
    """Return the smallest prime factor of n."""
    if n % 2 == 0:
        return 2
    i = 3
    while i * i <= n:
        if n % i == 0:
            return i
        i += 2
    return n


def _factorize(n: int) -> list[int]:
    """Return the list of prime factors of n (with multiplicity)."""
    factors = []
    while n > 1:
        p = _smallest_factor(n)
        while n % p == 0:
            factors.append(p)
            n //= p
    return factors


def _prime_factors(n: int) -> set[int]:
    """Return the set of distinct prime factors of n."""
    return set(_factorize(n))


def _is_giuga(n: int) -> bool:
    """Check if n is a Giuga number.

    n must be composite. For each prime factor p of n:
    p | (n/p - 1).
    Also, n must be squarefree (all known theoretical Giuga numbers must be).
    """
    factors = _factorize(n)
    distinct = set(factors)

    # Must be squarefree
    if len(factors) != len(distinct):
        return False

    # Must have at least 2 prime factors (composite)
    if len(distinct) < 2:
        return False

    for p in distinct:
        if (n // p - 1) % p != 0:
            return False
    return True


def verify(params: dict) -> dict:
    upper_bound = int(params.get("upper_bound", 100000))

    checked = 0
    giuga_numbers = []

    for n in range(2, upper_bound + 1):
        # Skip primes (quick check)
        if _smallest_factor(n) == n:
            continue
        checked += 1
        if _is_giuga(n):
            giuga_numbers.append(n)

    if giuga_numbers:
        return {
            "status": "fail",
            "summary": f"Giuga numbers found: {giuga_numbers}",
            "details": {
                "upper_bound": upper_bound,
                "composites_checked": checked,
                "giuga_numbers": giuga_numbers,
            },
        }

    return {
        "status": "pass",
        "summary": (
            f"No Giuga numbers found up to {upper_bound}. "
            f"Checked {checked} composite numbers."
        ),
        "details": {
            "upper_bound": upper_bound,
            "composites_checked": checked,
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({"upper_bound": 100000}), indent=2))
