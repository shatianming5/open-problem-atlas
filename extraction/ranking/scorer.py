"""Score candidates for prioritization in the review queue."""

import re
from dataclasses import dataclass

from ingestion.adapters.base import CandidateProblem


@dataclass
class ScoredCandidate:
    """A candidate with computed priority scores."""

    candidate: CandidateProblem
    priority_score: float
    impact_estimate: float
    formality_estimate: float
    toolability_estimate: float
    reasoning: str


# Keywords indicating high-impact problems
HIGH_IMPACT_KEYWORDS = [
    "millennium", "prize", "clay", "fields medal", "fundamental",
    "central", "major", "famous", "well-known", "long-standing",
]

# Keywords indicating formalizable problems
FORMALITY_KEYWORDS = [
    "prove that", "show that", "determine whether", "is it true",
    "for all", "there exists", "if and only if", "conjecture",
    "theorem", "lemma", "proposition",
]

# Keywords indicating tool-amenable problems
TOOLABILITY_KEYWORDS = [
    "compute", "algorithm", "polynomial", "complexity",
    "counterexample", "search", "verify", "enumerate",
    "bound", "inequality", "finite", "integer",
]


def _keyword_score(text: str, keywords: list[str]) -> float:
    """Compute a score based on keyword presence."""
    text_lower = text.lower()
    hits = sum(1 for kw in keywords if kw in text_lower)
    return min(hits / max(len(keywords) * 0.3, 1), 1.0)


def score_candidate(candidate: CandidateProblem) -> ScoredCandidate:
    """Score a candidate for review prioritization."""
    text = f"{candidate.title} {candidate.statement}"

    impact = _keyword_score(text, HIGH_IMPACT_KEYWORDS)
    formality = _keyword_score(text, FORMALITY_KEYWORDS)
    toolability = _keyword_score(text, TOOLABILITY_KEYWORDS)

    # Boost if from high-tier source
    source_boost = 0.2 if candidate.confidence > 0.5 else 0.0

    # Penalize very short or vague statements
    length_factor = min(len(candidate.statement) / 200, 1.0) if candidate.statement else 0.0

    priority = (
        impact * 0.3
        + formality * 0.25
        + toolability * 0.2
        + candidate.confidence * 0.15
        + length_factor * 0.1
        + source_boost
    )
    priority = min(priority, 1.0)

    reasoning_parts = []
    if impact > 0.3:
        reasoning_parts.append(f"high-impact keywords ({impact:.2f})")
    if formality > 0.3:
        reasoning_parts.append(f"formal statement ({formality:.2f})")
    if toolability > 0.3:
        reasoning_parts.append(f"tool-amenable ({toolability:.2f})")

    return ScoredCandidate(
        candidate=candidate,
        priority_score=priority,
        impact_estimate=impact,
        formality_estimate=formality,
        toolability_estimate=toolability,
        reasoning="; ".join(reasoning_parts) or "low signal",
    )


def rank_candidates(candidates: list[CandidateProblem]) -> list[ScoredCandidate]:
    """Score and rank candidates by priority."""
    scored = [score_candidate(c) for c in candidates]
    scored.sort(key=lambda s: s.priority_score, reverse=True)
    return scored
