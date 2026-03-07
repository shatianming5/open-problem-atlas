"""Twin prime conjecture verifier.

Twin primes are pairs of primes (p, p+2). The twin prime conjecture states
that there are infinitely many such pairs. This checker counts twin prime
pairs up to upper_bound and verifies they exist in the range.
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
    upper_bound = int(params.get("upper_bound", 10**6))

    is_prime = _sieve(upper_bound + 2)
    twin_pairs = []

    for p in range(2, upper_bound + 1):
        if p + 2 <= upper_bound + 2 and is_prime[p] and is_prime[p + 2]:
            twin_pairs.append((p, p + 2))

    count = len(twin_pairs)

    if count == 0:
        return {
            "status": "fail",
            "summary": f"No twin prime pairs found up to {upper_bound}",
            "details": {"upper_bound": upper_bound, "count": 0},
        }

    largest_pair = twin_pairs[-1]

    return {
        "status": "pass",
        "summary": (
            f"Found {count} twin prime pairs up to {upper_bound}. "
            f"Largest pair: ({largest_pair[0]}, {largest_pair[1]})"
        ),
        "details": {
            "upper_bound": upper_bound,
            "count": count,
            "largest_pair": list(largest_pair),
            "first_few_pairs": [list(p) for p in twin_pairs[:10]],
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({"upper_bound": 100000}), indent=2))
