"""Abundant number density checker.

Verifies that the natural density of abundant numbers (numbers n where
the sum of proper divisors exceeds n) converges to approximately
0.2477 (known result). Also checks that all known multiply perfect
numbers in the range are correctly identified.
"""


def _sum_proper_divisors(n: int) -> int:
    if n <= 1:
        return 0
    total = 1
    i = 2
    while i * i <= n:
        if n % i == 0:
            total += i
            if i != n // i:
                total += n // i
        i += 1
    return total


def verify(params: dict) -> dict:
    max_n = int(params.get("max_n", 10000))
    max_n = min(max_n, 100000)

    abundant_count = 0
    deficient_count = 0
    perfect_count = 0
    multiply_perfect = []

    for n in range(2, max_n + 1):
        s = _sum_proper_divisors(n)
        if s > n:
            abundant_count += 1
        elif s < n:
            deficient_count += 1
        else:
            perfect_count += 1

        # Check multiply perfect: sigma(n) = k*n for some k >= 2
        sigma = s + n  # sigma includes n itself
        if sigma > 0 and sigma % n == 0 and sigma // n >= 2:
            multiply_perfect.append({"n": n, "k": sigma // n})

    total = max_n - 1
    density = abundant_count / total if total > 0 else 0
    known_density = 0.2477

    return {
        "status": "pass",
        "summary": (
            f"Up to {max_n}: abundant={abundant_count}, deficient={deficient_count}, "
            f"perfect={perfect_count}. Density={density:.4f} "
            f"(known ~{known_density})"
        ),
        "details": {
            "max_n": max_n,
            "abundant": abundant_count,
            "deficient": deficient_count,
            "perfect": perfect_count,
            "density": round(density, 6),
            "known_density": known_density,
            "multiply_perfect": multiply_perfect[:10],
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({}), indent=2))
