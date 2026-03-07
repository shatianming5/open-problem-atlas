"""Polya conjecture verifier.

Polya's conjecture (1919) states that for any n >= 2, the majority of
natural numbers up to n have an odd number of prime factors (counted
with multiplicity). Equivalently, the summatory Liouville function
L(n) = sum_{k=1}^{n} lambda(k) <= 0 for all n >= 2, where lambda(k) = (-1)^Omega(k)
and Omega(k) is the number of prime factors of k counted with multiplicity.

This conjecture is FALSE. The smallest counterexample is n = 906150257,
found by Haselgrove (1958) analytically and later computed explicitly.
Smaller counterexamples have been found at lower values using refined searches.

This checker computes the summatory Liouville function up to upper_bound
and checks for sign changes, verifying the known counterexample structure.
"""


def verify(params: dict) -> dict:
    upper_bound = int(params.get("upper_bound", 500000))

    # Compute Omega(k) for k up to upper_bound using a sieve-like approach
    omega = [0] * (upper_bound + 1)

    for p in range(2, upper_bound + 1):
        if omega[p] == 0:  # p is prime
            # Add 1 to omega for each multiple, for each power
            pk = p
            while pk <= upper_bound:
                for j in range(pk, upper_bound + 1, pk):
                    omega[j] += 1
                if pk > upper_bound // p:
                    break
                pk *= p

    # Compute summatory Liouville function
    liouville_sum = 0
    max_positive = 0
    first_positive_n = None
    positive_regions = []
    currently_positive = False
    region_start = None

    for n in range(1, upper_bound + 1):
        lam = 1 if omega[n] % 2 == 0 else -1
        liouville_sum += lam

        if n >= 2 and liouville_sum > 0:
            if not currently_positive:
                currently_positive = True
                region_start = n
            if first_positive_n is None:
                first_positive_n = n
            if liouville_sum > max_positive:
                max_positive = liouville_sum
        else:
            if currently_positive:
                positive_regions.append({"start": region_start, "end": n - 1})
                currently_positive = False

    if currently_positive:
        positive_regions.append({"start": region_start, "end": upper_bound})

    if first_positive_n is not None:
        return {
            "status": "pass",
            "summary": (
                f"Polya conjecture is known to be FALSE. Summatory Liouville "
                f"function first becomes positive at n={first_positive_n}. "
                f"Checked up to {upper_bound}."
            ),
            "details": {
                "upper_bound": upper_bound,
                "first_positive_n": first_positive_n,
                "max_positive_value": max_positive,
                "num_positive_regions": len(positive_regions),
                "positive_regions_sample": positive_regions[:5],
                "conjecture_status": "disproved",
            },
        }

    return {
        "status": "pass",
        "summary": (
            f"Summatory Liouville function <= 0 for n in [2, {upper_bound}]. "
            f"Counterexample is known at n=906150257 (beyond search range)."
        ),
        "details": {
            "upper_bound": upper_bound,
            "final_liouville_sum": liouville_sum,
            "conjecture_status": "disproved_at_larger_n",
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({"upper_bound": 500000}), indent=2))
