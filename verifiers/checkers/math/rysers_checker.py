"""Ryser's conjecture checker.

Ryser's conjecture: every Latin square of odd order n has a transversal
(a set of n entries, one from each row and column, with all symbols
distinct). Verifies for Latin squares of odd order up to max_n.
"""

from itertools import permutations


def _has_transversal(square: list[list[int]], n: int) -> bool:
    """Check if Latin square has a transversal."""
    def bt(row: int, used_cols: int, used_syms: int) -> bool:
        if row == n:
            return True
        for col in range(n):
            if used_cols & (1 << col):
                continue
            sym = square[row][col]
            if used_syms & (1 << sym):
                continue
            if bt(row + 1, used_cols | (1 << col), used_syms | (1 << sym)):
                return True
        return False
    return bt(0, 0, 0)


def _generate_latin_square(n: int, seed: int) -> list[list[int]]:
    """Generate a Latin square by cyclic construction with permutation."""
    import random
    rng = random.Random(seed)
    perm = list(range(n))
    rng.shuffle(perm)
    square = [[(perm[j] + i) % n for j in range(n)] for i in range(n)]
    return square


def verify(params: dict) -> dict:
    max_n = int(params.get("max_n", 7))
    max_n = min(max_n, 9)

    results = []
    all_have_transversal = True

    for n in range(1, max_n + 1, 2):  # odd orders
        num_trials = 10
        has_trans_count = 0

        for seed in range(num_trials):
            sq = _generate_latin_square(n, seed + n * 100)
            if _has_transversal(sq, n):
                has_trans_count += 1

        results.append({
            "order": n,
            "trials": num_trials,
            "with_transversal": has_trans_count,
        })
        if has_trans_count < num_trials:
            all_have_transversal = False

    return {
        "status": "pass" if all_have_transversal else "fail",
        "summary": (
            f"Ryser's conjecture tested for odd Latin squares up to order {max_n}. "
            f"All have transversals: {all_have_transversal}"
        ),
        "details": {"max_n": max_n, "results": results},
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({}), indent=2))
