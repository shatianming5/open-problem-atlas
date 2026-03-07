"""Selfridge's conjecture (PSW pseudoprime) checker.

Searches for a composite number that is both a strong pseudoprime to base 2
and a Lucas pseudoprime. No such number is known to exist.
Checks all composites up to `upper_bound`.
"""


def _is_strong_pseudoprime_base2(n: int) -> bool:
    """Miller-Rabin test with base 2 only."""
    if n < 2 or n % 2 == 0:
        return n == 2
    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1
    x = pow(2, d, n)
    if x == 1 or x == n - 1:
        return True
    for _ in range(r - 1):
        x = pow(x, 2, n)
        if x == n - 1:
            return True
    return False


def _jacobi(a: int, n: int) -> int:
    """Compute the Jacobi symbol (a/n)."""
    if n <= 0 or n % 2 == 0:
        raise ValueError("n must be a positive odd integer")
    a = a % n
    result = 1
    while a != 0:
        while a % 2 == 0:
            a //= 2
            if n % 8 in (3, 5):
                result = -result
        a, n = n, a
        if a % 4 == 3 and n % 4 == 3:
            result = -result
        a = a % n
    return result if n == 1 else 0


def _is_lucas_pseudoprime(n: int) -> bool:
    """Standard Lucas pseudoprime test with Selfridge's method A parameters."""
    if n < 2 or n % 2 == 0:
        return n == 2

    # Find D using Selfridge's method A
    d_val = 5
    sign = 1
    while True:
        D = d_val * sign
        j = _jacobi(D, n)
        if j == 0:
            return D == n  # n divides D means n is small factor
        if j == -1:
            break
        d_val += 2
        sign = -sign
        if d_val > 1000:
            return False  # safety

    P = 1
    Q = (1 - D) // 4

    # Compute Lucas U_{n+1} mod n using binary method
    k = n + 1
    bits = bin(k)[2:]
    U, V = 0, 2
    Qk = Q
    for bit in bits:
        U, V = (U * V) % n, (V * V - 2 * Qk) % n
        Qk = pow(Qk, 2, n)
        if bit == '1':
            U, V = (P * U + V) * pow(2, n - 2, n) % n, (P * V + D * U) * pow(2, n - 2, n) % n
            Qk = (Qk * Q) % n

    return U % n == 0


def _is_prime_small(n: int) -> bool:
    """Trial division primality test for small numbers."""
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
    upper_bound = int(params.get("upper_bound", 10**6))

    checked = 0
    for n in range(3, upper_bound + 1, 2):  # Skip evens
        if _is_prime_small(n):
            continue
        checked += 1
        if _is_strong_pseudoprime_base2(n) and _is_lucas_pseudoprime(n):
            return {
                "status": "fail",
                "summary": f"Found PSW pseudoprime: {n}",
                "details": {"counterexample": n},
            }

    return {
        "status": "pass",
        "summary": f"No PSW pseudoprime found up to {upper_bound} ({checked} composites checked)",
        "details": {"upper_bound": upper_bound, "composites_checked": checked},
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({"upper_bound": 10000}), indent=2))
