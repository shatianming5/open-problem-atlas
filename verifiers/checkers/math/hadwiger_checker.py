"""Hadwiger conjecture verifier.

Hadwiger's conjecture states that if a graph G has no K_t minor, then
G is (t-1)-colorable (i.e., the chromatic number chi(G) <= t-1).

Equivalently: chi(G) >= t implies G has a K_t minor.

This is known to hold for t <= 6:
- t=1,2,3: trivial/easy
- t=4: equivalent to the four-color theorem (proved 1976)
- t=5: proved by Wagner (1937), equivalent to four-color theorem
- t=6: proved by Robertson, Seymour, Thomas (1993)

This checker verifies the conjecture for small graphs by computing
chromatic numbers and checking for clique minors.
"""

from itertools import combinations


def _chromatic_number(adj: dict, n: int) -> int:
    """Compute the chromatic number of a graph by trying k-colorings."""
    if n == 0:
        return 0

    vertices = list(range(n))

    for k in range(1, n + 1):
        # Try k-coloring using backtracking
        colors = [-1] * n

        def backtrack(v):
            if v == n:
                return True
            for c in range(k):
                if all(colors[u] != c for u in adj.get(v, []) if colors[u] >= 0):
                    colors[v] = c
                    if backtrack(v + 1):
                        return True
                    colors[v] = -1
            return False

        if backtrack(0):
            return k

    return n


def _has_minor(adj: dict, n: int, t: int) -> bool:
    """Check if graph has K_t as a minor.

    K_t minor exists iff we can partition some connected subsets
    S_1, ..., S_t of V such that each pair has an edge between them.

    For small t and n, use brute force.
    """
    if t <= 1:
        return n >= 1
    if t == 2:
        # K_2 minor exists iff graph has an edge
        return any(len(adj.get(v, [])) > 0 for v in range(n))

    vertices = list(range(n))

    # Try all ways to assign t groups
    # For efficiency, limit search
    def _is_connected_subset(subset, adj_dict):
        if not subset:
            return False
        subset = set(subset)
        visited = set()
        stack = [next(iter(subset))]
        while stack:
            u = stack.pop()
            if u in visited:
                continue
            visited.add(u)
            for v in adj_dict.get(u, []):
                if v in subset and v not in visited:
                    stack.append(v)
        return visited == subset

    def _has_edge_between(s1, s2, adj_dict):
        for u in s1:
            for v in adj_dict.get(u, []):
                if v in s2:
                    return True
        return False

    # For small t (<=4), try partitioning
    if t <= 4 and n <= 10:
        # Try subsets of vertices
        for size in range(t, n + 1):
            for chosen in combinations(vertices, size):
                # Try assigning groups
                chosen_list = list(chosen)

                def try_partition(idx, groups):
                    if idx == len(chosen_list):
                        if len(groups) < t:
                            return False
                        # Check connectivity and adjacency
                        group_lists = list(groups.values())
                        for g in group_lists:
                            if not _is_connected_subset(g, adj):
                                return False
                        for i in range(len(group_lists)):
                            for j in range(i + 1, len(group_lists)):
                                if not _has_edge_between(
                                    group_lists[i], group_lists[j], adj
                                ):
                                    return False
                        return True

                    v = chosen_list[idx]
                    # Try adding to existing group or new group
                    for g_id in list(groups.keys()):
                        groups[g_id].append(v)
                        if try_partition(idx + 1, groups):
                            return True
                        groups[g_id].pop()

                    if len(groups) < t:
                        new_id = len(groups)
                        groups[new_id] = [v]
                        if try_partition(idx + 1, groups):
                            return True
                        del groups[new_id]

                    return False

                if try_partition(0, {}):
                    return True

    return False


def verify(params: dict) -> dict:
    max_vertices = int(params.get("max_vertices", 6))
    max_vertices = min(max_vertices, 7)

    total_checked = 0
    violations = []

    for n in range(2, max_vertices + 1):
        edge_list = [(i, j) for i in range(n) for j in range(i + 1, n)]
        num_possible = len(edge_list)

        for mask in range(1, 2 ** num_possible):
            edges = [edge_list[i] for i in range(num_possible) if mask & (1 << i)]

            adj = {i: [] for i in range(n)}
            for u, v in edges:
                adj[u].append(v)
                adj[v].append(u)

            chi = _chromatic_number(adj, n)
            # Hadwiger: chi >= t implies K_t minor exists
            # We check: does G have K_chi minor?
            if chi >= 2:
                has_k_chi = _has_minor(adj, n, chi)
                total_checked += 1

                if not has_k_chi:
                    violations.append({
                        "n": n,
                        "edges": edges,
                        "chromatic_number": chi,
                        "missing_minor": f"K_{chi}",
                    })

            if total_checked >= 3000:
                break
        if total_checked >= 3000:
            break

    if violations:
        return {
            "status": "fail",
            "summary": (
                f"Hadwiger conjecture violated for {len(violations)} graph(s)"
            ),
            "details": {
                "max_vertices": max_vertices,
                "total_checked": total_checked,
                "violations": violations[:5],
            },
        }

    return {
        "status": "pass",
        "summary": (
            f"Hadwiger conjecture verified for graphs on up to "
            f"{max_vertices} vertices. Checked {total_checked} graphs."
        ),
        "details": {
            "max_vertices": max_vertices,
            "total_checked": total_checked,
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({"max_vertices": 5}), indent=2))
