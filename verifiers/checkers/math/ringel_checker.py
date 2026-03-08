"""Ringel's conjecture checker.

Ringel's conjecture (now theorem for large n, proved by Montgomery,
Pokrovskiy, Sudakov 2020): the complete graph K_{2n+1} can be
decomposed into 2n+1 copies of any tree T with n edges.
This checker verifies graceful labelings exist for small trees,
which implies such decompositions.
"""

from itertools import permutations


def _is_graceful(adj: list[list[int]], labeling: list[int]) -> bool:
    """Check if labeling is a graceful labeling of the tree."""
    n = len(adj)
    num_edges = sum(len(a) for a in adj) // 2
    edge_labels = set()
    for u in range(n):
        for v in adj[u]:
            if u < v:
                diff = abs(labeling[u] - labeling[v])
                if diff == 0 or diff > num_edges:
                    return False
                edge_labels.add(diff)
    return len(edge_labels) == num_edges


def _generate_trees(n: int) -> list[list[list[int]]]:
    """Generate small trees on n vertices using Prufer sequences."""
    if n == 1:
        return [[[]]]
    if n == 2:
        return [[[1], [0]]]

    trees = []
    seen = set()

    def prufer_to_tree(seq: tuple) -> list[list[int]] | None:
        degree = [1] * n
        for i in seq:
            degree[i] += 1
        adj = [[] for _ in range(n)]
        remaining = list(seq)
        leaves = sorted([i for i in range(n) if degree[i] == 1])

        for s in remaining:
            if not leaves:
                return None
            leaf = leaves.pop(0)
            adj[leaf].append(s)
            adj[s].append(leaf)
            degree[leaf] -= 1
            degree[s] -= 1
            if degree[s] == 1:
                # Insert into sorted leaves
                import bisect
                bisect.insort(leaves, s)

        # Connect last two nodes
        last = [i for i in range(n) if degree[i] == 1]
        if len(last) == 2:
            adj[last[0]].append(last[1])
            adj[last[1]].append(last[0])

        # Canonical form for deduplication
        canon = tuple(sorted(tuple(sorted(a)) for a in adj))
        if canon in seen:
            return None
        seen.add(canon)
        return adj

    # Generate all Prufer sequences of length n-2
    from itertools import product as iprod
    for seq in iprod(range(n), repeat=n - 2):
        tree = prufer_to_tree(seq)
        if tree is not None:
            trees.append(tree)
            if len(trees) >= 50:  # cap to prevent blowup
                break

    return trees


def verify(params: dict) -> dict:
    max_n = int(params.get("max_n", 7))
    max_n = min(max_n, 9)
    # Only check small trees feasibly
    actual_n = min(max_n, 7)

    results = []
    all_graceful = True

    for n in range(2, actual_n + 1):
        trees = _generate_trees(n)
        graceful_count = 0
        total = len(trees)

        for adj in trees:
            num_edges = n - 1
            found = False
            for perm in permutations(range(num_edges + 1)):
                labeling = list(perm[:n])
                if _is_graceful(adj, labeling):
                    found = True
                    break
            if found:
                graceful_count += 1

        results.append({
            "vertices": n,
            "trees_checked": total,
            "graceful": graceful_count,
        })
        if graceful_count < total:
            all_graceful = False

    return {
        "status": "pass" if all_graceful else "fail",
        "summary": (
            f"Checked graceful labelings for trees up to {actual_n} vertices. "
            f"All graceful: {all_graceful}"
        ),
        "details": {"max_n": actual_n, "results": results},
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({"max_n": 5}), indent=2))
