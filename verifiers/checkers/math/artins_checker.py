"""Artin's conjecture on primitive roots checker.

Artin's conjecture: every integer a that is not -1 or a perfect square
is a primitive root modulo infinitely many primes. This checker tests
whether 2 is a primitive root for primes up to max_n.
"""


def _sieve(limit: int) -> list[int]:
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False
    return [i for i in range(2, limit + 1) if is_prime[i]]


def _is_primitive_root(a: int, p: int) -> bool:
    """Check if a is a primitive root mod p."""
    if p == 2:
        return a % 2 == 1
    order = p - 1
    # Factor p-1
    temp = order
    factors = set()
    d = 2
    while d * d <= temp:
        while temp % d == 0:
            factors.add(d)
            temp //= d
        d += 1
    if temp > 1:
        factors.add(temp)
    # a is primitive root iff a^((p-1)/q) != 1 mod p for all prime q | p-1
    for q in factors:
        if pow(a, order // q, p) == 1:
            return False
    return True


def verify(params: dict) -> dict:
    max_n = int(params.get("max_n", 1000))
    max_n = min(max_n, 10000)

    primes = _sieve(max_n)
    prim_root_count = 0
    non_prim_root = []

    for p in primes:
        if p == 2:
            continue
        if _is_primitive_root(2, p):
            prim_root_count += 1
        else:
            non_prim_root.append(p)

    total = len(primes) - 1  # exclude p=2
    fraction = prim_root_count / total if total > 0 else 0
    # Artin's constant ~ 0.3739558136
    artin_const = 0.3739558136

    return {
        "status": "pass",
        "summary": (
            f"2 is primitive root for {prim_root_count}/{total} odd primes "
            f"up to {max_n} ({fraction:.4f}, Artin's constant={artin_const:.4f})"
        ),
        "details": {
            "max_n": max_n,
            "primitive_root_count": prim_root_count,
            "total_odd_primes": total,
            "fraction": round(fraction, 6),
            "artin_constant": artin_const,
            "first_non_prim_roots": non_prim_root[:20],
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({}), indent=2))
