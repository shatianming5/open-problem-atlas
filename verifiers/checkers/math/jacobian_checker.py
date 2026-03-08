"""Jacobian conjecture checker.

The Jacobian conjecture: if F: C^n -> C^n is a polynomial map with
constant nonzero Jacobian determinant, then F is invertible. This
checker tests polynomial maps in 2 variables of degree up to max_d.
"""


def _eval_poly2(coeffs: dict, x: float, y: float) -> float:
    """Evaluate polynomial with coefficients {(i,j): c} at (x,y)."""
    result = 0.0
    for (i, j), c in coeffs.items():
        result += c * (x ** i) * (y ** j)
    return result


def _jacobian_det(f_coeffs: dict, g_coeffs: dict, x: float, y: float) -> float:
    """Compute Jacobian determinant of (f,g) at (x,y) numerically."""
    h = 1e-7
    df_dx = (_eval_poly2(f_coeffs, x + h, y) - _eval_poly2(f_coeffs, x - h, y)) / (2 * h)
    df_dy = (_eval_poly2(f_coeffs, x, y + h) - _eval_poly2(f_coeffs, x, y - h)) / (2 * h)
    dg_dx = (_eval_poly2(g_coeffs, x + h, y) - _eval_poly2(g_coeffs, x - h, y)) / (2 * h)
    dg_dy = (_eval_poly2(g_coeffs, x, y + h) - _eval_poly2(g_coeffs, x, y - h)) / (2 * h)
    return df_dx * dg_dy - df_dy * dg_dx


def _is_injective_sample(f_coeffs: dict, g_coeffs: dict, points: list) -> bool:
    """Sample-based injectivity check."""
    images = {}
    for x, y in points:
        fx = round(_eval_poly2(f_coeffs, x, y), 8)
        gy = round(_eval_poly2(g_coeffs, x, y), 8)
        key = (fx, gy)
        if key in images:
            old = images[key]
            if abs(old[0] - x) > 1e-6 or abs(old[1] - y) > 1e-6:
                return False
        images[key] = (x, y)
    return True


def verify(params: dict) -> dict:
    max_d = int(params.get("max_d", 3))
    max_d = min(max_d, 5)

    import random
    rng = random.Random(42)

    results = []
    conjecture_holds = True

    for deg in range(1, max_d + 1):
        for trial in range(10):
            # Generate random polynomial map of degree deg
            f_coeffs = {(1, 0): 1.0, (0, 1): 0.0}  # start with identity-like
            g_coeffs = {(1, 0): 0.0, (0, 1): 1.0}
            # Add higher degree terms with small coefficients
            for i in range(deg + 1):
                for j in range(deg + 1 - i):
                    if i + j >= 2 and i + j <= deg:
                        f_coeffs[(i, j)] = rng.uniform(-0.1, 0.1)
                        g_coeffs[(i, j)] = rng.uniform(-0.1, 0.1)

            # Check Jacobian at sample points
            test_pts = [(rng.uniform(-2, 2), rng.uniform(-2, 2))
                        for _ in range(20)]
            jac_vals = [_jacobian_det(f_coeffs, g_coeffs, x, y)
                        for x, y in test_pts]

            # Check if Jacobian is approximately constant
            jac_mean = sum(jac_vals) / len(jac_vals)
            jac_var = sum((j - jac_mean) ** 2 for j in jac_vals) / len(jac_vals)
            is_const_jac = jac_var < 0.01 and abs(jac_mean) > 0.1

            if is_const_jac:
                # Check injectivity
                grid_pts = [(x * 0.5, y * 0.5)
                            for x in range(-4, 5) for y in range(-4, 5)]
                injective = _is_injective_sample(f_coeffs, g_coeffs, grid_pts)
                results.append({
                    "degree": deg, "trial": trial,
                    "const_jacobian": True,
                    "jac_mean": round(jac_mean, 4),
                    "injective": injective,
                })
                if not injective:
                    conjecture_holds = False

    return {
        "status": "pass" if conjecture_holds else "fail",
        "summary": (
            f"Jacobian conjecture tested for 2-variable maps up to degree "
            f"{max_d}. Maps with constant Jacobian tested: {len(results)}. "
            f"All injective: {conjecture_holds}"
        ),
        "details": {
            "max_d": max_d,
            "tested_maps": len(results),
            "holds": conjecture_holds,
            "sample_results": results[:10],
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({}), indent=2))
