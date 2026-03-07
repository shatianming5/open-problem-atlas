"""Erdos-Straus conjecture verifier.

The Erdos-Straus conjecture states that for every integer n >= 2,
the fraction 4/n can be written as a sum of three unit fractions:
4/n = 1/a + 1/b + 1/c, where a, b, c are positive integers.

This checker verifies the conjecture for all n up to upper_bound by
searching for such decompositions.
"""


def _find_decomposition(n: int) -> tuple:
    """Try to find a, b, c such that 4/n = 1/a + 1/b + 1/c.

    Returns (a, b, c) if found, else None.
    Strategy: fix a, then solve 4/n - 1/a = 1/b + 1/c.
    """
    # 4/n = 1/a + 1/b + 1/c
    # a must be >= ceil(n/4) (since 1/a <= 4/n) and a <= 3n (rough upper bound)
    for a in range((n + 3) // 4, 3 * n + 1):
        # Remaining: 4/n - 1/a = (4a - n) / (na)
        num = 4 * a - n
        den = n * a
        if num <= 0:
            continue
        # Need 1/b + 1/c = num/den with b <= c
        # b >= ceil(den/num) (since 1/b <= num/den)
        # b <= 2*den/num (since 1/b >= num/(2*den))
        b_min = (den + num - 1) // num
        b_max = 2 * den // num
        for b in range(b_min, b_max + 1):
            # 1/c = num/den - 1/b = (num*b - den) / (den*b)
            c_num = num * b - den
            c_den = den * b
            if c_num <= 0:
                continue
            if c_den % c_num == 0:
                c = c_den // c_num
                if c >= b:
                    return (a, b, c)
    return None


def verify(params: dict) -> dict:
    upper_bound = int(params.get("upper_bound", 10000))

    checked = 0
    failures = []

    for n in range(2, upper_bound + 1):
        result = _find_decomposition(n)
        if result is None:
            failures.append(n)
            if len(failures) >= 5:
                break
        checked += 1

    if failures:
        return {
            "status": "fail",
            "summary": (
                f"Erdos-Straus conjecture: no decomposition found for n={failures}"
            ),
            "details": {
                "upper_bound": upper_bound,
                "checked": checked,
                "failures": failures,
            },
        }

    return {
        "status": "pass",
        "summary": (
            f"Erdos-Straus conjecture verified for all n in [2, {upper_bound}]"
        ),
        "details": {
            "upper_bound": upper_bound,
            "checked": checked,
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({"upper_bound": 10000}), indent=2))
