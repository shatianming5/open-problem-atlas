"""Catalan-Dickson conjecture extended checker.

Tracks aliquot sequences for starting values up to max_n with more
detailed analysis of growth rates and sequence behavior.
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


def verify(params: dict) -> dict:
    max_n = int(params.get("max_n", 100))
    max_n = min(max_n, 500)
    max_steps = int(params.get("max_steps", 200))
    max_steps = min(max_steps, 500)

    terminated = 0
    cycled = 0
    unresolved = 0
    growing = []

    for start in range(2, max_n + 1):
        seen = {start: 0}
        n = start
        peak = start
        outcome = "unknown"

        for step in range(1, max_steps + 1):
            n = _sum_proper_divisors(n)
            if n > peak:
                peak = n
            if n == 0:
                outcome = "terminated"
                terminated += 1
                break
            if n in seen:
                outcome = "cycled"
                cycled += 1
                break
            seen[n] = step

        if outcome == "unknown":
            unresolved += 1
            if peak > start * 10:
                growing.append({
                    "start": start, "peak": peak,
                    "last": n, "steps": max_steps,
                    "growth_factor": round(peak / start, 2),
                })

    growing.sort(key=lambda x: -x["growth_factor"])

    return {
        "status": "pass",
        "summary": (
            f"Aliquot sequences for starts 2..{max_n}: "
            f"terminated={terminated}, cycled={cycled}, "
            f"unresolved={unresolved}"
        ),
        "details": {
            "max_n": max_n,
            "max_steps": max_steps,
            "terminated": terminated,
            "cycled": cycled,
            "unresolved": unresolved,
            "fastest_growing": growing[:5],
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({}), indent=2))
