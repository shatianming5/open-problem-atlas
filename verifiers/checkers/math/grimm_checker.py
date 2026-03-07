"""Grimm's conjecture verifier.

Grimm's conjecture: for every consecutive sequence of composite numbers
n+1, n+2, ..., n+k (between consecutive primes), there exist distinct primes
p_1, p_2, ..., p_k such that p_i divides n+i for each i.
Verifies for composites up to `upper_bound`.
"""


def _sieve(limit: int) -> list[bool]:
    """Sieve of Eratosthenes returning boolean array."""
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False
    return is_prime


def _prime_factors(n: int) -> set[int]:
    """Return the set of prime factors of n."""
    factors = set()
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 1
    if n > 1:
        factors.add(n)
    return factors


def _can_match(composites: list[int]) -> bool:
    """Check if distinct prime factors can be assigned to each composite (bipartite matching)."""
    if not composites:
        return True

    # Build bipartite graph: composite -> set of prime factors
    factor_sets = [_prime_factors(c) for c in composites]
    all_primes = sorted(set().union(*factor_sets))
    prime_idx = {p: i for i, p in enumerate(all_primes)}

    n = len(composites)
    m = len(all_primes)
    match_prime = [-1] * m  # which composite is matched to each prime

    def try_kuhn(v: int, visited: list[bool]) -> bool:
        for p in factor_sets[v]:
            pi = prime_idx[p]
            if not visited[pi]:
                visited[pi] = True
                if match_prime[pi] == -1 or try_kuhn(match_prime[pi], visited):
                    match_prime[pi] = v
                    return True
        return False

    matched = 0
    for i in range(n):
        visited = [False] * m
        if try_kuhn(i, visited):
            matched += 1

    return matched == n


def verify(params: dict) -> dict:
    upper_bound = int(params.get("upper_bound", 10**6))

    is_prime = _sieve(upper_bound + 1)

    # Find consecutive composite runs between primes
    gaps_checked = 0
    i = 2
    while i <= upper_bound:
        if is_prime[i]:
            i += 1
            continue
        # Start of composite run
        composites = []
        j = i
        while j <= upper_bound and not is_prime[j]:
            composites.append(j)
            j += 1

        if composites and not _can_match(composites):
            return {
                "status": "fail",
                "summary": f"Grimm's conjecture fails for composite run starting at {composites[0]}",
                "details": {"run_start": composites[0], "run_length": len(composites)},
            }
        gaps_checked += 1
        i = j

    return {
        "status": "pass",
        "summary": f"Grimm's conjecture verified up to {upper_bound} ({gaps_checked} composite gaps checked)",
        "details": {"upper_bound": upper_bound, "gaps_checked": gaps_checked},
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({"upper_bound": 10000}), indent=2))
