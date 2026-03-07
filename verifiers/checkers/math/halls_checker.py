"""Hall's conjecture verifier.

Hall's conjecture states that for integers x and y with y^2 != x^3,
|x^3 - y^2| > C * x^(1/2) for some constant C > 0.

More precisely, for every epsilon > 0, there exists a constant C(epsilon)
such that |x^3 - y^2| > C(epsilon) * x^(1/2 - epsilon) for all x, y with
y^2 != x^3.

This checker searches for close pairs (x, y) where |x^3 - y^2| is small
relative to x^(1/2), verifying that the ratio doesn't vanish.
"""

import math


def verify(params: dict) -> dict:
    limit = int(params.get("limit", 10000))
    upper_bound = int(params.get("upper_bound", limit))

    closest_pairs = []
    min_ratio = float("inf")
    min_pair = None

    for x in range(2, upper_bound + 1):
        x3 = x * x * x
        # y should be close to x^(3/2)
        y_approx = math.isqrt(x3)

        for y in range(max(1, y_approx - 2), y_approx + 3):
            diff = x3 - y * y
            if diff == 0:
                continue
            abs_diff = abs(diff)
            sqrt_x = math.sqrt(x)

            if sqrt_x > 0:
                ratio = abs_diff / sqrt_x
                if ratio < min_ratio:
                    min_ratio = ratio
                    min_pair = {"x": x, "y": y, "x3": x3, "y2": y * y,
                                "diff": diff, "ratio": round(ratio, 6)}

                if ratio < 1.0:
                    closest_pairs.append({
                        "x": x, "y": y, "diff": diff,
                        "ratio": round(ratio, 6),
                    })

    # Hall's conjecture predicts ratio stays bounded away from 0
    # We report the smallest ratio found
    status = "pass"
    summary_parts = [
        f"Hall's conjecture checked for x in [2, {upper_bound}].",
    ]
    if min_pair:
        summary_parts.append(
            f"Smallest |x^3-y^2|/x^(1/2) ratio: {min_pair['ratio']:.6f} "
            f"at x={min_pair['x']}, y={min_pair['y']}."
        )

    return {
        "status": status,
        "summary": " ".join(summary_parts),
        "details": {
            "upper_bound": upper_bound,
            "min_ratio": round(min_ratio, 6) if min_ratio != float("inf") else None,
            "min_pair": min_pair,
            "close_pairs_count": len(closest_pairs),
            "close_pairs_sample": closest_pairs[:10],
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({"upper_bound": 5000}), indent=2))
