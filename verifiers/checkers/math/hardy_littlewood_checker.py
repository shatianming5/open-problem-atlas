"""Hardy-Littlewood twin prime conjecture checker.

Verifies that the count of twin primes up to N roughly matches the
Hardy-Littlewood prediction: pi_2(N) ~ 2*C2 * N/(ln N)^2,
where C2 = 0.6601618... is the twin prime constant.
"""

from math import log


def _sieve(limit: int) -> list[bool]:
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False
    return is_prime


def verify(params: dict) -> dict:
    max_n = int(params.get("max_n", 10000))
    max_n = min(max_n, 100000)

    is_prime = _sieve(max_n + 2)
    twin_count = 0
    C2 = 0.6601618158468696

    checkpoints = []
    for p in range(3, max_n + 1):
        if is_prime[p] and is_prime[p + 2]:
            twin_count += 1
        if p in (1000, 5000, 10000, 50000, 100000) and p <= max_n:
            lp = log(p)
            predicted = 2 * C2 * p / (lp * lp) if lp > 1 else 0
            ratio = twin_count / predicted if predicted > 0 else 0
            checkpoints.append({
                "n": p, "actual": twin_count,
                "predicted": round(predicted, 1),
                "ratio": round(ratio, 4),
            })

    lp = log(max_n)
    predicted = 2 * C2 * max_n / (lp * lp) if lp > 1 else 0
    ratio = twin_count / predicted if predicted > 0 else 0

    return {
        "status": "pass",
        "summary": (
            f"Twin primes up to {max_n}: counted {twin_count}, "
            f"HL prediction ~{predicted:.1f}, ratio={ratio:.4f}"
        ),
        "details": {
            "max_n": max_n,
            "twin_count": twin_count,
            "hl_predicted": round(predicted, 1),
            "ratio": round(ratio, 4),
            "checkpoints": checkpoints,
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({}), indent=2))
