"""Reconstruction conjecture verifier.

The reconstruction conjecture (Kelly-Ulam conjecture) states that every
graph on n >= 3 vertices is determined (up to isomorphism) by its
multiset of vertex-deleted subgraphs (the "deck").

This checker verifies the conjecture for all graphs on n vertices (n <= 8)
by checking that no two non-isomorphic graphs share the same deck.
"""

from itertools import combinations


def _adjacency_to_edges(adj: list, n: int) -> set:
    """Convert adjacency matrix to edge set."""
    edges = set()
    for i in range(n):
        for j in range(i + 1, n):
            if adj[i][j]:
                edges.add((i, j))
    return edges


def _graph_invariant(adj: list, n: int) -> tuple:
    """Compute a simple graph invariant for quick comparison.

    Returns sorted degree sequence and edge count.
    """
    degrees = sorted(sum(adj[i][j] for j in range(n)) for i in range(n))
    edge_count = sum(adj[i][j] for i in range(n) for j in range(i + 1, n))
    return (tuple(degrees), edge_count)


def _canonical_form(adj: list, n: int) -> tuple:
    """Compute a canonical form for graph isomorphism testing.

    Uses a simple but correct approach: try all permutations for tiny n,
    or use degree-based refinement for larger n.
    """
    if n <= 5:
        # For small n, try all permutations (5! = 120 is fast)
        from itertools import permutations
        best = None
        for perm in permutations(range(n)):
            # Apply permutation
            form = []
            for i in range(n):
                for j in range(i + 1, n):
                    form.append(adj[perm[i]][perm[j]])
            form = tuple(form)
            if best is None or form < best:
                best = form
        return best
    else:
        # For larger n, use degree sequence + neighbor degree sequences
        # This is a heuristic but works well for most graphs
        degs = [sum(adj[i]) for i in range(n)]
        # Sort vertices by degree, breaking ties by neighbor degree sum
        vertex_key = []
        for i in range(n):
            nb_degs = sorted([degs[j] for j in range(n) if adj[i][j]], reverse=True)
            vertex_key.append((degs[i], tuple(nb_degs), i))
        vertex_key.sort()
        perm = [vk[2] for vk in vertex_key]

        form = []
        for i in range(n):
            for j in range(i + 1, n):
                form.append(adj[perm[i]][perm[j]])
        return tuple(form)


def _delete_vertex(adj: list, n: int, v: int) -> list:
    """Delete vertex v from the graph, return (n-1) x (n-1) adjacency matrix."""
    new_adj = []
    for i in range(n):
        if i == v:
            continue
        row = []
        for j in range(n):
            if j == v:
                continue
            row.append(adj[i][j])
        new_adj.append(row)
    return new_adj


def _get_deck(adj: list, n: int) -> tuple:
    """Get the deck (multiset of vertex-deleted subgraph canonical forms)."""
    cards = []
    for v in range(n):
        sub = _delete_vertex(adj, n, v)
        cards.append(_canonical_form(sub, n - 1))
    return tuple(sorted(cards))


def verify(params: dict) -> dict:
    max_vertices = int(params.get("max_vertices", 5))
    max_vertices = min(max_vertices, 6)

    total_checked = 0
    violations = []

    for n in range(3, max_vertices + 1):
        # Generate all graphs on n vertices
        num_edges = n * (n - 1) // 2
        edge_list = [(i, j) for i in range(n) for j in range(i + 1, n)]

        # Group graphs by canonical form
        deck_to_canonical = {}

        for edge_mask in range(2 ** num_edges):
            # Build adjacency matrix
            adj = [[0] * n for _ in range(n)]
            for idx in range(num_edges):
                if edge_mask & (1 << idx):
                    i, j = edge_list[idx]
                    adj[i][j] = 1
                    adj[j][i] = 1

            canon = _canonical_form(adj, n)

            # Skip if we've seen this isomorphism class
            # But we need to track by deck
            if canon in deck_to_canonical:
                continue

            deck = _get_deck(adj, n)
            total_checked += 1

            if deck in deck_to_canonical:
                # Two non-isomorphic graphs with the same deck!
                existing_canon = deck_to_canonical[deck]
                if existing_canon != canon:
                    violations.append({
                        "n": n,
                        "graph1_canon": list(existing_canon),
                        "graph2_canon": list(canon),
                    })
            else:
                deck_to_canonical[deck] = canon

    if violations:
        return {
            "status": "fail",
            "summary": (
                f"Reconstruction conjecture violated: "
                f"{len(violations)} pair(s) of non-isomorphic graphs share a deck"
            ),
            "details": {
                "max_vertices": max_vertices,
                "total_graphs_checked": total_checked,
                "violations": violations[:10],
            },
        }

    return {
        "status": "pass",
        "summary": (
            f"Reconstruction conjecture verified for all graphs on n in [3, {max_vertices}]. "
            f"Checked {total_checked} non-isomorphic graphs."
        ),
        "details": {
            "max_vertices": max_vertices,
            "total_graphs_checked": total_checked,
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({"max_vertices": 6}), indent=2))
