"""Link candidate problem titles to known problems via alias matching."""

import re
from dataclasses import dataclass

from extraction.dedupe.deduplicator import normalize_title, token_overlap


@dataclass
class AliasMatch:
    """Result of an alias-linking lookup."""

    canonical_id: str
    confidence: float
    match_type: str  # "exact_alias", "fuzzy", "person_name"


# ---------------------------------------------------------------------------
# Known alias table
#
# Maps canonical problem ID -> set of known alternative names.
# This table covers common mathematical / CS open problems and their
# widely-used alternative titles.
# ---------------------------------------------------------------------------

KNOWN_ALIASES: dict[str, list[str]] = {
    "opa.mathematics.number-theory.collatz-conjecture": [
        "Collatz Conjecture",
        "3x+1 Problem",
        "Syracuse Problem",
        "Kakutani's Problem",
        "Ulam's Conjecture",
        "Hasse's Algorithm",
    ],
    "opa.mathematics.number-theory.goldbach-conjecture": [
        "Goldbach's Conjecture",
        "Goldbach's Strong Conjecture",
        "Binary Goldbach Conjecture",
    ],
    "opa.mathematics.number-theory.twin-prime-conjecture": [
        "Twin Prime Conjecture",
        "Twin Primes Problem",
    ],
    "opa.mathematics.number-theory.riemann-hypothesis": [
        "Riemann Hypothesis",
        "Riemann Zeta Hypothesis",
        "RH",
    ],
    "opa.mathematics.number-theory.birch-swinnerton-dyer-conjecture": [
        "Birch and Swinnerton-Dyer Conjecture",
        "BSD Conjecture",
    ],
    "opa.mathematics.combinatorics.union-closed-sets-conjecture": [
        "Union-Closed Sets Conjecture",
        "Frankl's Conjecture",
        "Frankl's Union-Closed Conjecture",
    ],
    "opa.mathematics.graph-theory.hadwiger-conjecture": [
        "Hadwiger's Conjecture",
        "Hadwiger Conjecture",
    ],
    "opa.mathematics.graph-theory.reconstruction-conjecture": [
        "Reconstruction Conjecture",
        "Kelly-Ulam Conjecture",
    ],
    "opa.mathematics.graph-theory.graceful-tree-conjecture": [
        "Graceful Tree Conjecture",
        "Ringel-Kotzig Conjecture",
        "Graceful Labeling Conjecture",
    ],
    "opa.mathematics.pde.navier-stokes-existence-and-smoothness": [
        "Navier-Stokes Existence and Smoothness",
        "Navier-Stokes Problem",
        "Navier-Stokes Regularity",
    ],
    "opa.theoretical-cs.complexity-theory.p-vs-np": [
        "P vs NP",
        "P versus NP",
        "P = NP",
        "P != NP",
        "Cook's Problem",
    ],
    "opa.theoretical-cs.complexity-theory.unique-games-conjecture": [
        "Unique Games Conjecture",
        "UGC",
        "Khot's Conjecture",
    ],
    "opa.mathematical-physics.quantum-gravity.yang-mills-existence-and-mass-gap": [
        "Yang-Mills Existence and Mass Gap",
        "Yang-Mills Problem",
        "Yang-Mills Mass Gap",
    ],
}

# ---------------------------------------------------------------------------
# Person-name extraction for person-name matching
# ---------------------------------------------------------------------------

# Common person names associated with famous problems (surname only).
_PERSON_PROBLEM_MAP: dict[str, str] = {
    "collatz": "opa.mathematics.number-theory.collatz-conjecture",
    "goldbach": "opa.mathematics.number-theory.goldbach-conjecture",
    "riemann": "opa.mathematics.number-theory.riemann-hypothesis",
    "birch": "opa.mathematics.number-theory.birch-swinnerton-dyer-conjecture",
    "swinnerton-dyer": "opa.mathematics.number-theory.birch-swinnerton-dyer-conjecture",
    "frankl": "opa.mathematics.combinatorics.union-closed-sets-conjecture",
    "hadwiger": "opa.mathematics.graph-theory.hadwiger-conjecture",
    "navier": "opa.mathematics.pde.navier-stokes-existence-and-smoothness",
    "stokes": "opa.mathematics.pde.navier-stokes-existence-and-smoothness",
    "cook": "opa.theoretical-cs.complexity-theory.p-vs-np",
    "khot": "opa.theoretical-cs.complexity-theory.unique-games-conjecture",
    "yang": "opa.mathematical-physics.quantum-gravity.yang-mills-existence-and-mass-gap",
    "mills": "opa.mathematical-physics.quantum-gravity.yang-mills-existence-and-mass-gap",
    "hadamard": "opa.mathematics.combinatorics.hadamard-conjecture",
    "jacobi": "opa.mathematics.algebra.jacobian-conjecture",
    "kakeya": "opa.mathematics.analysis.kakeya-conjecture",
    "vaught": "opa.mathematics.logic.vaughts-conjecture",
}


# ---------------------------------------------------------------------------
# Build inverted index: normalized alias -> canonical id
# ---------------------------------------------------------------------------

def _build_alias_index() -> dict[str, str]:
    """Create a dict mapping normalized alias -> canonical problem ID."""
    index: dict[str, str] = {}
    for canonical_id, aliases in KNOWN_ALIASES.items():
        for alias in aliases:
            index[normalize_title(alias)] = canonical_id
    return index


_ALIAS_INDEX = _build_alias_index()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def link_aliases(
    candidate_title: str,
    known_problems: dict[str, list[str]] | None = None,
    *,
    fuzzy_threshold: float = 0.65,
) -> AliasMatch | None:
    """Try to link *candidate_title* to a known problem via aliases.

    Matching strategies (tried in order):
    1. **Exact alias** -- normalized title appears in the alias table.
    2. **Fuzzy** -- token-overlap Jaccard similarity >= *fuzzy_threshold*.
    3. **Person name** -- a known mathematician surname appears in the title.

    Parameters
    ----------
    candidate_title:
        The title of the candidate problem to look up.
    known_problems:
        Optional additional mapping ``{canonical_id: [alias, ...]}`` that
        supplements the built-in ``KNOWN_ALIASES`` table.
    fuzzy_threshold:
        Minimum Jaccard token-overlap to accept a fuzzy match.

    Returns
    -------
    AliasMatch | None
        The best match found, or ``None`` if no match exceeds thresholds.
    """
    # Merge caller-provided aliases into a local index copy.
    alias_index = dict(_ALIAS_INDEX)
    if known_problems:
        for cid, aliases in known_problems.items():
            for alias in aliases:
                alias_index[normalize_title(alias)] = cid

    norm = normalize_title(candidate_title)

    # Strategy 1: Exact alias match
    if norm in alias_index:
        return AliasMatch(
            canonical_id=alias_index[norm],
            confidence=1.0,
            match_type="exact_alias",
        )

    # Strategy 2: Fuzzy token-overlap
    best_score = 0.0
    best_id = ""
    for alias_norm, cid in alias_index.items():
        score = token_overlap(candidate_title, alias_norm)
        if score > best_score:
            best_score = score
            best_id = cid

    if best_score >= fuzzy_threshold and best_id:
        return AliasMatch(
            canonical_id=best_id,
            confidence=round(best_score, 3),
            match_type="fuzzy",
        )

    # Strategy 3: Person-name matching
    title_lower = candidate_title.lower()
    for person, cid in _PERSON_PROBLEM_MAP.items():
        if person in title_lower:
            return AliasMatch(
                canonical_id=cid,
                confidence=0.55,
                match_type="person_name",
            )

    return None
