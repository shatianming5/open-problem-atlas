"""Total coloring conjecture checker.

The total coloring conjecture (Behzad-Vizing): the total chromatic
number of any graph is at most Delta(G) + 2, where Delta is the
maximum degree. Verifies for small graphs.
"""

from itertools import combinations


def _max_degree(adj: list[set[int]], n: int) -> int:
    return max((len(adj[v]) for v in range(n)), default=0)


def _can_total_color(adj: list[set[int]], n: int, k: int) -> bool:
    """Check if graph has a total coloring with k colors."""
    edges = []
    for u in range(n):
        for v in adj[u]:
            if u < v:
                edges.append((u, v))
    m = len(edges)
    # Assign colors to vertices (0..n-1) and edges (n..n+m-1)
    total = n + m
    color = [-1] * total

    # Build conflict graph
    conflicts = [set() for _ in range(total)]
    # Adjacent vertices conflict
    for u in range(n):
        for v in adj[u]:
            conflicts[u].add(v)
    # Incident edges conflict
    for i, (u1, v1) in enumerate(edges):
        for j, (u2, v2) in enumerate(edges):
            if i < j and (u1 == u2 or u1 == v2 or v1 == u2 or v1 == v2):
                conflicts[n + i].add(n + j)
                conflicts[n + j].add(n + i)
    # Vertex-edge incidence conflicts
    for i, (u, v) in enumerate(edges):
        conflicts[u].add(n + i)
        conflicts[n + i].add(u)
        conflicts[v].add(n + i)
        conflicts[n + i].add(v)

    def bt(idx: int) -> bool:
        if idx == total:
            return True
        for c in range(k):
            if all(color[nb] != c for nb in conflicts[idx] if color[nb] >= 0):
                color[idx] = c
                if bt(idx + 1):
                    return True
                color[idx] = -1
        return False

    return bt(0)


def verify(params: dict) -> dict:
    max_vertices = int(params.get("max_vertices", 6))
    max_vertices = min(max_vertices, 8)

    checked = 0
    violations = []

    import random
    random.seed(42)

    for n in range(3, max_vertices + 1):
        for trial in range(10):
            adj = [set() for _ in range(n)]
            for u, v in combinations(range(n), 2):
                if random.random() < 0.5:
                    adj[u].add(v)
                    adj[v].add(u)

            delta = _max_degree(adj, n)
            if delta == 0:
                continue

            bound = delta + 2
            colorable = _can_total_color(adj, n, bound)
            checked += 1

            if not colorable:
                violations.append({"n": n, "delta": delta, "trial": trial})

    if violations:
        return {
            "status": "fail",
            "summary": f"Total coloring conjecture violated for {len(violations)} graphs",
            "details": {"violations": violations[:10]},
        }

    return {
        "status": "pass",
        "summary": (
            f"Total coloring conjecture (chi'' <= Delta+2) verified for "
            f"{checked} random graphs up to {max_vertices} vertices"
        ),
        "details": {"max_vertices": max_vertices, "checked": checked},
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({}), indent=2))
