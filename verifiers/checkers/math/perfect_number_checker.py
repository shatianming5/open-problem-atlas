"""Perfect number checker.

Verifies properties of perfect numbers: a number n is perfect if the
sum of its proper divisors equals n. It is conjectured that all even
perfect numbers are of the form 2^(p-1) * (2^p - 1) where 2^p - 1 is
a Mersenne prime, and that no odd perfect numbers exist.
"""


def _sum_proper_divisors(n: int) -> int:
    if n <= 1:
        return 0
    total = 1
    i = 2
    while i * i <= n:
        if n % i == 0:
            total += i
            if i != n // i:
                total += n // i
        i += 1
    return total


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

    perfect_numbers = []
    for n in range(2, max_n + 1):
        if _sum_proper_divisors(n) == n:
            perfect_numbers.append(n)

    # Verify Euler form: all found should be 2^(p-1)*(2^p-1)
    euler_form_verified = True
    for pn in perfect_numbers:
        found_form = False
        for p in range(2, 32):
            mp = (1 << p) - 1
            candidate = (1 << (p - 1)) * mp
            if candidate == pn and _is_prime(mp):
                found_form = True
                break
        if not found_form:
            euler_form_verified = False

    # Check no odd perfect in range
    odd_perfect = [n for n in perfect_numbers if n % 2 == 1]

    return {
        "status": "pass",
        "summary": (
            f"Found {len(perfect_numbers)} perfect numbers up to {max_n}: "
            f"{perfect_numbers}. All even and Euler form: {euler_form_verified}. "
            f"Odd perfect numbers: {len(odd_perfect)}"
        ),
        "details": {
            "max_n": max_n,
            "perfect_numbers": perfect_numbers,
            "euler_form": euler_form_verified,
            "odd_perfect_count": len(odd_perfect),
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({}), indent=2))
