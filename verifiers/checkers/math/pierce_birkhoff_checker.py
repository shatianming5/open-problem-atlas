"""Pierce-Birkhoff conjecture checker.

The Pierce-Birkhoff conjecture: every piecewise polynomial function
on R^n can be written as a sup of inf's of finitely many polynomials.
This checker tests small cases in 2 variables with simple piecewise
polynomial functions.
"""


def _eval_pw(pieces: list[tuple], x: float, y: float) -> float:
    """Evaluate piecewise polynomial. Each piece is (condition_fn, poly_fn)."""
    for cond, poly in pieces:
        if cond(x, y):
            return poly(x, y)
    return pieces[-1][1](x, y)


def _sup_inf_representable(pieces: list[tuple], test_points: list[tuple],
                           polys: list, tol: float = 1e-6) -> bool:
    """Check if piecewise function equals some sup-inf of given polynomials
    at test points."""
    n = len(polys)
    if n == 0:
        return False

    # Evaluate all polynomials at all test points
    poly_vals = [[p(x, y) for x, y in test_points] for p in polys]
    target = [_eval_pw(pieces, x, y) for x, y in test_points]

    # Try sup of single polynomials
    for i in range(n):
        if all(abs(poly_vals[i][j] - target[j]) < tol
               for j in range(len(test_points))):
            return True

    # Try sup of inf of pairs
    for i in range(n):
        for j in range(n):
            vals = [min(poly_vals[i][k], poly_vals[j][k])
                    for k in range(len(test_points))]
            if all(abs(vals[k] - target[k]) < tol
                   for k in range(len(test_points))):
                return True

    # Try max of two polynomials
    for i in range(n):
        for j in range(i, n):
            vals = [max(poly_vals[i][k], poly_vals[j][k])
                    for k in range(len(test_points))]
            if all(abs(vals[k] - target[k]) < tol
                   for k in range(len(test_points))):
                return True

    return False


def verify(params: dict) -> dict:
    max_pieces = int(params.get("max_pieces", 4))
    max_pieces = min(max_pieces, 8)

    # Test case 1: |x| = max(x, -x)
    pieces1 = [
        (lambda x, y: x >= 0, lambda x, y: x),
        (lambda x, y: True, lambda x, y: -x),
    ]
    polys1 = [lambda x, y: x, lambda x, y: -x, lambda x, y: 0]
    test_pts = [(x * 0.5, y * 0.5) for x in range(-4, 5) for y in range(-4, 5)]

    rep1 = _sup_inf_representable(pieces1, test_pts, polys1)

    # Test case 2: max(x, y)
    pieces2 = [
        (lambda x, y: x >= y, lambda x, y: x),
        (lambda x, y: True, lambda x, y: y),
    ]
    polys2 = [lambda x, y: x, lambda x, y: y]
    rep2 = _sup_inf_representable(pieces2, test_pts, polys2)

    # Test case 3: max(x^2, y^2)
    pieces3 = [
        (lambda x, y: x * x >= y * y, lambda x, y: x * x),
        (lambda x, y: True, lambda x, y: y * y),
    ]
    polys3 = [lambda x, y: x * x, lambda x, y: y * y,
              lambda x, y: x * x + y * y]
    rep3 = _sup_inf_representable(pieces3, test_pts, polys3)

    results = [
        {"function": "|x|", "representable": rep1},
        {"function": "max(x,y)", "representable": rep2},
        {"function": "max(x^2,y^2)", "representable": rep3},
    ]

    all_rep = all(r["representable"] for r in results)

    return {
        "status": "pass" if all_rep else "fail",
        "summary": (
            f"Pierce-Birkhoff conjecture tested for {len(results)} piecewise "
            f"polynomial functions. All representable: {all_rep}"
        ),
        "details": {"max_pieces": max_pieces, "results": results},
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({}), indent=2))
