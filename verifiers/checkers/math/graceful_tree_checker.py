"""Graceful tree conjecture checker.

The graceful labeling conjecture states that every tree has a graceful labeling.
A graceful labeling of a graph with m edges assigns distinct labels from {0,...,m}
to vertices such that the induced edge labels |f(u)-f(v)| are all distinct.
Verifies by exhaustive search for all trees up to `max_vertices` vertices.
"""

from itertools import permutations


def _generate_trees(n: int) -> list[list[tuple[int, int]]]:
    """Generate all labeled trees on n vertices using Prufer sequences."""
    if n == 1:
        return [[]]
    if n == 2:
        return [[(0, 1)]]

    trees = set()
    # Enumerate all Prufer sequences of length n-2 with elements in [0, n-1]
    def prufer_to_edges(seq: tuple[int, ...]) -> tuple[tuple[int, int], ...]:
        degree = [1] * n
        for v in seq:
            degree[v] += 1
        edges = []
        seq_list = list(seq)
        for s in seq_list:
            for leaf in range(n):
                if degree[leaf] == 1:
                    edges.append((min(leaf, s), max(leaf, s)))
                    degree[leaf] -= 1
                    degree[s] -= 1
                    break
        # Last edge
        last = [v for v in range(n) if degree[v] == 1]
        if len(last) == 2:
            edges.append((min(last[0], last[1]), max(last[0], last[1])))
        return tuple(sorted(edges))

    def gen_prufer(pos, seq):
        if pos == n - 2:
            tree = prufer_to_edges(tuple(seq))
            trees.add(tree)
            return
        for v in range(n):
            seq.append(v)
            gen_prufer(pos + 1, seq)
            seq.pop()

    gen_prufer(0, [])
    return [list(t) for t in trees]


def _has_graceful_labeling(edges: list[tuple[int, int]], n: int) -> bool:
    """Check if a tree with given edges has a graceful labeling."""
    m = len(edges)  # = n - 1

    # Try all permutations of labels {0, ..., m} assigned to n vertices
    for perm in permutations(range(m + 1), n):
        edge_labels = set()
        valid = True
        for u, v in edges:
            el = abs(perm[u] - perm[v])
            if el == 0 or el in edge_labels:
                valid = False
                break
            edge_labels.add(el)
        if valid and len(edge_labels) == m:
            return True
    return False


def verify(params: dict) -> dict:
    max_vertices = int(params.get("max_vertices", 10))
    # Limit to reasonable sizes due to exponential complexity
    max_vertices = min(max_vertices, 10)

    total_trees = 0
    graceful_trees = 0
    failures = []

    for n in range(1, max_vertices + 1):
        trees = _generate_trees(n)
        # Remove duplicate tree structures (isomorphic trees)
        unique_trees = []
        seen = set()
        for t in trees:
            key = tuple(sorted(t))
            if key not in seen:
                seen.add(key)
                unique_trees.append(t)

        for tree in unique_trees:
            total_trees += 1
            if _has_graceful_labeling(tree, n):
                graceful_trees += 1
            else:
                failures.append({"n": n, "edges": tree})

    if failures:
        return {
            "status": "fail",
            "summary": f"Found {len(failures)} trees without graceful labeling",
            "details": {"failures": failures[:5]},
        }

    return {
        "status": "pass",
        "summary": f"All {total_trees} trees up to {max_vertices} vertices have graceful labelings",
        "details": {"max_vertices": max_vertices, "total_trees": total_trees},
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({"max_vertices": 7}), indent=2))
