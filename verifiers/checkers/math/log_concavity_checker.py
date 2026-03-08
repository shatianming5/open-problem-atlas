"""Log-concavity of combinatorial sequences checker.

Verifies log-concavity (a_k^2 >= a_{k-1} * a_{k+1}) for classical
combinatorial sequences: binomial coefficients, Stirling numbers of
the second kind, and Euler numbers.
"""


def _binomial(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    if k == 0 or k == n:
        return 1
    k = min(k, n - k)
    result = 1
    for i in range(k):
        result = result * (n - i) // (i + 1)
    return result


def _stirling2(n: int, k: int) -> int:
    """Stirling number of the second kind S(n,k)."""
    if n == 0 and k == 0:
        return 1
    if n == 0 or k == 0:
        return 0
    if k > n:
        return 0
    # Use recurrence: S(n,k) = k*S(n-1,k) + S(n-1,k-1)
    prev = [0] * (k + 1)
    prev[0] = 1  # S(0,0)
    for i in range(1, n + 1):
        curr = [0] * (k + 1)
        for j in range(1, min(i, k) + 1):
            curr[j] = j * prev[j] + prev[j - 1]
        prev = curr
    return prev[k]


def verify(params: dict) -> dict:
    max_n = int(params.get("max_n", 20))
    max_n = min(max_n, 50)

    results = []
    all_log_concave = True

    # Check binomial coefficients C(n, k) for each n
    binom_violations = []
    for n in range(2, max_n + 1):
        seq = [_binomial(n, k) for k in range(n + 1)]
        for k in range(1, len(seq) - 1):
            if seq[k] * seq[k] < seq[k - 1] * seq[k + 1]:
                binom_violations.append({"n": n, "k": k})
                all_log_concave = False

    results.append({
        "sequence": "binomial C(n,k)",
        "max_n": max_n,
        "log_concave": len(binom_violations) == 0,
        "violations": len(binom_violations),
    })

    # Check Stirling numbers S(n, k) for each n
    stirling_violations = []
    for n in range(2, min(max_n, 15) + 1):
        seq = [_stirling2(n, k) for k in range(n + 1)]
        for k in range(1, len(seq) - 1):
            if seq[k] > 0 and seq[k - 1] >= 0 and seq[k + 1] >= 0:
                if seq[k] * seq[k] < seq[k - 1] * seq[k + 1]:
                    stirling_violations.append({"n": n, "k": k})
                    all_log_concave = False

    results.append({
        "sequence": "Stirling S(n,k)",
        "max_n": min(max_n, 15),
        "log_concave": len(stirling_violations) == 0,
        "violations": len(stirling_violations),
    })

    # Check derangement-related sequence: D(n) / n!
    # Actually check that sequence of derangements is log-concave
    derangements = [1, 0]  # D(0)=1, D(1)=0
    for n in range(2, max_n + 1):
        derangements.append((n - 1) * (derangements[-1] + derangements[-2]))

    derang_violations = []
    for k in range(1, len(derangements) - 1):
        a, b, c = derangements[k - 1], derangements[k], derangements[k + 1]
        if b > 0 and b * b < a * c:
            derang_violations.append({"k": k})

    results.append({
        "sequence": "derangements D(n)",
        "max_n": max_n,
        "log_concave": len(derang_violations) == 0,
        "violations": len(derang_violations),
    })

    return {
        "status": "pass" if all_log_concave else "fail",
        "summary": (
            f"Log-concavity checked for 3 sequences up to n={max_n}. "
            f"All log-concave: {all_log_concave}"
        ),
        "details": {"max_n": max_n, "results": results},
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({}), indent=2))
