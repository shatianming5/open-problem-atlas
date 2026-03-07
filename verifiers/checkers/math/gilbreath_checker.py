"""Gilbreath's conjecture verifier.

Gilbreath's conjecture: starting with the sequence of primes and repeatedly
taking absolute differences of consecutive terms, the first term is always 1.
Verifies for the first `num_primes` primes.
"""


def _sieve(limit: int) -> list[int]:
    """Simple sieve of Eratosthenes."""
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False
    return [i for i in range(2, limit + 1) if is_prime[i]]


def verify(params: dict) -> dict:
    num_primes = int(params.get("num_primes", 100000))

    # Generate enough primes
    limit = max(num_primes * 15, 10000)
    primes = _sieve(limit)
    while len(primes) < num_primes:
        limit *= 2
        primes = _sieve(limit)
    primes = primes[:num_primes]

    # Iteratively take absolute differences and check first element
    seq = list(primes)
    rows_checked = 0

    for row in range(1, len(seq)):
        new_seq = [abs(seq[i + 1] - seq[i]) for i in range(len(seq) - 1)]
        if not new_seq:
            break
        if new_seq[0] != 1:
            return {
                "status": "fail",
                "summary": f"Gilbreath's conjecture fails at row {row}: first element is {new_seq[0]}",
                "details": {"row": row, "first_element": new_seq[0]},
            }
        rows_checked += 1
        seq = new_seq
        # Only need to check until sequence length becomes small
        if len(seq) <= 1:
            break

    return {
        "status": "pass",
        "summary": f"Gilbreath's conjecture verified for first {num_primes} primes ({rows_checked} rows)",
        "details": {"num_primes": num_primes, "rows_checked": rows_checked},
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({"num_primes": 1000}), indent=2))
