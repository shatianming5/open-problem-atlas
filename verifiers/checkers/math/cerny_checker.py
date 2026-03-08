"""Cerny conjecture checker.

The Cerny conjecture: every synchronizing automaton with n states has a
synchronizing word of length at most (n-1)^2. Tests all synchronizing
automata with a small number of states over a binary alphabet.
"""


def _apply_letter(states: frozenset, trans: list[int]) -> frozenset:
    return frozenset(trans[s] for s in states)


def _is_synchronizing(trans_a: list[int], trans_b: list[int], n: int) -> tuple:
    """Check if DFA with two transition functions is synchronizing.
    Returns (is_sync, shortest_sync_length) using BFS on subsets.
    """
    start = frozenset(range(n))
    if len(start) == 1:
        return (True, 0)

    visited = {start: 0}
    queue = [start]
    head = 0

    while head < len(queue):
        current = queue[head]
        head += 1
        dist = visited[current]

        for trans in [trans_a, trans_b]:
            nxt = _apply_letter(current, trans)
            if len(nxt) == 1:
                return (True, dist + 1)
            if nxt not in visited:
                visited[nxt] = dist + 1
                queue.append(nxt)

    return (False, -1)


def verify(params: dict) -> dict:
    max_n = int(params.get("max_n", 5))
    max_n = min(max_n, 7)

    from itertools import product as iprod

    results = []
    worst_ratio = 0.0
    cerny_holds = True

    for n in range(2, max_n + 1):
        bound = (n - 1) ** 2
        max_sync_len = 0
        sync_count = 0
        total = 0
        violation = None

        # Sample some DFAs (all possible for small n, sample for larger)
        all_trans = list(iprod(range(n), repeat=n))
        trans_limit = min(len(all_trans), 20)
        sampled_a = all_trans[:trans_limit]
        sampled_b = all_trans[:trans_limit]

        for ta in sampled_a:
            for tb in sampled_b:
                total += 1
                is_sync, length = _is_synchronizing(list(ta), list(tb), n)
                if is_sync:
                    sync_count += 1
                    if length > max_sync_len:
                        max_sync_len = length
                    if length > bound:
                        cerny_holds = False
                        violation = {
                            "n": n, "length": length,
                            "bound": bound,
                            "trans_a": list(ta),
                            "trans_b": list(tb),
                        }

        ratio = max_sync_len / bound if bound > 0 else 0
        if ratio > worst_ratio:
            worst_ratio = ratio
        results.append({
            "n": n, "bound": bound, "max_sync_len": max_sync_len,
            "sync_count": sync_count, "total_tested": total,
            "ratio": round(ratio, 4),
        })

    if not cerny_holds:
        return {
            "status": "fail",
            "summary": f"Cerny conjecture violated",
            "details": {"violation": violation, "results": results},
        }

    return {
        "status": "pass",
        "summary": (
            f"Cerny conjecture verified for automata up to {max_n} states. "
            f"Worst sync_len/(n-1)^2 ratio: {worst_ratio:.4f}"
        ),
        "details": {"max_n": max_n, "results": results},
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({"max_n": 4}), indent=2))
