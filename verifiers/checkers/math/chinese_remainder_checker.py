"""Chinese Remainder Theorem checker.

Verifies the Chinese Remainder Theorem: for pairwise coprime moduli
m_1, ..., m_k and any residues a_1, ..., a_k, there exists a unique
solution x mod (m_1 * ... * m_k). Tests correctness of CRT solutions
for small moduli sets.
"""

from math import gcd
from itertools import combinations


def _extended_gcd(a: int, b: int) -> tuple:
    if a == 0:
        return b, 0, 1
    g, x1, y1 = _extended_gcd(b % a, a)
    return g, y1 - (b // a) * x1, x1


def _crt(residues: list[int], moduli: list[int]) -> int | None:
    """Solve system x = a_i mod m_i using CRT."""
    if not moduli:
        return None
    # Check pairwise coprime
    for i in range(len(moduli)):
        for j in range(i + 1, len(moduli)):
            if gcd(moduli[i], moduli[j]) != 1:
                return None

    M = 1
    for m in moduli:
        M *= m

    x = 0
    for ai, mi in zip(residues, moduli):
        Mi = M // mi
        _, inv, _ = _extended_gcd(Mi % mi, mi)
        x += ai * Mi * inv

    return x % M


def verify(params: dict) -> dict:
    max_n = int(params.get("max_n", 20))
    max_n = min(max_n, 50)

    # Generate test cases with small primes as moduli
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    primes = [p for p in primes if p <= max_n]

    total_tests = 0
    failures = []

    # Test all pairs and triples of primes
    for k in range(2, min(len(primes) + 1, 5)):
        for mod_combo in combinations(primes, k):
            moduli = list(mod_combo)
            M = 1
            for m in moduli:
                M *= m

            # Test several residue combinations
            import random
            rng = random.Random(42 + sum(moduli))
            for _ in range(10):
                residues = [rng.randint(0, m - 1) for m in moduli]
                x = _crt(residues, moduli)

                if x is None:
                    continue

                total_tests += 1
                # Verify solution
                for ai, mi in zip(residues, moduli):
                    if x % mi != ai:
                        failures.append({
                            "moduli": moduli,
                            "residues": residues,
                            "solution": x,
                            "failed_mod": mi,
                        })
                        break

    if failures:
        return {
            "status": "fail",
            "summary": f"CRT verification failed in {len(failures)} cases",
            "details": {"failures": failures[:10]},
        }

    return {
        "status": "pass",
        "summary": (
            f"CRT verified for {total_tests} systems with moduli from "
            f"primes up to {max(primes) if primes else 0}"
        ),
        "details": {
            "max_n": max_n,
            "total_tests": total_tests,
            "primes_used": primes,
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({}), indent=2))
