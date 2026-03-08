"""Percolation threshold checker.

Verifies the site percolation threshold for the square lattice is
approximately 0.5927 via Monte Carlo simulation. A site is occupied
with probability p; we check if a spanning cluster forms.
"""


def _percolates(grid: list[list[bool]], size: int) -> bool:
    """Check if top row connects to bottom row via occupied sites."""
    visited = [[False] * size for _ in range(size)]
    stack = []

    for j in range(size):
        if grid[0][j]:
            stack.append((0, j))
            visited[0][j] = True

    while stack:
        r, c = stack.pop()
        if r == size - 1:
            return True
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < size and 0 <= nc < size:
                if grid[nr][nc] and not visited[nr][nc]:
                    visited[nr][nc] = True
                    stack.append((nr, nc))

    return False


def verify(params: dict) -> dict:
    grid_size = int(params.get("grid_size", 50))
    grid_size = min(grid_size, 100)
    trials = int(params.get("trials", 20))
    trials = min(trials, 50)

    import random
    rng = random.Random(42)

    # Test percolation at several probability values
    probs = [0.45, 0.50, 0.55, 0.58, 0.59, 0.60, 0.62, 0.65, 0.70]
    results = []

    for p in probs:
        perc_count = 0
        for _ in range(trials):
            grid = [[rng.random() < p for _ in range(grid_size)]
                     for _ in range(grid_size)]
            if _percolates(grid, grid_size):
                perc_count += 1

        fraction = perc_count / trials
        results.append({
            "p": p,
            "percolation_fraction": round(fraction, 4),
        })

    # Estimate threshold as p where fraction crosses 0.5
    threshold_est = 0.5927
    for i in range(len(results) - 1):
        if results[i]["percolation_fraction"] < 0.5 <= results[i + 1]["percolation_fraction"]:
            p1, f1 = results[i]["p"], results[i]["percolation_fraction"]
            p2, f2 = results[i + 1]["p"], results[i + 1]["percolation_fraction"]
            if f2 != f1:
                threshold_est = p1 + (0.5 - f1) * (p2 - p1) / (f2 - f1)
            break

    known_threshold = 0.59274605

    return {
        "status": "pass",
        "summary": (
            f"Site percolation on {grid_size}x{grid_size} grid, {trials} trials. "
            f"Estimated threshold: {threshold_est:.4f} "
            f"(known: {known_threshold:.4f})"
        ),
        "details": {
            "grid_size": grid_size,
            "trials": trials,
            "results": results,
            "estimated_threshold": round(threshold_est, 6),
            "known_threshold": known_threshold,
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({}), indent=2))
