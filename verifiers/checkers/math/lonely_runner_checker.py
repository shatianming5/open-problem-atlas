"""Lonely runner conjecture verifier.

The lonely runner conjecture states: if k runners with distinct speeds
run on a circular track of unit circumference starting from the same
point, then each runner is at some time "lonely" (at distance >= 1/(k+1)
from all other runners).

More precisely, for k+1 runners with pairwise distinct speeds
v_0, v_1, ..., v_k on a unit circle, for each runner i, there exists
a time t such that ||(v_i - v_j)*t|| >= 1/(k+1) for all j != i,
where ||x|| denotes the distance from x to the nearest integer.

WLOG we can fix v_0 = 0 and consider k runners with speeds v_1, ..., v_k.
"""

import math
from itertools import combinations


def _fractional_distance(x: float) -> float:
    """Distance from x to the nearest integer: ||x|| = min(x - floor(x), ceil(x) - x)."""
    f = x - math.floor(x)
    return min(f, 1.0 - f)


def _check_lonely(speeds: list, runner_idx: int, num_steps: int = 10000) -> bool:
    """Check if runner at runner_idx is lonely at some time.

    We check many rational times t = j/N for various N.
    """
    k = len(speeds)  # total number of runners (including runner 0 with speed 0)
    threshold = 1.0 / (k + 1) - 1e-10  # slight tolerance

    # WLOG speed 0 is 0 (we've already subtracted)
    for N in range(1, num_steps + 1):
        for j in range(N):
            t = j / N
            lonely = True
            for i in range(len(speeds)):
                if i == runner_idx:
                    continue
                dist = _fractional_distance((speeds[runner_idx] - speeds[i]) * t)
                if dist < threshold:
                    lonely = False
                    break
            if lonely:
                return True

    return False


def verify(params: dict) -> dict:
    n_runners = int(params.get("n_runners", 4))
    n_runners = min(n_runners, 6)  # Cap for performance

    # Test with various speed sets
    # WLOG one runner has speed 0; we test runners with speeds {1, 2, ..., n_runners-1}
    # and other configurations

    test_configs = []

    # Standard configuration: speeds 0, 1, 2, ..., k
    for k in range(2, n_runners + 1):
        test_configs.append(list(range(k)))

    # Some other interesting configurations
    if n_runners >= 3:
        test_configs.append([0, 1, 3])
    if n_runners >= 4:
        test_configs.append([0, 1, 3, 7])
        test_configs.append([0, 1, 2, 5])
    if n_runners >= 5:
        test_configs.append([0, 1, 3, 5, 7])

    total_checked = 0
    violations = []
    results = []

    for speeds in test_configs:
        k = len(speeds)
        all_lonely = True
        config_details = {"speeds": speeds, "runners": []}

        for runner in range(k):
            lonely = _check_lonely(speeds, runner, num_steps=1000)
            config_details["runners"].append({
                "index": runner,
                "speed": speeds[runner],
                "is_lonely": lonely,
            })
            if not lonely:
                all_lonely = False

        total_checked += 1
        config_details["all_lonely"] = all_lonely

        if not all_lonely:
            violations.append(config_details)

        results.append(config_details)

    if violations:
        return {
            "status": "fail",
            "summary": (
                f"Lonely runner conjecture violated for "
                f"{len(violations)} speed configuration(s)"
            ),
            "details": {
                "n_runners": n_runners,
                "total_checked": total_checked,
                "violations": violations,
            },
        }

    return {
        "status": "pass",
        "summary": (
            f"Lonely runner conjecture verified for {total_checked} speed "
            f"configurations with up to {n_runners} runners."
        ),
        "details": {
            "n_runners": n_runners,
            "total_checked": total_checked,
            "results": results,
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({"n_runners": 4}), indent=2))
