"""Overfull conjecture checker.

The overfull conjecture: a graph G with Delta(G) >= n/3 is Class 2
(edge chromatic number = Delta+1) if and only if it contains an
overfull subgraph H (one with |E(H)| > Delta(G) * floor(|V(H)|/2)).
Tests small graphs.
"""

from itertools import combinations


def _edge_chromatic_number(adj: list[set[int]], n: int) -> int:
    """Compute edge chromatic number by brute force."""
    edges = []
    for u in range(n):
        for v in adj[u]:
            if u < v:
                edges.append((u, v))
    if not edges:
        return 0

    delta = max(len(adj[v]) for v in range(n))

    # Try coloring edges with delta colors first, then delta+1
    for k in range(delta, delta + 2):
        if _can_edge_color(edges, adj, n, k):
            return k
    return delta + 1


def _can_edge_color(edges: list, adj: list[set[int]], n: int, k: int) -> bool:
    m = len(edges)
    color = [-1] * m
    # Build edge conflict: edges sharing a vertex
    conflicts = [[] for _ in range(m)]
    for i in range(m):
        for j in range(i + 1, m):
            u1, v1 = edges[i]
            u2, v2 = edges[j]
            if u1 == u2 or u1 == v2 or v1 == u2 or v1 == v2:
                conflicts[i].append(j)
                conflicts[j].append(i)

    def bt(idx: int) -> bool:
        if idx == m:
            return True
        for c in range(k):
            if all(color[nb] != c for nb in conflicts[idx] if color[nb] >= 0):
                color[idx] = c
                if bt(idx + 1):
                    return True
                color[idx] = -1
        return False

    return bt(0)


def _is_overfull(adj: list[set[int]], n: int, delta_G: int) -> bool:
    """Check if graph has an overfull subgraph."""
    for size in range(3, n + 1, 2):  # odd subsets
        for subset in combinations(range(n), size):
            sub_edges = 0
            for u, v in combinations(subset, 2):
                if v in adj[u]:
                    sub_edges += 1
            if sub_edges > delta_G * (size // 2):
                return True
    return False


def verify(params: dict) -> dict:
    max_vertices = int(params.get("max_vertices", 7))
    max_vertices = min(max_vertices, 9)
    n = min(max_vertices, 7)

    import random
    random.seed(42)

    checked = 0
    conjecture_holds = True
    counterexamples = []

    for trial in range(30):
        adj = [set() for _ in range(n)]
        for u, v in combinations(range(n), 2):
            if random.random() < 0.5:
                adj[u].add(v)
                adj[v].add(u)

        delta = max((len(adj[v]) for v in range(n)), default=0)
        if delta < n / 3 or delta == 0:
            continue

        chi_e = _edge_chromatic_number(adj, n)
        is_class2 = (chi_e == delta + 1)
        overfull = _is_overfull(adj, n, delta)
        checked += 1

        if is_class2 != overfull:
            conjecture_holds = False
            counterexamples.append({
                "trial": trial, "class2": is_class2, "overfull": overfull,
            })

    return {
        "status": "pass" if conjecture_holds else "fail",
        "summary": (
            f"Overfull conjecture checked for {checked} graphs on {n} vertices. "
            f"Conjecture holds: {conjecture_holds}"
        ),
        "details": {
            "max_vertices": n,
            "checked": checked,
            "holds": conjecture_holds,
            "counterexamples": counterexamples[:5],
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({}), indent=2))
