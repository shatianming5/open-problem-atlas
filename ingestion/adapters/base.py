"""Base adapter for ingesting open problems from external sources."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date


@dataclass
class RawSourceRecord:
    """Normalized record from an external source."""

    source_id: str
    source_kind: str  # paper, survey, problem_list, etc.
    source_tier: int  # 1, 2, or 3
    title: str
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    url: str | None = None
    doi: str | None = None
    content_sections: list[dict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    fetched_at: str = field(default_factory=lambda: date.today().isoformat())


@dataclass
class CandidateProblem:
    """A candidate open problem extracted from a source."""

    title: str
    statement: str
    source_id: str
    source_locator: str = ""
    domain_hint: str = ""
    subdomain_hint: str = ""
    problem_type_hint: str = ""
    confidence: float = 0.5
    raw_text: str = ""
    extraction_method: str = ""


class BaseAdapter(ABC):
    """Abstract base class for source adapters."""

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Human-readable name of this source."""

    @property
    @abstractmethod
    def source_tier(self) -> int:
        """Source tier (1, 2, or 3)."""

    @abstractmethod
    def fetch(self, **kwargs) -> list[RawSourceRecord]:
        """Fetch raw records from the source.

        Returns a list of normalized source records.
        """

    @abstractmethod
    def extract_candidates(self, records: list[RawSourceRecord]) -> list[CandidateProblem]:
        """Extract candidate problems from raw records.

        Returns a list of candidate problems for review.
        """

    def run(self, **kwargs) -> list[CandidateProblem]:
        """Full pipeline: fetch then extract."""
        records = self.fetch(**kwargs)
        return self.extract_candidates(records)
