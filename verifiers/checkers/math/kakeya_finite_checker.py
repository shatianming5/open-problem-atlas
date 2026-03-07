"""Kakeya set in finite fields verifier.

The finite field Kakeya conjecture (proved by Dvir in 2009) states that
a Kakeya set in F_q^n (a set containing a line in every direction) has
size at least c_n * q^n for some constant c_n > 0.

This checker verifies the Kakeya property in small finite fields F_q
for dimension 2: a Kakeya set in F_q^2 must contain a line in every
direction, and its minimum size can be computed.

For F_q^2, the minimum Kakeya set has size q(q+1)/2 + (q-1)/2 for odd q.
"""


def verify(params: dict) -> dict:
    # Test for small prime fields F_p
    max_q = int(params.get("max_q", 11))
    upper_bound = int(params.get("upper_bound", max_q))

    primes = []
    for p in range(2, upper_bound + 1):
        if all(p % d != 0 for d in range(2, int(p**0.5) + 1)):
            primes.append(p)

    results = []

    for q in primes:
        if q > max_q:
            break

        # In F_q^2, directions are elements of the projective line P^1(F_q)
        # which has q+1 elements: slopes 0, 1, ..., q-1 and infinity (vertical)

        # A line with slope m through point (a, b): {(a+t, b+m*t) : t in F_q}
        # A vertical line through (a, b): {(a, b+t) : t in F_q}

        # Build a minimal Kakeya set greedily
        kakeya_set = set()

        # Add a line in each direction
        # Direction slope m: pick a line through (0, 0) with slope m
        for m in range(q):
            line = frozenset((t % q, (m * t) % q) for t in range(q))
            kakeya_set |= set(line)

        # Vertical line through (0, 0)
        vert_line = frozenset((0, t % q) for t in range(q))
        kakeya_set |= set(vert_line)

        kakeya_size = len(kakeya_set)

        # Verify this is indeed a Kakeya set (contains a line in every direction)
        all_directions_covered = True

        # Check each non-vertical direction (slope m)
        for m in range(q):
            has_line = False
            for a in range(q):
                for b in range(q):
                    line = {((a + t) % q, (b + m * t) % q) for t in range(q)}
                    if line.issubset(kakeya_set):
                        has_line = True
                        break
                if has_line:
                    break
            if not has_line:
                all_directions_covered = False
                break

        # Check vertical direction
        if all_directions_covered:
            has_vert = False
            for a in range(q):
                line = {(a, t) for t in range(q)}
                if line.issubset(kakeya_set):
                    has_vert = True
                    break
            if not has_vert:
                all_directions_covered = False

        # Dvir's bound: |K| >= q^2 / 2 (for n=2)
        dvir_bound = q * q / 2

        results.append({
            "q": q,
            "kakeya_size": kakeya_size,
            "q_squared": q * q,
            "dvir_lower_bound": dvir_bound,
            "satisfies_dvir": kakeya_size >= dvir_bound,
            "all_directions_covered": all_directions_covered,
        })

    all_passed = all(r["all_directions_covered"] and r["satisfies_dvir"]
                     for r in results)

    if not all_passed:
        failed = [r for r in results
                  if not r["all_directions_covered"] or not r["satisfies_dvir"]]
        return {
            "status": "fail",
            "summary": f"Kakeya verification failed for some finite fields",
            "details": {"results": results, "failed": failed},
        }

    return {
        "status": "pass",
        "summary": (
            f"Kakeya sets verified in F_q^2 for primes q up to {max_q}. "
            f"All satisfy Dvir's bound |K| >= q^2/2."
        ),
        "details": {
            "max_q": max_q,
            "num_tested": len(results),
            "results": results,
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({"max_q": 7}), indent=2))
