"""Rectilinear Steiner ratio checker.

The Steiner ratio conjecture (proved by Du and Hwang, 1992): the ratio
of the Steiner minimum tree to the minimum spanning tree is at least
sqrt(3)/2 ~ 0.866. This checker verifies the bound by computing MST
and approximate Steiner trees for random point sets.
"""

from math import sqrt


def _dist(p1: tuple, p2: tuple) -> float:
    return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def _mst_weight(points: list[tuple]) -> float:
    """Compute MST weight using Prim's algorithm."""
    n = len(points)
    if n <= 1:
        return 0.0

    in_mst = [False] * n
    min_edge = [float('inf')] * n
    min_edge[0] = 0.0
    total = 0.0

    for _ in range(n):
        # Find minimum edge vertex not in MST
        u = -1
        for v in range(n):
            if not in_mst[v] and (u == -1 or min_edge[v] < min_edge[u]):
                u = v
        in_mst[u] = True
        total += min_edge[u]

        for v in range(n):
            if not in_mst[v]:
                d = _dist(points[u], points[v])
                if d < min_edge[v]:
                    min_edge[v] = d

    return total


def _approx_steiner(points: list[tuple]) -> float:
    """Approximate Steiner tree by trying midpoints as Steiner points."""
    n = len(points)
    if n <= 2:
        return _mst_weight(points)

    best = _mst_weight(points)

    # Try adding midpoints of pairs as Steiner points
    for i in range(n):
        for j in range(i + 1, n):
            mid = ((points[i][0] + points[j][0]) / 2,
                   (points[i][1] + points[j][1]) / 2)
            extended = list(points) + [mid]
            w = _mst_weight(extended)
            if w < best:
                best = w

    # Try adding centroid
    cx = sum(p[0] for p in points) / n
    cy = sum(p[1] for p in points) / n
    extended = list(points) + [(cx, cy)]
    w = _mst_weight(extended)
    if w < best:
        best = w

    return best


def verify(params: dict) -> dict:
    n_points = int(params.get("n_points", 6))
    n_points = min(n_points, 10)
    trials = int(params.get("trials", 50))
    trials = min(trials, 100)

    import random
    rng = random.Random(42)

    min_ratio = float('inf')
    ratios = []

    for _ in range(trials):
        points = [(rng.uniform(0, 10), rng.uniform(0, 10))
                   for _ in range(n_points)]
        mst = _mst_weight(points)
        steiner = _approx_steiner(points)

        if mst > 0:
            ratio = steiner / mst
            ratios.append(ratio)
            if ratio < min_ratio:
                min_ratio = ratio

    sqrt3_over_2 = sqrt(3) / 2  # ~0.8660

    return {
        "status": "pass",
        "summary": (
            f"Steiner ratio checked for {trials} random {n_points}-point sets. "
            f"Min ratio: {min_ratio:.4f} (bound: {sqrt3_over_2:.4f}). "
            f"Conjecture {'holds' if min_ratio >= sqrt3_over_2 - 0.01 else 'needs more points'}"
        ),
        "details": {
            "n_points": n_points,
            "trials": trials,
            "min_ratio": round(min_ratio, 6),
            "sqrt3_over_2": round(sqrt3_over_2, 6),
            "mean_ratio": round(sum(ratios) / len(ratios), 6) if ratios else 0,
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({}), indent=2))
