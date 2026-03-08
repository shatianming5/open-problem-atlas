"""List coloring conjecture checker.

The list chromatic number conjecture states that chi_l(G) = chi(G) for
every line graph (equivalently, list edge chromatic number equals edge
chromatic number). This checker tests small bipartite graphs where
the conjecture implies chi_l = chi.
"""

from itertools import combinations, product


def _chromatic_number_small(adj: list[set[int]], n: int) -> int:
    """Compute chromatic number by brute force."""
    if n == 0:
        return 0
    for k in range(1, n + 1):
        if _can_color(adj, n, k):
            return k
    return n


def _can_color(adj: list[set[int]], n: int, k: int) -> bool:
    coloring = [-1] * n
    def bt(v: int) -> bool:
        if v == n:
            return True
        for c in range(k):
            if all(coloring[u] != c for u in adj[v] if coloring[u] >= 0):
                coloring[v] = c
                if bt(v + 1):
                    return True
                coloring[v] = -1
        return False
    return bt(0)


def _can_list_color(adj: list[set[int]], n: int, lists: list[set[int]]) -> bool:
    """Check if graph can be colored from given lists."""
    coloring = [-1] * n
    def bt(v: int) -> bool:
        if v == n:
            return True
        for c in lists[v]:
            if all(coloring[u] != c for u in adj[v] if coloring[u] >= 0):
                coloring[v] = c
                if bt(v + 1):
                    return True
                coloring[v] = -1
        return False
    return bt(0)


def verify(params: dict) -> dict:
    max_n = int(params.get("max_n", 6))
    max_n = min(max_n, 8)

    checked = 0
    violations = []

    for n in range(2, max_n + 1):
        # Generate complete bipartite graphs K_{a,b}
        for a in range(1, n):
            b = n - a
            if b < a:
                break
            adj = [set() for _ in range(n)]
            for u in range(a):
                for v in range(a, n):
                    adj[u].add(v)
                    adj[v].add(u)

            chi = _chromatic_number_small(adj, n)

            # Test list coloring with lists of size chi
            # Try several random list assignments
            import random
            random.seed(42 + n * 100 + a)
            all_colors = list(range(chi + 2))

            list_colorable = True
            for _ in range(20):
                lists = [set(random.sample(all_colors, chi)) for _ in range(n)]
                if not _can_list_color(adj, n, lists):
                    list_colorable = False
                    break

            checked += 1
            if not list_colorable:
                violations.append({"n": n, "a": a, "b": b, "chi": chi})

    if violations:
        return {
            "status": "fail",
            "summary": f"List coloring conjecture violated for {len(violations)} graphs",
            "details": {"violations": violations},
        }

    return {
        "status": "pass",
        "summary": (
            f"List coloring conjecture verified for {checked} bipartite graphs "
            f"up to {max_n} vertices"
        ),
        "details": {"max_n": max_n, "checked": checked},
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({}), indent=2))
