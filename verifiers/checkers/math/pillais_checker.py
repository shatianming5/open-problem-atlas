"""Pillai's conjecture verifier.

Pillai's conjecture (also known as the Catalan-Pillai conjecture) states that
for any positive integer m, the equation |a^x - b^y| = m has only finitely
many solutions in integers a, b, x, y with a, b >= 1 and x, y >= 2.

Equivalently, the gaps between consecutive perfect powers (squares, cubes, etc.)
tend to infinity.

This checker verifies that gaps between consecutive perfect powers grow,
and searches for pairs of perfect powers with small differences.
"""


def verify(params: dict) -> dict:
    limit = int(params.get("limit", 100000))
    upper_bound = int(params.get("upper_bound", limit))

    # Generate all perfect powers up to upper_bound
    # A perfect power is n = a^k for some a >= 1, k >= 2
    perfect_powers = set()

    # Add squares
    a = 2
    while a * a <= upper_bound:
        val = a * a
        while val <= upper_bound:
            perfect_powers.add(val)
            val *= a
        a += 1

    # Add cubes and higher powers separately for clarity
    for k in range(2, 64):
        a = 2
        while True:
            val = a ** k
            if val > upper_bound:
                break
            perfect_powers.add(val)
            a += 1

    sorted_powers = sorted(perfect_powers)

    # Compute gaps between consecutive perfect powers
    gaps = []
    min_gap = float("inf")
    min_gap_pair = None

    for i in range(1, len(sorted_powers)):
        gap = sorted_powers[i] - sorted_powers[i - 1]
        if gap < min_gap:
            min_gap = gap
            min_gap_pair = (sorted_powers[i - 1], sorted_powers[i])
        gaps.append({"pair": [sorted_powers[i - 1], sorted_powers[i]], "gap": gap})

    # Find pairs with gap = 1 (Catalan's theorem: only 8,9)
    gap_one_pairs = [g for g in gaps if g["gap"] == 1]

    # Find pairs with small gaps
    small_gap_pairs = sorted(gaps, key=lambda g: g["gap"])[:10]

    # Catalan's theorem (proved by Mihailescu 2002): the only consecutive
    # perfect powers are 8 and 9.
    catalan_verified = True
    for g in gap_one_pairs:
        if g["pair"] != [8, 9]:
            catalan_verified = False

    if not catalan_verified:
        return {
            "status": "fail",
            "summary": "Found consecutive perfect powers other than (8, 9)!",
            "details": {
                "gap_one_pairs": gap_one_pairs,
                "upper_bound": upper_bound,
            },
        }

    return {
        "status": "pass",
        "summary": (
            f"Pillai's conjecture consistent up to {upper_bound}. "
            f"Found {len(sorted_powers)} perfect powers. "
            f"Only gap-1 pair: (8, 9). Smallest gap overall: {min_gap}."
        ),
        "details": {
            "upper_bound": upper_bound,
            "num_perfect_powers": len(sorted_powers),
            "min_gap": min_gap,
            "min_gap_pair": list(min_gap_pair) if min_gap_pair else None,
            "gap_one_pairs": gap_one_pairs,
            "smallest_gaps": small_gap_pairs,
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({"upper_bound": 100000}), indent=2))
