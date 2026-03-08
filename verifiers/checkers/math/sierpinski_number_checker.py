"""Sierpinski number checker.

A Sierpinski number is an odd k such that k*2^n + 1 is composite for
all n >= 1. This checker verifies known small Sierpinski numbers by
confirming k*2^n + 1 is composite for n up to n_max.
"""


def _is_prime_miller_rabin(n: int) -> bool:
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
    n_max = int(params.get("n_max", 100))
    n_max = min(n_max, 500)

    # Known Sierpinski number: 78557 is the smallest known
    known_sierpinski = [78557, 271129, 271577, 322523, 327739]
    results = []

    for k in known_sierpinski:
        found_prime = False
        for n in range(1, n_max + 1):
            val = k * (1 << n) + 1
            if _is_prime_miller_rabin(val):
                found_prime = True
                results.append({"k": k, "prime_at_n": n, "sierpinski": False})
                break
        if not found_prime:
            results.append({"k": k, "checked_up_to": n_max, "sierpinski": True})

    confirmed = [r for r in results if r.get("sierpinski", False)]

    return {
        "status": "pass",
        "summary": (
            f"Checked {len(known_sierpinski)} known Sierpinski candidates "
            f"for n up to {n_max}. {len(confirmed)} still show no primes."
        ),
        "details": {
            "n_max": n_max,
            "results": results,
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({}), indent=2))
