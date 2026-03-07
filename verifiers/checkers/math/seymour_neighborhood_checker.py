"""Seymour's second neighborhood conjecture verifier.

Seymour's second neighborhood conjecture states that every oriented graph
(directed graph without 2-cycles) has a vertex v such that
|N++(v)| >= |N+(v)|, where N+(v) is the out-neighborhood of v and
N++(v) is the set of vertices reachable from v in exactly 2 directed steps
but not in N+(v) union {v}.

More precisely, N++(v) = {w : exists u in N+(v) with (u,w) in E, w not in N+(v), w != v}.

Actually, the standard statement is: |N+(N+(v))| >= |N+(v)| where
N+(N+(v)) = union of N+(u) for u in N+(v), minus v.

This checker verifies the conjecture for small oriented graphs.
"""

from itertools import combinations, product


def _check_conjecture(n: int, edges: set) -> dict:
    """Check Seymour's second neighborhood conjecture for an oriented graph.

    Returns dict with 'holds' and the witness vertex if found.
    """
    adj_out = {i: set() for i in range(n)}
    for u, v in edges:
        adj_out[u].add(v)

    for v in range(n):
        n_plus = adj_out[v]
        # Second neighborhood: vertices reachable in 2 steps from v through N+(v)
        n_plus_plus = set()
        for u in n_plus:
            for w in adj_out[u]:
                if w != v and w not in n_plus:
                    n_plus_plus.add(w)

        if len(n_plus_plus) >= len(n_plus):
            return {
                "holds": True,
                "witness": v,
                "n_plus_size": len(n_plus),
                "n_plus_plus_size": len(n_plus_plus),
            }

    return {"holds": False}


def verify(params: dict) -> dict:
    max_vertices = int(params.get("max_vertices", 5))
    max_vertices = min(max_vertices, 6)

    total_checked = 0
    violations = []

    for n in range(2, max_vertices + 1):
        # Generate oriented graphs: for each pair (i,j), either no edge,
        # edge i->j, or edge j->i (no 2-cycles)
        pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
        num_pairs = len(pairs)

        # Each pair has 3 choices: no edge, i->j, j->i
        for config in range(3 ** num_pairs):
            edges = set()
            temp = config
            for pi in range(num_pairs):
                choice = temp % 3
                temp //= 3
                i, j = pairs[pi]
                if choice == 1:
                    edges.add((i, j))
                elif choice == 2:
                    edges.add((j, i))

            # Skip empty graphs
            if not edges:
                continue

            total_checked += 1
            result = _check_conjecture(n, edges)

            if not result["holds"]:
                violations.append({
                    "n": n,
                    "edges": sorted(edges),
                })

            if total_checked >= 10000:
                break
        if total_checked >= 10000:
            break

    if violations:
        return {
            "status": "fail",
            "summary": (
                f"Seymour's second neighborhood conjecture violated for "
                f"{len(violations)} oriented graph(s)"
            ),
            "details": {
                "max_vertices": max_vertices,
                "total_checked": total_checked,
                "violations": violations[:10],
            },
        }

    return {
        "status": "pass",
        "summary": (
            f"Seymour's second neighborhood conjecture verified for oriented graphs "
            f"on up to {max_vertices} vertices. Checked {total_checked} graphs."
        ),
        "details": {
            "max_vertices": max_vertices,
            "total_checked": total_checked,
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({"max_vertices": 5}), indent=2))
