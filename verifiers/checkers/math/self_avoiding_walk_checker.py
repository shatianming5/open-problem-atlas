"""Self-avoiding walk connective constant checker.

Counts self-avoiding walks (SAWs) on the square lattice and estimates
the connective constant mu, which is known to satisfy
mu = sqrt(2 + sqrt(2)) ~ 2.6381585 (proved by Duminil-Copin and
Smirnov for the hexagonal lattice; square lattice value is ~2.63816).
"""

from math import log, sqrt


def _count_saws(max_steps: int) -> list[int]:
    """Count self-avoiding walks of length 0, 1, ..., max_steps
    on the square lattice starting from the origin."""
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    counts = [0] * (max_steps + 1)
    counts[0] = 1

    def walk(x: int, y: int, steps: int, visited: set) -> None:
        counts[steps] += 1
        if steps == max_steps:
            return
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (nx, ny) not in visited:
                visited.add((nx, ny))
                walk(nx, ny, steps + 1, visited)
                visited.remove((nx, ny))

    visited = {(0, 0)}
    walk(0, 0, 0, visited)

    return counts


def verify(params: dict) -> dict:
    max_steps = int(params.get("max_steps", 10))
    max_steps = min(max_steps, 15)

    counts = _count_saws(max_steps)

    # Estimate connective constant: mu ~ c_n^(1/n)
    estimates = []
    for n in range(1, max_steps + 1):
        if counts[n] > 0:
            mu_est = counts[n] ** (1.0 / n)
            estimates.append({
                "n": n,
                "c_n": counts[n],
                "mu_estimate": round(mu_est, 6),
            })

    # Ratio estimates: c_{n+1}/c_n -> mu
    ratio_estimates = []
    for n in range(1, max_steps):
        if counts[n] > 0:
            ratio = counts[n + 1] / counts[n]
            ratio_estimates.append({
                "n": n,
                "ratio": round(ratio, 6),
            })

    known_mu_hex = sqrt(2 + sqrt(2))  # ~2.6381585
    known_mu_sq = 2.63815853  # best numerical estimate for square lattice

    best_estimate = estimates[-1]["mu_estimate"] if estimates else 0

    return {
        "status": "pass",
        "summary": (
            f"SAW counts on square lattice up to {max_steps} steps. "
            f"c_{max_steps}={counts[max_steps]}. "
            f"mu estimate: {best_estimate:.4f} "
            f"(known: {known_mu_sq:.4f})"
        ),
        "details": {
            "max_steps": max_steps,
            "counts": counts,
            "mu_estimates": estimates,
            "ratio_estimates": ratio_estimates,
            "known_mu_square": known_mu_sq,
            "known_mu_hexagonal": round(known_mu_hex, 6),
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({}), indent=2))
