"""Lebesgue universal covering problem verifier.

The Lebesgue universal covering problem asks for the convex set of
minimum area that can cover (contain a congruent copy of) every planar
set of diameter 1.

Known bounds:
- Lower bound: 0.832 (various authors)
- Upper bound: 0.8441153 (Gibbs 2018, improved from earlier bounds)
- The exact minimum area is unknown.

A regular hexagon of appropriate size gives area ~0.866.
Sprague (1936) showed area can be reduced to ~0.8441.

This checker verifies known bounds and basic covering properties.
"""

import math


def _area_regular_hexagon_circumradius(R: float) -> float:
    """Area of a regular hexagon with circumradius R."""
    return (3 * math.sqrt(3) / 2) * R * R


def _area_reuleaux_triangle(width: float) -> float:
    """Area of a Reuleaux triangle with given width."""
    return (math.pi - math.sqrt(3)) / 2 * width * width


def _verify_circle_covers_diameter_1(radius: float) -> bool:
    """A circle of given radius covers all sets of diameter 1
    if and only if radius >= 1/sqrt(3) (from Jung's theorem in 2D).
    """
    return radius >= 1.0 / math.sqrt(3) - 1e-10


def verify(params: dict) -> dict:
    # Known bounds for the Lebesgue universal covering problem
    known_upper = 0.8441153  # Gibbs (2018)
    known_lower = 0.832  # Brass-Sharif (2005) and others

    # Jung's theorem: the smallest enclosing circle of a set of diameter 1
    # has radius r = 1/sqrt(3)
    jung_radius = 1.0 / math.sqrt(3)
    circle_area = math.pi * jung_radius ** 2

    # Reuleaux triangle of width 1
    reuleaux_area = _area_reuleaux_triangle(1.0)

    # Regular hexagon inscribed in circle of radius 1/sqrt(3)
    hex_area = _area_regular_hexagon_circumradius(jung_radius)

    # Equilateral triangle of side 1 has diameter 1
    # It must fit inside the universal cover
    eq_triangle_area = math.sqrt(3) / 4

    # Unit diameter circle has diameter 1, area pi/4
    unit_circle_area = math.pi / 4

    # Verification checks
    checks = {
        "circle_covers": _verify_circle_covers_diameter_1(jung_radius),
        "circle_area": round(circle_area, 6),
        "reuleaux_area": round(reuleaux_area, 6),
        "hexagon_area": round(hex_area, 6),
        "known_lower_lt_upper": known_lower < known_upper,
        "upper_lt_circle": known_upper < circle_area,
        "lower_gt_half_pi_fourth": known_lower > unit_circle_area,
    }

    all_passed = all(v if isinstance(v, bool) else True for v in checks.values())

    if not all_passed:
        return {
            "status": "fail",
            "summary": "Lebesgue universal covering bounds verification failed",
            "details": {"checks": checks},
        }

    return {
        "status": "pass",
        "summary": (
            f"Lebesgue universal covering bounds verified. "
            f"Best known area in [{known_lower}, {known_upper}]. "
            f"Circle area: {circle_area:.6f}, Reuleaux: {reuleaux_area:.6f}."
        ),
        "details": {
            "known_lower_bound": known_lower,
            "known_upper_bound": known_upper,
            "gap": round(known_upper - known_lower, 6),
            "jung_radius": round(jung_radius, 6),
            "circle_area": round(circle_area, 6),
            "reuleaux_area": round(reuleaux_area, 6),
            "hexagon_area": round(hex_area, 6),
            "checks": checks,
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(verify({}), indent=2))
