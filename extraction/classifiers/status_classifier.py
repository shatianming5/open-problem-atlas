"""Classify whether a candidate is a true open problem, solved, or other."""

import re
from dataclasses import dataclass
from enum import Enum


class CandidateLabel(Enum):
    OPEN_PROBLEM = "open_problem"
    SOLVED = "solved"
    FUTURE_WORK = "future_work"
    VAGUE_AGENDA = "vague_agenda"
    NON_PROBLEM = "non_problem"
    ABSTAIN = "abstain"


@dataclass
class ClassificationResult:
    label: CandidateLabel
    confidence: float
    reason: str


# Rule-based indicators
OPEN_INDICATORS = [
    r"(?i)\bis\s+(still\s+)?open\b",
    r"(?i)\bremains\s+(un)?solved\b",
    r"(?i)\bopen\s+problem\b",
    r"(?i)\bopen\s+question\b",
    r"(?i)\bopen\s+conjecture\b",
    r"(?i)\bunsolved\b",
    r"(?i)\bunknown\s+whether\b",
    r"(?i)\bwe\s+conjecture\b",
    r"(?i)\bit\s+is\s+conjectured\b",
    r"(?i)\bno\s+proof\s+is\s+known\b",
]

SOLVED_INDICATORS = [
    r"(?i)\bwas\s+(recently\s+)?solved\b",
    r"(?i)\bhas\s+been\s+(recently\s+)?solved\b",
    r"(?i)\bwas\s+(recently\s+)?proved\b",
    r"(?i)\bhas\s+been\s+(recently\s+)?proved\b",
    r"(?i)\bwas\s+(recently\s+)?disproved\b",
    r"(?i)\bproof\s+was\s+given\b",
    r"(?i)\bsettled\s+(in|by)\b",
    r"(?i)\bresolved\s+(in|by)\b",
]

FUTURE_WORK_INDICATORS = [
    r"(?i)\bfuture\s+work\b",
    r"(?i)\bit\s+would\s+be\s+interesting\b",
    r"(?i)\bone\s+could\s+also\b",
    r"(?i)\bwe\s+leave\s+(this|it)\b",
    r"(?i)\bfurther\s+investigation\b",
    r"(?i)\bremains\s+to\s+be\s+(seen|explored|investigated)\b",
]

VAGUE_INDICATORS = [
    r"(?i)\bunderstanding\s+(the|how|why)\b",
    r"(?i)\bexploring\s+the\b",
    r"(?i)\bdeveloping\s+(new|better)\b",
    r"(?i)\bimproving\s+(the|our)\b",
]


def classify_rule_based(text: str) -> ClassificationResult:
    """Classify a candidate using rule-based heuristics.

    Returns ABSTAIN when confidence is too low.
    """
    open_score = sum(1 for p in OPEN_INDICATORS if re.search(p, text))
    solved_score = sum(1 for p in SOLVED_INDICATORS if re.search(p, text))
    future_score = sum(1 for p in FUTURE_WORK_INDICATORS if re.search(p, text))
    vague_score = sum(1 for p in VAGUE_INDICATORS if re.search(p, text))

    scores = {
        CandidateLabel.OPEN_PROBLEM: open_score,
        CandidateLabel.SOLVED: solved_score,
        CandidateLabel.FUTURE_WORK: future_score,
        CandidateLabel.VAGUE_AGENDA: vague_score,
    }

    total = sum(scores.values())
    if total == 0:
        return ClassificationResult(
            label=CandidateLabel.ABSTAIN,
            confidence=0.0,
            reason="No indicators matched",
        )

    best_label = max(scores, key=scores.get)
    best_score = scores[best_label]
    confidence = best_score / max(total, 1)

    # Require minimum confidence to not abstain
    if confidence < 0.4:
        return ClassificationResult(
            label=CandidateLabel.ABSTAIN,
            confidence=confidence,
            reason=f"Low confidence: best={best_label.value} ({confidence:.2f})",
        )

    return ClassificationResult(
        label=best_label,
        confidence=confidence,
        reason=f"Rule-based: {best_score}/{total} indicators for {best_label.value}",
    )
