"""Singmaster's conjecture checker (extended search).

Singmaster's conjecture: there is a finite upper bound on the number of
times a value > 1 can appear in Pascal's triangle. This variant searches
for values appearing more than 6 times in rows up to max_n.
"""


def verify(params: dict) -> dict:
    max_n = int(params.get("max_n", 500))
    max_n = min(max_n, 1000)

    counts: dict[int, int] = {}
    high_mult = []

    for n in range(max_n + 1):
        val = 1
        for k in range(n // 2 + 1):
            if val > 1:
                copies = 2 if k != n - k else 1
                counts[val] = counts.get(val, 0) + copies
            if k < n:
                val = val * (n - k) // (k + 1)

    max_count = 0
    max_val = 0
    for v, c in counts.items():
        if c > max_count:
            max_count = c
            max_val = v
        if c > 6:
            high_mult.append({"value": v, "count": c})

    high_mult.sort(key=lambda x: -x["count"])

    status = "fail" if high_mult else "pass"
    return {
        "status": status,
        "summary": (
            f"Searched rows 0..{max_n}. Max multiplicity: {max_count} "
            f"(value={max_val}). Values with mult > 6: {len(high_mult)}"
        ),
        "details": {
            "max_n": max_n,
            "max_multiplicity": max_count,
            "max_multiplicity_value": max_val,
            "high_multiplicity": high_mult[:10],
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({}), indent=2))
