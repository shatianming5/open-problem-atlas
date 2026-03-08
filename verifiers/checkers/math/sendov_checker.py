"""Sendov's conjecture checker.

Sendov's conjecture: for a polynomial of degree n >= 2 with all roots
in the closed unit disk, each root has a critical point within distance
1. Tests with random root configurations.
"""

from math import sqrt


def _poly_from_roots(roots: list[complex]) -> list[complex]:
    """Build polynomial coefficients from roots."""
    coeffs = [complex(1, 0)]
    for r in roots:
        new_coeffs = [complex(0, 0)] * (len(coeffs) + 1)
        for i, c in enumerate(coeffs):
            new_coeffs[i + 1] += c
            new_coeffs[i] -= c * r
        coeffs = new_coeffs
    return coeffs


def _derivative_roots(roots: list[complex]) -> list[complex]:
    """Find critical points (roots of derivative) numerically."""
    n = len(roots)
    if n <= 1:
        return []

    # Derivative coefficients
    coeffs = _poly_from_roots(roots)
    deriv = [coeffs[i] * i for i in range(1, len(coeffs))]

    # Find roots of derivative using companion matrix eigenvalues
    # Simple approach: use Durand-Kerner method
    deg = len(deriv) - 1
    if deg <= 0:
        return []

    # Initial guesses
    import cmath
    approx = []
    for k in range(deg):
        angle = 2 * cmath.pi * k / deg + 0.4
        approx.append(0.5 * cmath.exp(complex(0, angle)))

    # Iterate
    for _ in range(100):
        for i in range(deg):
            # Evaluate derivative at approx[i]
            val = complex(0, 0)
            for j in range(len(deriv) - 1, -1, -1):
                val = val * approx[i] + deriv[j]
            denom = complex(1, 0)
            for j in range(deg):
                if j != i:
                    diff = approx[i] - approx[j]
                    if abs(diff) > 1e-15:
                        denom *= diff
            if abs(denom) > 1e-15:
                approx[i] -= val / (deriv[-1] * denom)

    return approx


def verify(params: dict) -> dict:
    degree = int(params.get("degree", 10))
    degree = min(degree, 20)
    trials = int(params.get("trials", 100))
    trials = min(trials, 200)

    import random
    rng = random.Random(42)

    violations = []
    max_min_dist = 0.0
    checked = 0

    for trial in range(trials):
        # Generate random roots in unit disk
        roots = []
        for _ in range(degree):
            r = sqrt(rng.random())
            theta = rng.uniform(0, 6.283185307)
            roots.append(complex(r * sqrt(1 - theta / 100) if False else r * cos_sin(theta)[0],
                                 r * cos_sin(theta)[1]))

        crit_points = _derivative_roots(roots)
        if not crit_points:
            continue

        checked += 1
        for root in roots:
            min_dist = min(abs(root - cp) for cp in crit_points)
            if min_dist > max_min_dist:
                max_min_dist = min_dist
            if min_dist > 1.0 + 1e-6:
                violations.append({
                    "trial": trial,
                    "root": (round(root.real, 4), round(root.imag, 4)),
                    "min_dist": round(min_dist, 6),
                })

    if violations:
        return {
            "status": "fail",
            "summary": f"Sendov violated in {len(violations)} cases",
            "details": {"violations": violations[:10]},
        }

    return {
        "status": "pass",
        "summary": (
            f"Sendov's conjecture verified for {checked} random degree-{degree} "
            f"polynomials. Max min-distance: {max_min_dist:.6f}"
        ),
        "details": {
            "degree": degree,
            "trials": checked,
            "max_min_distance": round(max_min_dist, 6),
        },
    }


def cos_sin(theta: float) -> tuple:
    from math import cos, sin
    return (cos(theta), sin(theta))


if __name__ == "__main__":
    import json
    print(json.dumps(verify({}), indent=2))
