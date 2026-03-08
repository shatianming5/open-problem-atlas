"""Lehmer's totient problem checker.

Lehmer's conjecture: if phi(n) divides (n-1), then n is prime.
Equivalently, there is no composite n with phi(n) | (n-1).
Checks all n up to max_n.
"""


def _euler_phi(n: int) -> int:
    """Compute Euler's totient function."""
    result = n
    p = 2
    temp = n
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            result -= result // p
        p += 1
    if temp > 1:
        result -= result // temp
    return result


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def verify(params: dict) -> dict:
    max_n = int(params.get("max_n", 10000))
    max_n = min(max_n, 100000)

    checked = 0
    for n in range(2, max_n + 1):
        if _is_prime(n):
            continue
        checked += 1
        phi_n = _euler_phi(n)
        if (n - 1) % phi_n == 0:
            return {
                "status": "fail",
                "summary": f"Lehmer counterexample found: n={n}, phi(n)={phi_n}",
                "details": {"counterexample": n, "phi_n": phi_n},
            }

    return {
        "status": "pass",
        "summary": (
            f"Lehmer's totient conjecture verified for all composite n "
            f"up to {max_n} ({checked} composites checked)"
        ),
        "details": {"max_n": max_n, "composites_checked": checked},
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({}), indent=2))
