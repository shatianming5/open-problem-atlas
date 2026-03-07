"""Extract candidate open problems from text using regex-based rules (no LLM API)."""

import re
from dataclasses import dataclass, field

from ingestion.adapters.base import CandidateProblem


# ---------------------------------------------------------------------------
# Pattern definitions
# ---------------------------------------------------------------------------

@dataclass
class _PatternSpec:
    """Internal specification for a regex-based extraction rule."""

    pattern: re.Pattern
    label: str
    base_confidence: float
    # Group index inside the regex that captures the problem statement text.
    # 0 means the whole match.
    capture_group: int = 0


# Each spec tries to grab the statement that follows the trigger phrase.
# We capture up to the next sentence-ending punctuation or paragraph break.
_SENTENCE_TAIL = r"(.+?(?:\.\s|\.\Z|\n))"

_PATTERN_SPECS: list[_PatternSpec] = [
    # "Conjecture X.Y: <statement>"
    _PatternSpec(
        pattern=re.compile(
            r"(?i)(Conjecture\s+[\d]+(?:\.[\d]+)?\s*[:.]?\s*)" + _SENTENCE_TAIL,
            re.DOTALL,
        ),
        label="conjecture_numbered",
        base_confidence=0.80,
        capture_group=0,
    ),
    # "Open Problem: <statement>"
    _PatternSpec(
        pattern=re.compile(
            r"(?i)(Open\s+Problem\s*[:.]?\s*)" + _SENTENCE_TAIL,
            re.DOTALL,
        ),
        label="open_problem_label",
        base_confidence=0.85,
        capture_group=0,
    ),
    # "Question: Is it true that <statement>"
    _PatternSpec(
        pattern=re.compile(
            r"(?i)(Question\s*[:.]?\s*Is\s+it\s+true\s+that\s+)" + _SENTENCE_TAIL,
            re.DOTALL,
        ),
        label="question_is_it_true",
        base_confidence=0.75,
        capture_group=0,
    ),
    # "It remains open whether <statement>"
    _PatternSpec(
        pattern=re.compile(
            r"(?i)(It\s+remains\s+open\s+whether\s+)" + _SENTENCE_TAIL,
            re.DOTALL,
        ),
        label="remains_open_whether",
        base_confidence=0.70,
        capture_group=0,
    ),
    # "We conjecture that <statement>"
    _PatternSpec(
        pattern=re.compile(
            r"(?i)(We\s+conjecture\s+that\s+)" + _SENTENCE_TAIL,
            re.DOTALL,
        ),
        label="we_conjecture_that",
        base_confidence=0.75,
        capture_group=0,
    ),
]


# ---------------------------------------------------------------------------
# Title heuristic
# ---------------------------------------------------------------------------

def _derive_title(matched_text: str, label: str, index: int) -> str:
    """Derive a short title from matched text and pattern label.

    Falls back to a generic numbered title when nothing better can be inferred.
    """
    # For numbered conjectures, use the number part as part of the title.
    num_match = re.match(r"(?i)Conjecture\s+([\d]+(?:\.[\d]+)?)", matched_text)
    if num_match:
        return f"Conjecture {num_match.group(1)}"

    # Truncate the statement to a short title (first 60 chars).
    # Strip the trigger prefix first.
    statement_only = re.sub(
        r"(?i)^(open\s+problem|question|we\s+conjecture\s+that|it\s+remains\s+open\s+whether)\s*[:.]?\s*",
        "",
        matched_text,
    ).strip()
    if len(statement_only) > 60:
        statement_only = statement_only[:57] + "..."
    if statement_only:
        return statement_only

    return f"Candidate {label}_{index}"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_from_text(
    text: str,
    source_id: str,
    *,
    domain_hint: str = "",
    subdomain_hint: str = "",
) -> list[CandidateProblem]:
    """Scan *text* for candidate open problems using regex rules.

    Parameters
    ----------
    text:
        The full text of a paper section, survey paragraph, etc.
    source_id:
        Identifier of the source document (used in the returned candidates).
    domain_hint:
        Optional domain hint forwarded to each ``CandidateProblem``.
    subdomain_hint:
        Optional subdomain hint forwarded to each ``CandidateProblem``.

    Returns
    -------
    list[CandidateProblem]
        A (possibly empty) list of candidates found in *text*.
    """
    candidates: list[CandidateProblem] = []
    seen_spans: list[tuple[int, int]] = []  # avoid overlapping matches

    for spec in _PATTERN_SPECS:
        for match in spec.pattern.finditer(text):
            start, end = match.span(spec.capture_group)

            # Skip if this span overlaps with an already-captured one.
            if any(s <= start < e or s < end <= e for s, e in seen_spans):
                continue
            seen_spans.append((start, end))

            raw = match.group(spec.capture_group).strip()
            title = _derive_title(raw, spec.label, len(candidates) + 1)

            candidates.append(
                CandidateProblem(
                    title=title,
                    statement=raw,
                    source_id=source_id,
                    source_locator=f"char {start}-{end}",
                    domain_hint=domain_hint,
                    subdomain_hint=subdomain_hint,
                    problem_type_hint="conjecture" if "conjecture" in spec.label else "open_question",
                    confidence=spec.base_confidence,
                    raw_text=raw,
                    extraction_method=f"regex:{spec.label}",
                )
            )

    return candidates
