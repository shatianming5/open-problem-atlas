"""Bunyakovsky conjecture verifier.

Bunyakovsky's conjecture states that an irreducible polynomial f(x) with
integer coefficients and positive leading coefficient, such that gcd of
all f(1), f(2), f(3), ... is 1, takes on infinitely many prime values.

This checker tests several known irreducible polynomials and verifies
that prime values appear among their outputs.
"""

import math


def _is_prime(n: int) -> bool:
    """Check primality by trial division."""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def _gcd_of_values(poly_func, start=1, count=100):
    """Compute gcd of first 'count' positive values of the polynomial."""
    from math import gcd
    g = 0
    for x in range(start, start + count):
        val = poly_func(x)
        if val > 0:
            g = gcd(g, val)
    return g


# Test polynomials: (name, function, irreducibility note)
_TEST_POLYNOMIALS = [
    ("x^2 + 1", lambda x: x * x + 1, "irreducible over Z"),
    ("x^2 + x + 1", lambda x: x * x + x + 1, "irreducible over Z"),
    ("x^2 - x + 1", lambda x: x * x - x + 1, "irreducible over Z"),
    ("x^4 + 1", lambda x: x**4 + 1, "irreducible over Z"),
    ("2x^2 + 1", lambda x: 2 * x * x + 1, "irreducible over Z"),
    ("x^2 + 3", lambda x: x * x + 3, "irreducible, gcd=1 when x runs over Z"),
    ("6x^2 + 5", lambda x: 6 * x * x + 5, "irreducible, gcd=1"),
]


def verify(params: dict) -> dict:
    limit = int(params.get("limit", 10000))
    upper_bound = int(params.get("upper_bound", limit))

    results = []
    all_passed = True

    for name, poly, note in _TEST_POLYNOMIALS:
        # Check the fixed-divisor condition
        g = _gcd_of_values(poly, 1, min(200, upper_bound))

        prime_values = []
        for x in range(1, upper_bound + 1):
            val = poly(x)
            if val > 1 and _is_prime(val):
                prime_values.append({"x": x, "f_x": val})

        count = len(prime_values)
        has_primes = count > 0

        if g > 1:
            # Fixed divisor > 1 means conjecture doesn't apply
            result_status = "skipped"
        elif not has_primes:
            result_status = "no_primes"
            all_passed = False
        else:
            result_status = "primes_found"

        results.append({
            "polynomial": name,
            "status": result_status,
            "gcd_condition": g,
            "prime_count": count,
            "sample_primes": prime_values[:5],
        })

    applicable = [r for r in results if r["status"] != "skipped"]
    primes_found_count = sum(1 for r in applicable if r["status"] == "primes_found")

    if primes_found_count == len(applicable) and len(applicable) > 0:
        return {
            "status": "pass",
            "summary": (
                f"Bunyakovsky conjecture consistent: all {len(applicable)} "
                f"eligible polynomials produce primes up to x={upper_bound}."
            ),
            "details": {
                "upper_bound": upper_bound,
                "polynomials_tested": len(results),
                "polynomials_with_primes": primes_found_count,
                "results": results,
            },
        }

    failed = [r for r in applicable if r["status"] == "no_primes"]
    return {
        "status": "fail",
        "summary": (
            f"Bunyakovsky conjecture: {len(failed)} polynomial(s) "
            f"produced no primes up to x={upper_bound}"
        ),
        "details": {
            "upper_bound": upper_bound,
            "failed_polynomials": failed,
            "results": results,
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({"limit": 1000}), indent=2))
