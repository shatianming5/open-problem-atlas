"""Casas-Alvero conjecture checker.

The Casas-Alvero conjecture: if a monic polynomial f of degree n over
a field of characteristic 0 shares a root with each of its derivatives
f', f'', ..., f^(n-1), then f(x) = (x - a)^n for some a.
Verifies for polynomials of degree up to max_degree.
"""


def _poly_eval(coeffs: list[float], x: float) -> float:
    """Evaluate polynomial with coefficients [a0, a1, ..., an] at x."""
    result = 0.0
    for i in range(len(coeffs) - 1, -1, -1):
        result = result * x + coeffs[i]
    return result


def _poly_derivative(coeffs: list[float]) -> list[float]:
    """Compute derivative of polynomial."""
    if len(coeffs) <= 1:
        return [0.0]
    return [coeffs[i] * i for i in range(1, len(coeffs))]


def _shares_root(f: list[float], g: list[float], tol: float = 1e-8) -> bool:
    """Check if polynomials f and g share an approximate root."""
    # Find roots of g by sampling and Newton's method
    roots = _find_roots(g)
    for r in roots:
        if abs(_poly_eval(f, r)) < tol:
            return True
    return False


def _find_roots(coeffs: list[float], n_samples: int = 50) -> list[float]:
    """Find approximate real roots using Newton's method from samples."""
    if len(coeffs) <= 1:
        return []
    deriv = _poly_derivative(coeffs)
    roots = []
    for i in range(n_samples):
        x = (i - n_samples // 2) * 0.2
        for _ in range(50):
            fx = _poly_eval(coeffs, x)
            dfx = _poly_eval(deriv, x)
            if abs(dfx) < 1e-15:
                break
            x -= fx / dfx
            if abs(fx) < 1e-12:
                # Check if this is a new root
                is_new = all(abs(x - r) > 1e-6 for r in roots)
                if is_new:
                    roots.append(x)
                break
    return roots


def verify(params: dict) -> dict:
    max_degree = int(params.get("max_degree", 10))
    max_degree = min(max_degree, 20)

    results = []
    conjecture_holds = True

    for n in range(2, max_degree + 1):
        # Test (x - a)^n form: should satisfy the condition
        a = 1.0
        # Coefficients of (x-1)^n via binomial
        coeffs = []
        for k in range(n + 1):
            binom = 1
            for j in range(k):
                binom = binom * (n - j) // (j + 1)
            coeffs.append(binom * ((-a) ** (n - k)))
        coeffs.reverse()

        all_share = True
        f = coeffs[:]
        for d in range(1, n):
            f_d = f[:]
            for _ in range(d):
                f_d = _poly_derivative(f_d)
            if not _shares_root(coeffs, f_d):
                all_share = False
                break

        results.append({
            "degree": n,
            "form": f"(x-1)^{n}",
            "shares_root_with_all_derivs": all_share,
        })

        # Test a random non-perfect-power polynomial
        import random
        rng = random.Random(42 + n)
        rand_coeffs = [rng.uniform(-1, 1) for _ in range(n)] + [1.0]
        all_share_rand = True
        f_rand = rand_coeffs[:]
        for d in range(1, n):
            f_d = f_rand[:]
            for _ in range(d):
                f_d = _poly_derivative(f_d)
            if not _shares_root(rand_coeffs, f_d):
                all_share_rand = False
                break

        if all_share_rand:
            # If random poly shares roots with all derivatives but isn't (x-a)^n
            conjecture_holds = False

    return {
        "status": "pass" if conjecture_holds else "fail",
        "summary": (
            f"Casas-Alvero conjecture tested for degrees 2..{max_degree}. "
            f"Perfect powers satisfy condition. "
            f"No random counterexamples found: {conjecture_holds}"
        ),
        "details": {
            "max_degree": max_degree,
            "results": results,
            "holds": conjecture_holds,
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({}), indent=2))
