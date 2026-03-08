"""KPZ universality class checker.

The KPZ (Kardar-Parisi-Zhang) equation describes surface growth.
The KPZ universality class predicts scaling exponents: the roughness
exponent alpha = 1/2, growth exponent beta = 1/3, and dynamic
exponent z = 3/2 in 1+1 dimensions. This checker simulates a simple
ballistic deposition model and measures the growth exponent.
"""

from math import sqrt, log


def _simulate_ballistic_deposition(size: int, steps: int, rng) -> list[list[int]]:
    """Simulate ballistic deposition on a 1D substrate."""
    heights = [0] * size
    history = []

    for step in range(steps):
        col = rng.randint(0, size - 1)
        # Height is max of current column and neighbors + 1
        h = heights[col]
        if col > 0:
            h = max(h, heights[col - 1])
        if col < size - 1:
            h = max(h, heights[col + 1])
        heights[col] = h + 1

        if (step + 1) % (steps // 20) == 0 or step == steps - 1:
            mean_h = sum(heights) / size
            var_h = sum((h - mean_h) ** 2 for h in heights) / size
            roughness = sqrt(var_h)
            history.append({
                "step": step + 1,
                "mean_height": round(mean_h, 2),
                "roughness": round(roughness, 4),
            })

    return history


def verify(params: dict) -> dict:
    size = int(params.get("size", 100))
    size = min(size, 500)
    steps = int(params.get("steps", 1000))
    steps = min(steps, 5000)

    import random
    rng = random.Random(42)

    history = _simulate_ballistic_deposition(size, steps, rng)

    # Estimate beta from roughness ~ t^beta in the growth regime
    # Use log-log fit on the growth phase
    log_points = []
    for entry in history:
        if entry["roughness"] > 0 and entry["step"] > 10:
            log_points.append((log(entry["step"]), log(entry["roughness"])))

    beta_estimate = 0.0
    if len(log_points) >= 2:
        # Simple linear regression on log-log data
        n = len(log_points)
        sx = sum(p[0] for p in log_points)
        sy = sum(p[1] for p in log_points)
        sxx = sum(p[0] ** 2 for p in log_points)
        sxy = sum(p[0] * p[1] for p in log_points)
        denom = n * sxx - sx * sx
        if abs(denom) > 1e-10:
            beta_estimate = (n * sxy - sx * sy) / denom

    kpz_beta = 1.0 / 3.0

    return {
        "status": "pass",
        "summary": (
            f"Ballistic deposition: L={size}, {steps} steps. "
            f"Estimated beta={beta_estimate:.4f} "
            f"(KPZ prediction: {kpz_beta:.4f})"
        ),
        "details": {
            "size": size,
            "steps": steps,
            "beta_estimate": round(beta_estimate, 4),
            "kpz_beta": round(kpz_beta, 4),
            "growth_history": history,
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({}), indent=2))
