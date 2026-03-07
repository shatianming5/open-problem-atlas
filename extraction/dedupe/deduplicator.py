"""Deduplicate candidate problems using multi-level matching."""

import re
from dataclasses import dataclass

from ingestion.adapters.base import CandidateProblem


@dataclass
class DedupeMatch:
    """Result of a deduplication check."""

    candidate_a: str
    candidate_b: str
    match_level: str  # "exact", "high_confidence_alias", "human_merge"
    similarity: float
    reason: str


def normalize_title(title: str) -> str:
    """Normalize a title for comparison."""
    title = title.lower().strip()
    title = re.sub(r"[''`]s?\b", "", title)  # Remove possessives
    title = re.sub(r"\bthe\b", "", title)
    title = re.sub(r"\bconjecture\b", "", title)
    title = re.sub(r"\bproblem\b", "", title)
    title = re.sub(r"\bhypothesis\b", "", title)
    title = re.sub(r"[^a-z0-9\s]", "", title)
    title = re.sub(r"\s+", " ", title).strip()
    return title


def exact_match(a: str, b: str) -> bool:
    """Check for exact title match after normalization."""
    return normalize_title(a) == normalize_title(b)


def token_overlap(a: str, b: str) -> float:
    """Compute Jaccard similarity between token sets."""
    tokens_a = set(normalize_title(a).split())
    tokens_b = set(normalize_title(b).split())
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b
    return len(intersection) / len(union)


def find_duplicates(
    candidates: list[CandidateProblem],
    existing_titles: list[str] | None = None,
    threshold: float = 0.6,
) -> tuple[list[CandidateProblem], list[DedupeMatch]]:
    """Find and flag duplicate candidates.

    Returns:
        - deduplicated list (exact duplicates removed)
        - list of potential matches for human review
    """
    existing_titles = existing_titles or []
    matches = []
    unique = []
    seen_normalized = {}

    # Index existing titles
    for title in existing_titles:
        norm = normalize_title(title)
        seen_normalized[norm] = title

    for candidate in candidates:
        norm = normalize_title(candidate.title)

        # Level 1: Exact match
        if norm in seen_normalized:
            matches.append(DedupeMatch(
                candidate_a=candidate.title,
                candidate_b=seen_normalized[norm],
                match_level="exact",
                similarity=1.0,
                reason="Identical normalized title",
            ))
            continue

        # Level 2: High-confidence alias (token overlap > threshold)
        best_overlap = 0.0
        best_match = ""
        for existing_norm, existing_title in seen_normalized.items():
            overlap = token_overlap(candidate.title, existing_title)
            if overlap > best_overlap:
                best_overlap = overlap
                best_match = existing_title

        if best_overlap >= threshold:
            matches.append(DedupeMatch(
                candidate_a=candidate.title,
                candidate_b=best_match,
                match_level="high_confidence_alias" if best_overlap >= 0.8 else "human_merge",
                similarity=best_overlap,
                reason=f"Token overlap: {best_overlap:.2f}",
            ))
            if best_overlap >= 0.8:
                continue  # Skip high-confidence duplicates

        seen_normalized[norm] = candidate.title
        unique.append(candidate)

    return unique, matches
