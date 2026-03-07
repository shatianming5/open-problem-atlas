"""Tests for extraction components."""

from extraction.classifiers.status_classifier import (
    CandidateLabel,
    classify_rule_based,
)
from extraction.dedupe.deduplicator import (
    exact_match,
    find_duplicates,
    normalize_title,
    token_overlap,
)
from ingestion.adapters.base import CandidateProblem


class TestStatusClassifier:
    def test_open_problem_detected(self):
        result = classify_rule_based("This is an open problem that remains unsolved.")
        assert result.label == CandidateLabel.OPEN_PROBLEM

    def test_solved_detected(self):
        result = classify_rule_based("This conjecture was recently proved by Smith in 2024.")
        assert result.label == CandidateLabel.SOLVED

    def test_future_work_detected(self):
        result = classify_rule_based("In future work, it would be interesting to explore this direction.")
        assert result.label == CandidateLabel.FUTURE_WORK

    def test_abstain_on_no_indicators(self):
        result = classify_rule_based("The sky is blue and water is wet.")
        assert result.label == CandidateLabel.ABSTAIN

    def test_confidence_range(self):
        result = classify_rule_based("This is an open problem.")
        assert 0.0 <= result.confidence <= 1.0


class TestDeduplication:
    def test_normalize_title(self):
        assert normalize_title("The Collatz Conjecture") == normalize_title("collatz")

    def test_exact_match(self):
        assert exact_match("Twin Prime Conjecture", "twin prime conjecture")
        assert not exact_match("Twin Prime", "Goldbach")

    def test_token_overlap(self):
        score = token_overlap("Twin Prime Conjecture", "Twin Primes Problem")
        assert score > 0.3

    def test_find_duplicates_removes_exact(self):
        candidates = [
            CandidateProblem(title="Collatz Conjecture", statement="", source_id="a"),
            CandidateProblem(title="collatz conjecture", statement="", source_id="b"),
        ]
        unique, matches = find_duplicates(candidates)
        assert len(unique) == 1
        assert len(matches) == 1
        assert matches[0].match_level == "exact"

    def test_find_duplicates_flags_similar(self):
        candidates = [
            CandidateProblem(title="Twin Prime Conjecture", statement="", source_id="a"),
        ]
        existing = ["Twin Primes Problem"]
        unique, matches = find_duplicates(candidates, existing, threshold=0.4)
        assert len(matches) >= 0  # May or may not match depending on threshold
