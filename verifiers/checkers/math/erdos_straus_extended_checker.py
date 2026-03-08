"""Erdos-Straus conjecture extended checker (odd n only).

Verifies 4/n = 1/a + 1/b + 1/c has a solution for odd n up to max_n.
Even n are trivially handled since 4/n = 1/(n/2) + 1/(n/2) + ... ,
so this focuses on the harder odd cases.
"""


def _find_decomposition(n: int) -> tuple | None:
    """Find a, b, c with 4/n = 1/a + 1/b + 1/c, a <= b <= c."""
    for a in range((n + 3) // 4, 3 * n + 1):
        num = 4 * a - n
        den = n * a
        if num <= 0:
            continue
        b_min = (den + num - 1) // num
        b_max = 2 * den // num
        for b in range(b_min, b_max + 1):
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
    max_n = int(params.get("max_n", 10000))
    max_n = min(max_n, 100000)

    checked = 0
    failures = []

    for n in range(3, max_n + 1, 2):  # odd n only
        result = _find_decomposition(n)
        if result is None:
            failures.append(n)
            if len(failures) >= 5:
                break
        checked += 1

    if failures:
        return {
            "status": "fail",
            "summary": f"No decomposition found for odd n={failures}",
            "details": {"failures": failures, "checked": checked},
        }

    return {
        "status": "pass",
        "summary": (
            f"Erdos-Straus verified for all odd n in [3, {max_n}] "
            f"({checked} checked)"
        ),
        "details": {"max_n": max_n, "checked": checked},
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({"max_n": 1000}), indent=2))
