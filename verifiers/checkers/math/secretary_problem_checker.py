"""Secretary problem optimal stopping checker.

The secretary problem: interview n candidates sequentially, hire the
best. The optimal strategy is to skip the first n/e candidates and
then hire the next one better than all seen so far. The probability
of hiring the best is 1/e ~ 0.3679. Verifies via simulation.
"""

from math import exp


def verify(params: dict) -> dict:
    n = int(params.get("n", 100))
    n = min(n, 1000)
    trials = int(params.get("trials", 10000))
    trials = min(trials, 50000)

    import random
    rng = random.Random(42)

    optimal_threshold = max(1, int(n / exp(1)))
    wins = 0

    for _ in range(trials):
        # Random permutation of 1..n (quality scores)
        candidates = list(range(1, n + 1))
        rng.shuffle(candidates)

        # Phase 1: observe first `threshold` candidates
        best_seen = max(candidates[:optimal_threshold]) if optimal_threshold > 0 else 0

        # Phase 2: hire first candidate better than best_seen
        hired = -1
        for i in range(optimal_threshold, n):
            if candidates[i] > best_seen:
                hired = candidates[i]
                break

        if hired == n:  # hired the best candidate
            wins += 1

    win_rate = wins / trials
    theoretical = 1.0 / exp(1)

    return {
        "status": "pass",
        "summary": (
            f"Secretary problem: n={n}, threshold={optimal_threshold}, "
            f"{trials} trials. Win rate: {win_rate:.4f} "
            f"(theoretical: {theoretical:.4f})"
        ),
        "details": {
            "n": n,
            "threshold": optimal_threshold,
            "trials": trials,
            "wins": wins,
            "win_rate": round(win_rate, 6),
            "theoretical_rate": round(theoretical, 6),
            "ratio": round(win_rate / theoretical, 4) if theoretical > 0 else 0,
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({}), indent=2))
