"""Erdos-Sos conjecture extended checker.

The Erdos-Sos conjecture: every graph with average degree > k-2
contains every tree with k edges as a subgraph. This checker tests
additional graph families beyond the basic checker.
"""

from itertools import combinations, permutations


def _generate_trees(k: int) -> list[list[tuple]]:
    """Generate all trees with k edges (k+1 vertices) using Prufer."""
    n = k + 1
    if n <= 1:
        return [[]]
    if n == 2:
        return [[(0, 1)]]

    trees = []
    seen = set()
    from itertools import product as iprod

    for seq in iprod(range(n), repeat=n - 2):
        degree = [1] * n
        for i in seq:
            degree[i] += 1
        edges = []
        remaining = list(seq)
        leaves = sorted(i for i in range(n) if degree[i] == 1)

        valid = True
        for s in remaining:
            if not leaves:
                valid = False
                break
            leaf = leaves.pop(0)
            edges.append((min(leaf, s), max(leaf, s)))
            degree[leaf] -= 1
            degree[s] -= 1
            if degree[s] == 1:
                import bisect
                bisect.insort(leaves, s)

        if not valid:
            continue
        last = [i for i in range(n) if degree[i] == 1]
        if len(last) == 2:
            edges.append((min(last[0], last[1]), max(last[0], last[1])))

        canon = tuple(sorted(edges))
        if canon not in seen:
            seen.add(canon)
            trees.append(list(canon))
            if len(trees) >= 30:
                break

    return trees


def _contains_tree(adj: list[set[int]], n: int, tree_edges: list[tuple], k: int) -> bool:
    """Check if graph contains the tree as a subgraph."""
    tree_n = k + 1
    if tree_n > n:
        return False

    tree_adj = [[] for _ in range(tree_n)]
    for u, v in tree_edges:
        tree_adj[u].append(v)
        tree_adj[v].append(u)

    for mapping_start in combinations(range(n), tree_n):
        for perm in permutations(mapping_start):
            if all(perm[v] in adj[perm[u]] for u, v in tree_edges):
                return True
    return False


def verify(params: dict) -> dict:
    max_n = int(params.get("max_n", 8))
    max_n = min(max_n, 10)

    import random
    rng = random.Random(42)

    violations = []
    checked = 0

    for n in range(4, max_n + 1):
        for k in range(2, min(n, 5)):
            trees = _generate_trees(k)
            threshold = k - 2

            for trial in range(10):
                adj = [set() for _ in range(n)]
                edge_count = 0
                for u, v in combinations(range(n), 2):
                    if rng.random() < 0.6:
                        adj[u].add(v)
                        adj[v].add(u)
                        edge_count += 1

                avg_degree = 2 * edge_count / n if n > 0 else 0
                if avg_degree <= threshold:
                    continue

                checked += 1
                for tree_edges in trees:
                    if not _contains_tree(adj, n, tree_edges, k):
                        violations.append({
                            "n": n, "k": k,
                            "avg_degree": round(avg_degree, 2),
                        })
                        break

    if violations:
        return {
            "status": "fail",
            "summary": f"Erdos-Sos violated in {len(violations)} cases",
            "details": {"violations": violations[:10]},
        }

    return {
        "status": "pass",
        "summary": (
            f"Erdos-Sos conjecture verified for {checked} graphs "
            f"up to {max_n} vertices"
        ),
        "details": {"max_n": max_n, "checked": checked},
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({"max_n": 6}), indent=2))
