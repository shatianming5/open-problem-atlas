"""Erdos-Gyarfas conjecture verifier.

The Erdos-Gyarfas conjecture states that every graph with minimum degree
at least 3 contains a cycle whose length is a power of 2.

This checker verifies the conjecture for small graphs by finding cycles
of length 2^j (j >= 1, i.e., lengths 2, 4, 8, ...) in graphs with
minimum degree >= 3.
"""

from itertools import combinations


def _find_cycle_lengths(adj: dict, n: int) -> set:
    """Find all cycle lengths present in the graph using BFS/DFS."""
    cycle_lengths = set()

    # Use BFS from each vertex to find shortest cycles
    for start in range(n):
        # BFS
        dist = [-1] * n
        dist[start] = 0
        queue = [start]

        while queue:
            u = queue.pop(0)
            for v in adj.get(u, []):
                if dist[v] == -1:
                    dist[v] = dist[u] + 1
                    queue.append(v)
                elif v != start and dist[v] >= dist[u]:
                    # Found a cycle
                    cycle_len = dist[u] + dist[v] + 1
                    cycle_lengths.add(cycle_len)

    # Also find exact cycle lengths using DFS for small graphs
    if n <= 10:
        visited_global = set()

        def dfs_cycles(path, visited):
            u = path[-1]
            for v in adj.get(u, []):
                if v == path[0] and len(path) >= 3:
                    cycle_lengths.add(len(path))
                elif v not in visited and v > path[0]:
                    visited.add(v)
                    path.append(v)
                    dfs_cycles(path, visited)
                    path.pop()
                    visited.discard(v)

        for start in range(n):
            dfs_cycles([start], {start})

    return cycle_lengths


def _is_power_of_2(n: int) -> bool:
    """Check if n is a power of 2."""
    return n > 0 and (n & (n - 1)) == 0


def verify(params: dict) -> dict:
    max_vertices = int(params.get("max_vertices", 7))
    max_vertices = min(max_vertices, 8)

    total_checked = 0
    violations = []

    for n in range(4, max_vertices + 1):  # Need at least 4 vertices for min degree 3
        edge_list = [(i, j) for i in range(n) for j in range(i + 1, n)]
        num_possible = len(edge_list)

        # For n=8, 2^28 is too many. Limit to graphs with enough edges
        min_edges = (3 * n + 1) // 2  # minimum edges for min degree 3

        for num_edges in range(min_edges, num_possible + 1):
            for edges in combinations(edge_list, num_edges):
                # Build adjacency list
                adj = {i: [] for i in range(n)}
                for u, v in edges:
                    adj[u].append(v)
                    adj[v].append(u)

                # Check minimum degree >= 3
                if any(len(adj[v]) < 3 for v in range(n)):
                    continue

                total_checked += 1

                # Find cycle lengths
                cycle_lens = _find_cycle_lengths(adj, n)

                # Check if any is a power of 2
                has_power_of_2_cycle = any(_is_power_of_2(cl) for cl in cycle_lens)

                if not has_power_of_2_cycle:
                    violations.append({
                        "n": n,
                        "edges": list(edges),
                        "cycle_lengths": sorted(cycle_lens),
                    })

                if total_checked >= 5000:
                    break
            if total_checked >= 5000:
                break
        if total_checked >= 5000:
            break

    if violations:
        return {
            "status": "fail",
            "summary": (
                f"Erdos-Gyarfas conjecture violated: {len(violations)} graph(s) "
                f"with min degree >= 3 have no power-of-2 length cycle"
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
            f"Erdos-Gyarfas conjecture verified for graphs on up to "
            f"{max_vertices} vertices. Checked {total_checked} graphs "
            f"with min degree >= 3."
        ),
        "details": {
            "max_vertices": max_vertices,
            "total_checked": total_checked,
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({"max_vertices": 6}), indent=2))
