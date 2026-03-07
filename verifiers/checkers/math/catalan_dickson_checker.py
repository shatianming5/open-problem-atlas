"""Catalan-Dickson conjecture (aliquot sequences) verifier.

The Catalan-Dickson conjecture states that every aliquot sequence
(iterating s(n) = sigma(n) - n, where sigma is the sum of divisors)
either terminates at 0 (for perfect or deficient numbers) or enters a
cycle (perfect numbers give period 1, amicable numbers give period 2, etc.).

The conjecture is widely believed to be FALSE -- the Lehmer five
(276, 552, 564, 660, 966) are sequences that have been computed to
enormous lengths without terminating or cycling.

This checker tracks aliquot sequences for small starting values, looking
for termination, cycles, or unbounded growth.
"""


def _sum_of_proper_divisors(n: int) -> int:
    """Compute s(n) = sigma(n) - n = sum of proper divisors of n."""
    if n <= 1:
        return 0
    total = 1  # 1 is always a proper divisor for n > 1
    i = 2
    while i * i <= n:
        if n % i == 0:
            total += i
            if i != n // i:
                total += n // i
        i += 1
    return total


def verify(params: dict) -> dict:
    upper_bound = int(params.get("upper_bound", 1000))
    max_steps = int(params.get("max_steps", 200))

    terminated = 0
    cycled = 0
    unresolved = 0
    perfect_numbers = []
    amicable_pairs = []
    unresolved_starts = []

    for start in range(2, upper_bound + 1):
        sequence = [start]
        visited = {start: 0}
        n = start

        for step in range(1, max_steps + 1):
            n = _sum_of_proper_divisors(n)
            if n == 0:
                terminated += 1
                break
            if n in visited:
                cycle_start = visited[n]
                cycle_len = step - cycle_start
                cycled += 1
                if cycle_len == 1 and n == start:
                    perfect_numbers.append(start)
                elif cycle_len == 2:
                    amicable_pairs.append(start)
                break
            visited[n] = step
            sequence.append(n)
        else:
            unresolved += 1
            if len(unresolved_starts) < 10:
                unresolved_starts.append({
                    "start": start,
                    "last_value": sequence[-1],
                    "steps": len(sequence),
                    "max_value": max(sequence),
                })

    total = terminated + cycled + unresolved

    return {
        "status": "pass",
        "summary": (
            f"Aliquot sequences checked for starts in [2, {upper_bound}]. "
            f"Terminated: {terminated}, Cycled: {cycled}, "
            f"Unresolved after {max_steps} steps: {unresolved}."
        ),
        "details": {
            "upper_bound": upper_bound,
            "max_steps": max_steps,
            "total_checked": total,
            "terminated": terminated,
            "cycled": cycled,
            "unresolved": unresolved,
            "perfect_numbers": perfect_numbers,
            "amicable_pairs_starts": amicable_pairs[:10],
            "unresolved_sample": unresolved_starts,
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({"upper_bound": 500, "max_steps": 100}), indent=2))
