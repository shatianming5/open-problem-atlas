"""Gilbreath's conjecture checker (row-based variant).

Gilbreath's conjecture: starting with the sequence of primes and repeatedly
taking absolute differences, the leading term of each row is always 1.
This variant checks up to max_rows rows.
"""


def _sieve(limit: int) -> list[int]:
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False
    return [i for i in range(2, limit + 1) if is_prime[i]]


def verify(params: dict) -> dict:
    max_rows = int(params.get("max_rows", 100))
    max_rows = min(max_rows, 500)

    num_primes = max_rows + 10
    limit = max(num_primes * 15, 10000)
    primes = _sieve(limit)
    while len(primes) < num_primes:
        limit *= 2
        primes = _sieve(limit)
    primes = primes[:num_primes]

    seq = list(primes)
    leading_terms = [seq[0]]

    for row in range(1, max_rows + 1):
        seq = [abs(seq[i + 1] - seq[i]) for i in range(len(seq) - 1)]
        if not seq:
            break
        leading_terms.append(seq[0])
        if seq[0] != 1:
            return {
                "status": "fail",
                "summary": f"Gilbreath's conjecture fails at row {row}: leading term = {seq[0]}",
                "details": {"row": row, "leading_term": seq[0]},
            }

    return {
        "status": "pass",
        "summary": f"Gilbreath's conjecture verified for {max_rows} rows of differences",
        "details": {
            "max_rows": max_rows,
            "all_leading_ones": True,
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({}), indent=2))
