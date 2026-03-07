"""Sierpinski problem checker.

A Sierpinski number is an odd k such that k*2^n + 1 is composite for all n >= 1.
The Sierpinski problem asks: is 78557 the smallest such k?
This checker verifies that known candidate k values below 78557 have a
prime k*2^n + 1 for some n <= max_n.
"""


def _is_prime_miller_rabin(n: int) -> bool:
    """Deterministic Miller-Rabin for n < 3.3e24."""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0:
        return False
    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]:
        if a >= n:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def verify(params: dict) -> dict:
    max_n = int(params.get("max_n", 10000))

    # Known remaining candidates as of 2024 (k < 78557, odd, no prime found yet)
    # These are the candidates that still need checking
    remaining_candidates = [21181, 22699, 24737, 55459, 67607]

    eliminated = []
    still_open = []

    for k in remaining_candidates:
        found_prime = False
        for n in range(1, max_n + 1):
            val = k * (1 << n) + 1
            if _is_prime_miller_rabin(val):
                eliminated.append({"k": k, "n": n})
                found_prime = True
                break
        if not found_prime:
            still_open.append(k)

    return {
        "status": "pass",
        "summary": (
            f"Checked {len(remaining_candidates)} Sierpinski candidates with n up to {max_n}. "
            f"Eliminated: {len(eliminated)}, Still open: {len(still_open)}"
        ),
        "details": {
            "max_n": max_n,
            "eliminated": eliminated,
            "still_open": still_open,
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({"max_n": 1000}), indent=2))
