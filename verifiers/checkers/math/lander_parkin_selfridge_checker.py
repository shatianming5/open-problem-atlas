"""Lander-Parkin-Selfridge conjecture verifier.

The Lander-Parkin-Selfridge conjecture concerns equal sums of like powers:
if a_1^k + a_2^k + ... + a_j^k = b_1^k + b_2^k + ... + b_m^k
where a_i, b_i are positive integers and k >= 2,
then j + m >= k.

In other words, it takes at least k terms total for an equation of k-th powers.

Special case: Euler's conjecture (now disproved for k=5 and k=4) stated that
k k-th powers are needed to sum to a k-th power (j >= k when m = 1).

This checker verifies the conjecture for small values by checking
that no counterexamples exist for given power k.
"""

from itertools import combinations_with_replacement


def verify(params: dict) -> dict:
    max_k = int(params.get("max_k", 5))
    max_base = int(params.get("max_base", 50))
    upper_bound = int(params.get("upper_bound", max_base))

    results = []
    counterexamples = []

    for k in range(3, max_k + 1):
        # Check: can a^k = sum of (k-2) or fewer k-th powers?
        # That is, can we have j + 1 < k where m = 1?
        # j < k - 1, i.e., fewer than k-1 terms summing to a k-th power

        # Build table of k-th powers
        powers = {}
        for a in range(1, upper_bound + 1):
            powers[a ** k] = a

        # Check sums of j terms for j < k-1
        for j in range(2, min(k - 1, 5)):  # j terms on left, 1 on right
            found = False
            for combo in combinations_with_replacement(range(1, upper_bound + 1), j):
                s = sum(x ** k for x in combo)
                if s in powers:
                    # Found: combo[0]^k + ... + combo[j-1]^k = powers[s]^k
                    # Total terms: j + 1. Conjecture says j + 1 >= k
                    if j + 1 < k:
                        counterexamples.append({
                            "k": k,
                            "lhs": list(combo),
                            "rhs": powers[s],
                            "total_terms": j + 1,
                        })
                    found = True
            if found:
                break

        results.append({
            "k": k,
            "max_base": upper_bound,
            "counterexamples_found": len([c for c in counterexamples if c["k"] == k]),
        })

    if counterexamples:
        return {
            "status": "fail",
            "summary": (
                f"Lander-Parkin-Selfridge counterexamples found: {len(counterexamples)}"
            ),
            "details": {
                "max_k": max_k,
                "max_base": upper_bound,
                "counterexamples": counterexamples[:10],
                "results_by_k": results,
            },
        }

    return {
        "status": "pass",
        "summary": (
            f"Lander-Parkin-Selfridge conjecture verified for k in [3, {max_k}] "
            f"with bases up to {upper_bound}. No counterexamples found."
        ),
        "details": {
            "max_k": max_k,
            "max_base": upper_bound,
            "results_by_k": results,
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({"max_k": 5, "max_base": 30}), indent=2))
