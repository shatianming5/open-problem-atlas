"""Erdos-Mollin-Walsh conjecture verifier.

The Erdos-Mollin-Walsh conjecture states that there are no three consecutive
powerful numbers. A powerful number (also called squareful) is a positive
integer n such that for every prime p dividing n, p^2 also divides n.
Equivalently, n = a^2 * b^3 for some integers a, b >= 1.

This checker searches for three consecutive powerful numbers up to upper_bound.
"""


def _is_powerful(n: int) -> bool:
    """Check if n is a powerful number.

    n is powerful if p^2 | n for every prime p | n.
    """
    if n <= 0:
        return False
    if n == 1:
        return True

    temp = n
    d = 2
    while d * d <= temp:
        if temp % d == 0:
            if temp % (d * d) != 0:
                return False
            while temp % d == 0:
                temp //= d
        d += 1
    # If temp > 1, then there's a prime factor > sqrt(n) that appears only once
    if temp > 1:
        return False
    return True


def verify(params: dict) -> dict:
    upper_bound = int(params.get("upper_bound", 1000000))

    # Find all powerful numbers up to upper_bound
    powerful = set()
    for n in range(1, upper_bound + 1):
        if _is_powerful(n):
            powerful.add(n)

    # Look for three consecutive powerful numbers
    triples = []
    for n in sorted(powerful):
        if n + 1 in powerful and n + 2 in powerful:
            triples.append((n, n + 1, n + 2))

    # Also find consecutive pairs (these do exist)
    pairs = []
    for n in sorted(powerful):
        if n + 1 in powerful:
            pairs.append((n, n + 1))

    if triples:
        return {
            "status": "fail",
            "summary": (
                f"Erdos-Mollin-Walsh conjecture violated: "
                f"found {len(triples)} triple(s) of consecutive powerful numbers"
            ),
            "details": {
                "upper_bound": upper_bound,
                "triples": [list(t) for t in triples[:10]],
                "num_powerful": len(powerful),
            },
        }

    return {
        "status": "pass",
        "summary": (
            f"Erdos-Mollin-Walsh conjecture verified up to {upper_bound}. "
            f"Found {len(powerful)} powerful numbers, {len(pairs)} consecutive pairs, "
            f"no consecutive triples."
        ),
        "details": {
            "upper_bound": upper_bound,
            "num_powerful": len(powerful),
            "consecutive_pairs_count": len(pairs),
            "sample_pairs": [list(p) for p in pairs[:10]],
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({"upper_bound": 100000}), indent=2))
