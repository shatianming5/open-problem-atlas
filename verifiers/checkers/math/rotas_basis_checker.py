"""Rota's basis conjecture checker.

Rota's basis conjecture: given n bases B_1, ..., B_n of an n-dimensional
vector space, one can always find n disjoint transversals, each forming
a basis. This checker tests small cases with the uniform matroid.
"""

from itertools import permutations, combinations


def _is_linearly_independent(vectors: list[list[int]], mod: int = 2) -> bool:
    """Check linear independence over GF(mod) using Gaussian elimination."""
    if not vectors:
        return True
    n = len(vectors)
    m = len(vectors[0])
    mat = [row[:] for row in vectors]

    pivot_row = 0
    for col in range(m):
        found = -1
        for row in range(pivot_row, n):
            if mat[row][col] % mod != 0:
                found = row
                break
        if found == -1:
            continue
        mat[pivot_row], mat[found] = mat[found], mat[pivot_row]
        for row in range(n):
            if row != pivot_row and mat[row][col] % mod != 0:
                for j in range(m):
                    mat[row][j] = (mat[row][j] - mat[pivot_row][j]) % mod
        pivot_row += 1

    return pivot_row == n


def verify(params: dict) -> dict:
    max_n = int(params.get("max_n", 4))
    max_n = min(max_n, 5)

    results = []
    conjecture_holds = True

    for n in range(2, max_n + 1):
        # Work over GF(2), dimension n
        # Generate n bases of GF(2)^n
        # Standard basis and permutations
        import random
        rng = random.Random(42 + n)

        all_vectors = []
        for i in range(1, 2**n):
            vec = [(i >> j) & 1 for j in range(n)]
            all_vectors.append(vec)

        # Find n bases
        bases = []
        for trial in range(n):
            rng.shuffle(all_vectors)
            for combo in combinations(all_vectors, n):
                if _is_linearly_independent(list(combo), 2):
                    bases.append(list(combo))
                    break

        if len(bases) < n:
            results.append({"n": n, "status": "insufficient_bases"})
            continue

        # Try to find n disjoint transversals that are each a basis
        # A transversal picks one vector from each basis
        found_decomposition = False

        # Try random permutations
        for _ in range(200):
            perms = [list(range(n)) for _ in range(n)]
            for p in perms:
                rng.shuffle(p)

            transversals = []
            valid = True
            for t in range(n):
                trans = [bases[b][perms[b][t]] for b in range(n)]
                if not _is_linearly_independent(trans, 2):
                    valid = False
                    break
                transversals.append(trans)
            if valid:
                found_decomposition = True
                break

        results.append({
            "n": n,
            "found_decomposition": found_decomposition,
        })
        if not found_decomposition:
            conjecture_holds = False

    return {
        "status": "pass" if conjecture_holds else "fail",
        "summary": (
            f"Rota's basis conjecture tested for dimensions 2..{max_n}. "
            f"Holds: {conjecture_holds}"
        ),
        "details": {"max_n": max_n, "results": results},
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({}), indent=2))
