"""Selfridge's conjecture checker.

Selfridge's conjecture: no prime p exists such that p^2 divides 2^p - 1.
This is related to Wieferich primes (where p^2 | 2^(p-1) - 1).
Checks all primes up to max_n.
"""


def _sieve(limit: int) -> list[int]:
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False
    return [i for i in range(2, limit + 1) if is_prime[i]]


def verify(params: dict) -> dict:
    max_n = int(params.get("max_n", 10000))
    max_n = min(max_n, 100000)

    primes = _sieve(max_n)
    violations = []
    wieferich = []

    for p in primes:
        p2 = p * p
        # Check if p^2 | 2^p - 1
        val = pow(2, p, p2)
        if val == 1:  # means p^2 | 2^p - 1
            violations.append(p)
        # Also check Wieferich: p^2 | 2^(p-1) - 1
        val2 = pow(2, p - 1, p2)
        if val2 == 1:
            wieferich.append(p)

    if violations:
        return {
            "status": "fail",
            "summary": (
                f"Selfridge's conjecture violated: p^2 | 2^p-1 for p={violations}"
            ),
            "details": {"violations": violations},
        }

    return {
        "status": "pass",
        "summary": (
            f"Selfridge's conjecture holds for all {len(primes)} primes up to "
            f"{max_n}. Wieferich primes found: {wieferich if wieferich else 'none'}"
        ),
        "details": {
            "max_n": max_n,
            "primes_checked": len(primes),
            "wieferich_primes": wieferich,
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({}), indent=2))
