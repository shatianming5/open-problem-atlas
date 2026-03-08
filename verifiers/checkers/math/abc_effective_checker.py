"""ABC conjecture effective checker.

The ABC conjecture: for coprime a + b = c, the radical rad(abc) is
usually not much smaller than c. An ABC triple has quality
q = log(c) / log(rad(abc)) > 1. This checker finds high-quality
ABC triples up to max_c.
"""

from math import gcd, log


def _radical(n: int) -> int:
    """Compute the radical of n (product of distinct prime factors)."""
    if n == 0:
        return 0
    rad = 1
    temp = abs(n)
    if temp % 2 == 0:
        rad *= 2
        while temp % 2 == 0:
            temp //= 2
    d = 3
    while d * d <= temp:
        if temp % d == 0:
            rad *= d
            while temp % d == 0:
                temp //= d
        d += 2
    if temp > 1:
        rad *= temp
    return rad


def verify(params: dict) -> dict:
    max_c = int(params.get("max_c", 10000))
    max_c = min(max_c, 100000)

    abc_triples = []
    max_quality = 0.0

    for c in range(3, max_c + 1):
        for a in range(1, c):
            b = c - a
            if b <= a:
                break
            if gcd(a, b) != 1:
                continue
            rad = _radical(a * b * c)
            if rad < c:
                quality = log(c) / log(rad) if rad > 1 else 0
                if quality > 1.0:
                    abc_triples.append({
                        "a": a, "b": b, "c": c,
                        "quality": round(quality, 4),
                    })
                    if quality > max_quality:
                        max_quality = quality

    abc_triples.sort(key=lambda x: -x["quality"])

    return {
        "status": "pass",
        "summary": (
            f"Found {len(abc_triples)} ABC triples with quality > 1 "
            f"up to c={max_c}. Max quality: {max_quality:.4f}"
        ),
        "details": {
            "max_c": max_c,
            "num_triples": len(abc_triples),
            "max_quality": round(max_quality, 4),
            "top_triples": abc_triples[:10],
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({"max_c": 1000}), indent=2))
