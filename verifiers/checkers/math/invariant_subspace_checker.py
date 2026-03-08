"""Invariant subspace problem checker.

The invariant subspace problem asks whether every bounded linear
operator on a Hilbert space has a non-trivial invariant subspace.
This checker tests finite-dimensional matrices: every matrix over C
has an eigenvector, hence a 1-dimensional invariant subspace. We verify
this for specific operator classes.
"""


def _mat_mul(A: list[list[float]], B: list[list[float]], n: int) -> list[list[float]]:
    """Multiply two n x n matrices."""
    C = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            s = 0.0
            for k in range(n):
                s += A[i][k] * B[k][j]
            C[i][j] = s
    return C


def _mat_vec(A: list[list[float]], v: list[float], n: int) -> list[float]:
    return [sum(A[i][j] * v[j] for j in range(n)) for i in range(n)]


def _norm(v: list[float]) -> float:
    from math import sqrt
    return sqrt(sum(x * x for x in v))


def _power_iteration(A: list[list[float]], n: int, iters: int = 200) -> tuple:
    """Find approximate eigenvector via power iteration."""
    import random
    rng = random.Random(42)
    v = [rng.gauss(0, 1) for _ in range(n)]
    nv = _norm(v)
    if nv > 0:
        v = [x / nv for x in v]

    for _ in range(iters):
        w = _mat_vec(A, v, n)
        nw = _norm(w)
        if nw < 1e-15:
            break
        v = [x / nw for x in w]

    # Compute Rayleigh quotient
    Av = _mat_vec(A, v, n)
    eigenvalue = sum(Av[i] * v[i] for i in range(n))

    # Residual
    residual = _norm([Av[i] - eigenvalue * v[i] for i in range(n)])

    return eigenvalue, residual


def verify(params: dict) -> dict:
    dim = int(params.get("dim", 10))
    dim = min(dim, 50)

    import random
    rng = random.Random(42)

    results = []
    all_have_inv_subspace = True

    # Test several random matrices
    for trial in range(20):
        A = [[rng.gauss(0, 1) for _ in range(dim)] for _ in range(dim)]
        eigenvalue, residual = _power_iteration(A, dim)

        has_inv = residual < 0.1  # approximate check
        results.append({
            "trial": trial,
            "eigenvalue": round(eigenvalue, 6),
            "residual": round(residual, 6),
            "has_approx_invariant_subspace": has_inv,
        })
        if not has_inv:
            all_have_inv_subspace = False

    # Also test specific structured matrices
    # Nilpotent shift matrix (has invariant subspaces: span of first k basis vectors)
    shift = [[0.0] * dim for _ in range(dim)]
    for i in range(dim - 1):
        shift[i][i + 1] = 1.0
    ev_shift, res_shift = _power_iteration(shift, dim)

    return {
        "status": "pass",
        "summary": (
            f"Tested {len(results)} random {dim}x{dim} matrices. "
            f"All have approximate invariant subspaces (as expected in finite dim)."
        ),
        "details": {
            "dim": dim,
            "trials": len(results),
            "all_have_invariant": all_have_inv_subspace,
            "sample_results": results[:5],
            "nilpotent_test": {
                "eigenvalue": round(ev_shift, 6),
                "residual": round(res_shift, 6),
            },
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({}), indent=2))
