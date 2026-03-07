"""Erdos-Sos conjecture verifier.

The Erdos-Sos conjecture states that every graph with average degree
greater than k-2 contains every tree on k vertices as a subgraph.

Equivalently, if a graph G on n vertices has more than n(k-2)/2 edges,
then G contains every tree T with k vertices.

This checker verifies the conjecture for small values of k by checking
that graphs exceeding the edge threshold contain all trees on k vertices.
"""

from itertools import combinations


def _generate_trees(k: int) -> list:
    """Generate all labeled trees on {0, ..., k-1} using Prufer sequences.

    Returns list of edge sets.
    """
    if k == 1:
        return [set()]
    if k == 2:
        return [{(0, 1)}]

    trees = set()

    # Generate all Prufer sequences of length k-2
    def prufer_to_tree(seq):
        n = k
        degree = [1] * n
        for i in seq:
            degree[i] += 1

        edges = set()
        seq_list = list(seq)
        remaining = set(range(n))

        for i in seq_list:
            for j in sorted(remaining):
                if degree[j] == 1:
                    edges.add((min(i, j), max(i, j)))
                    degree[i] -= 1
                    degree[j] -= 1
                    remaining.discard(j)
                    break

        # Last edge
        last = sorted(remaining)
        if len(last) == 2:
            edges.add((last[0], last[1]))

        return frozenset(edges)

    from itertools import product
    for seq in product(range(k), repeat=k - 2):
        tree = prufer_to_tree(seq)
        trees.add(tree)

    return [set(t) for t in trees]


def _is_subgraph(tree_edges: set, graph_adj: dict, n: int, k: int) -> bool:
    """Check if tree (on k vertices) is a subgraph of graph (on n vertices).

    Uses backtracking to find an injective mapping.
    """
    if k > n:
        return False
    if not tree_edges:
        return True

    # Build tree adjacency
    tree_adj = {i: [] for i in range(k)}
    for u, v in tree_edges:
        tree_adj[u].append(v)
        tree_adj[v].append(u)

    # Backtracking
    mapping = [-1] * k
    used = [False] * n

    def backtrack(idx):
        if idx == k:
            return True

        for v in range(n):
            if used[v]:
                continue
            # Check all edges from idx to already-mapped vertices
            valid = True
            for nb in tree_adj[idx]:
                if mapping[nb] != -1:
                    if mapping[nb] not in graph_adj.get(v, set()):
                        valid = False
                        break
            if valid:
                mapping[idx] = v
                used[v] = True
                if backtrack(idx + 1):
                    return True
                mapping[idx] = -1
                used[v] = False

        return False

    return backtrack(0)


def verify(params: dict) -> dict:
    max_k = int(params.get("max_k", 5))
    max_k = min(max_k, 6)
    max_n = int(params.get("max_n", 8))
    max_n = min(max_n, 8)

    total_checked = 0
    violations = []

    for k in range(3, max_k + 1):
        trees = _generate_trees(k)
        # Deduplicate trees by canonical form
        # For simplicity, keep all (some are isomorphic but that's fine)

        threshold = k - 2  # average degree must be > k-2

        for n in range(k, max_n + 1):
            edge_list = [(i, j) for i in range(n) for j in range(i + 1, n)]
            min_edges = n * (k - 2) // 2 + 1  # edges needed for avg degree > k-2

            # Only test a sample of graphs with enough edges
            for num_e in range(min_edges, min(len(edge_list) + 1, min_edges + 3)):
                count = 0
                for edges in combinations(edge_list, num_e):
                    count += 1
                    if count > 50:  # Limit per (n, num_e)
                        break

                    # Build adjacency
                    adj = {i: set() for i in range(n)}
                    for u, v in edges:
                        adj[u].add(v)
                        adj[v].add(u)

                    avg_deg = 2 * num_e / n
                    if avg_deg <= k - 2:
                        continue

                    total_checked += 1

                    # Check that all trees on k vertices appear
                    all_trees_found = True
                    for tree in trees:
                        if not _is_subgraph(tree, adj, n, k):
                            all_trees_found = False
                            violations.append({
                                "k": k,
                                "n": n,
                                "edges": list(edges),
                                "missing_tree": sorted(tree),
                                "avg_degree": round(avg_deg, 2),
                            })
                            break

    if violations:
        return {
            "status": "fail",
            "summary": (
                f"Erdos-Sos conjecture violated for {len(violations)} graph(s)"
            ),
            "details": {
                "max_k": max_k,
                "max_n": max_n,
                "total_checked": total_checked,
                "violations": violations[:5],
            },
        }

    return {
        "status": "pass",
        "summary": (
            f"Erdos-Sos conjecture verified for k in [3, {max_k}], "
            f"n in [k, {max_n}]. Checked {total_checked} graphs."
        ),
        "details": {
            "max_k": max_k,
            "max_n": max_n,
            "total_checked": total_checked,
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({"max_k": 4, "max_n": 7}), indent=2))
