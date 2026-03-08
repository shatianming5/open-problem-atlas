"""Euler brick and perfect cuboid checker.

An Euler brick has integer edges a, b, c with integer face diagonals.
A perfect cuboid would also have an integer space diagonal. No perfect
cuboid is known to exist. This checker searches for Euler bricks and
checks if any is a perfect cuboid.
"""

from math import isqrt


def _is_perfect_square(n: int) -> bool:
    if n < 0:
        return False
    s = isqrt(n)
    return s * s == n


def verify(params: dict) -> dict:
    max_n = int(params.get("max_n", 1000))
    max_n = min(max_n, 5000)

    euler_bricks = []
    perfect_cuboids = []

    for a in range(1, max_n + 1):
        for b in range(a, max_n + 1):
            ab2 = a * a + b * b
            if not _is_perfect_square(ab2):
                continue
            for c in range(b, max_n + 1):
                ac2 = a * a + c * c
                bc2 = b * b + c * c
                if _is_perfect_square(ac2) and _is_perfect_square(bc2):
                    euler_bricks.append({
                        "a": a, "b": b, "c": c,
                        "face_diag_ab": isqrt(ab2),
                        "face_diag_ac": isqrt(ac2),
                        "face_diag_bc": isqrt(bc2),
                    })
                    # Check space diagonal
                    space2 = a * a + b * b + c * c
                    if _is_perfect_square(space2):
                        perfect_cuboids.append({
                            "a": a, "b": b, "c": c,
                            "space_diag": isqrt(space2),
                        })

                    if len(euler_bricks) >= 20:
                        break
            if len(euler_bricks) >= 20:
                break
        if len(euler_bricks) >= 20:
            break

    return {
        "status": "pass",
        "summary": (
            f"Found {len(euler_bricks)} Euler bricks up to {max_n}. "
            f"Perfect cuboids found: {len(perfect_cuboids)} "
            f"(none expected)"
        ),
        "details": {
            "max_n": max_n,
            "euler_bricks": euler_bricks[:10],
            "perfect_cuboids": perfect_cuboids,
            "perfect_cuboid_exists": len(perfect_cuboids) > 0,
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({"max_n": 500}), indent=2))
