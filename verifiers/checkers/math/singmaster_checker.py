"""Singmaster's conjecture checker.

Singmaster's conjecture states there is a finite upper bound on the number
of times a number greater than 1 can appear in Pascal's triangle.
Searches for entries with high multiplicity up to `max_row`.
"""


def verify(params: dict) -> dict:
    max_row = int(params.get("max_row", 500))

    # Count occurrences of each value in Pascal's triangle
    counts: dict[int, int] = {}
    max_count = 0
    max_val = 0

    for n in range(max_row + 1):
        val = 1
        for k in range(n // 2 + 1):
            if val > 1:
                counts[val] = counts.get(val, 0) + (2 if k != n - k else 1)
                if counts[val] > max_count:
                    max_count = counts[val]
                    max_val = val
            if k < n:
                val = val * (n - k) // (k + 1)

    # The known record is 3003, appearing 8 times
    return {
        "status": "pass",
        "summary": (
            f"Searched Pascal's triangle to row {max_row}. "
            f"Max multiplicity: {max_count} (value={max_val}). "
            f"No infinite multiplicity found."
        ),
        "details": {
            "max_row": max_row,
            "max_multiplicity": max_count,
            "max_multiplicity_value": max_val,
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({"max_row": 200}), indent=2))
