"""Collatz conjecture range verifier.

Verifies that the Collatz sequence reaches 1 for all integers in [1, upper_bound].
"""


def verify(params: dict) -> dict:
    upper_bound = int(params.get("upper_bound", 10**7))

    checked = 0
    for n in range(1, upper_bound + 1):
        x = n
        steps = 0
        while x != 1:
            if x % 2 == 0:
                x //= 2
            else:
                x = 3 * x + 1
            steps += 1
            if steps > 10000:
                return {
                    "status": "fail",
                    "summary": f"Collatz sequence for {n} did not reach 1 within 10000 steps",
                    "details": {"failing_n": n, "steps": steps},
                }
        checked += 1

    return {
        "status": "pass",
        "summary": f"Collatz conjecture verified for all n in [1, {upper_bound}]",
        "details": {"checked": checked, "upper_bound": upper_bound},
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({"upper_bound": 100000}), indent=2))
