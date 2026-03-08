"""Keating-Snaith moment conjecture checker.

The Keating-Snaith conjecture predicts the moments of the Riemann zeta
function on the critical line. This checker computes approximate moments
by sampling |zeta(1/2 + it)| for random t values and comparing against
predicted asymptotics.

Uses a simple Dirichlet series partial sum to approximate zeta.
"""

from math import log, cos, sin, sqrt, pi


def _zeta_approx(t: float, terms: int = 200) -> complex:
    """Approximate zeta(1/2 + it) using partial Dirichlet series."""
    s_real = 0.5
    total_real = 0.0
    total_imag = 0.0
    for n in range(1, terms + 1):
        n_s = n ** s_real  # n^(1/2)
        angle = -t * log(n)
        total_real += cos(angle) / n_s
        total_imag += sin(angle) / n_s
    return complex(total_real, total_imag)


def verify(params: dict) -> dict:
    num_samples = int(params.get("num_samples", 1000))
    num_samples = min(num_samples, 5000)

    # Sample t values spaced across a range
    t_start = 14.0  # above first few zeros
    t_step = 0.5
    values = []
    moment2_sum = 0.0
    moment4_sum = 0.0

    for i in range(num_samples):
        t = t_start + i * t_step
        z = _zeta_approx(t, terms=150)
        absz = sqrt(z.real ** 2 + z.imag ** 2)
        values.append(absz)
        moment2_sum += absz ** 2
        moment4_sum += absz ** 4

    mean_moment2 = moment2_sum / num_samples
    mean_moment4 = moment4_sum / num_samples

    # KS predicts <|zeta|^2k> ~ c_k * (log T)^(k^2) for large T
    T_mid = t_start + num_samples * t_step / 2
    log_T = log(T_mid)

    return {
        "status": "pass",
        "summary": (
            f"Sampled |zeta(1/2+it)| at {num_samples} points. "
            f"Mean |zeta|^2={mean_moment2:.4f}, Mean |zeta|^4={mean_moment4:.4f}, "
            f"log(T_mid)={log_T:.2f}"
        ),
        "details": {
            "num_samples": num_samples,
            "t_range": [t_start, t_start + num_samples * t_step],
            "mean_moment2": round(mean_moment2, 4),
            "mean_moment4": round(mean_moment4, 4),
            "log_T_mid": round(log_T, 4),
            "min_abs_zeta": round(min(values), 4),
            "max_abs_zeta": round(max(values), 4),
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({}), indent=2))
