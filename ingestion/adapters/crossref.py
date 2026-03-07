"""Crossref adapter for discovering papers that discuss open problems.

Uses the public Crossref REST API (https://api.crossref.org) with support for
the *polite pool* (providing a ``mailto`` query parameter to receive higher
rate limits and priority).
"""

import logging

import httpx

from .base import BaseAdapter, CandidateProblem, RawSourceRecord

logger = logging.getLogger(__name__)

CROSSREF_API = "https://api.crossref.org/works"

# Keywords used to locate papers that discuss open problems.
DEFAULT_QUERIES = [
    "open problems in mathematics",
    "unsolved conjectures",
    "open questions combinatorics",
    "open problems number theory",
    "open problems graph theory",
]


class CrossrefAdapter(BaseAdapter):
    """Adapter for the Crossref REST API.

    Searches for scholarly works whose titles or abstracts mention open
    problems, conjectures or unsolved questions.
    """

    def __init__(self, mailto: str | None = None):
        """Initialise the adapter.

        Args:
            mailto: An email address to pass as the ``mailto`` query parameter.
                Crossref routes requests that include a valid mailto through the
                *polite pool*, which offers better performance and higher rate
                limits.
        """
        self.mailto = mailto
        self.client = httpx.Client(
            timeout=30,
            headers={"User-Agent": "OpenQuestionBot/1.0 (mailto:{})".format(
                mailto or "openquestion@example.com"
            )},
        )

    # ------------------------------------------------------------------
    # BaseAdapter interface
    # ------------------------------------------------------------------

    @property
    def source_name(self) -> str:
        return "Crossref"

    @property
    def source_tier(self) -> int:
        return 2

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _search(
        self, query: str, rows: int = 20, offset: int = 0
    ) -> list[dict]:
        """Execute a single query against the Crossref /works endpoint."""
        params: dict[str, str | int] = {
            "query": query,
            "rows": rows,
            "offset": offset,
            "sort": "relevance",
            "order": "desc",
            "select": (
                "DOI,title,author,abstract,published-print,"
                "published-online,type,subject,URL"
            ),
        }
        if self.mailto:
            params["mailto"] = self.mailto

        try:
            resp = self.client.get(CROSSREF_API, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("message", {}).get("items", [])
        except httpx.HTTPError as exc:
            logger.warning("Crossref search failed for '%s': %s", query, exc)
            return []
        except (KeyError, ValueError) as exc:
            logger.warning("Crossref response parse error: %s", exc)
            return []

    @staticmethod
    def _parse_item(item: dict) -> dict:
        """Normalise a single Crossref work item into a flat dict."""
        titles = item.get("title", [])
        title = titles[0] if titles else ""

        authors: list[str] = []
        for author in item.get("author", []):
            given = author.get("given", "")
            family = author.get("family", "")
            name = f"{given} {family}".strip()
            if name:
                authors.append(name)

        abstract = item.get("abstract", "")
        # Crossref abstracts may contain JATS XML tags; strip them.
        if abstract:
            import re
            abstract = re.sub(r"<[^>]+>", "", abstract).strip()

        doi = item.get("DOI", "")
        url = item.get("URL", f"https://doi.org/{doi}" if doi else "")

        year = None
        for date_field in ("published-print", "published-online"):
            parts = item.get(date_field, {}).get("date-parts", [[]])
            if parts and parts[0]:
                year = parts[0][0]
                break

        subjects = item.get("subject", [])

        return {
            "doi": doi,
            "title": title,
            "authors": authors,
            "abstract": abstract,
            "year": year,
            "url": url,
            "subjects": subjects,
            "type": item.get("type", ""),
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fetch(
        self,
        queries: list[str] | None = None,
        rows_per_query: int = 20,
        **kwargs,
    ) -> list[RawSourceRecord]:
        """Search Crossref for papers related to open problems.

        Args:
            queries: Search query strings. Defaults to ``DEFAULT_QUERIES``.
            rows_per_query: Maximum number of results per query.

        Returns:
            A list of ``RawSourceRecord`` instances.
        """
        queries = queries or DEFAULT_QUERIES
        records: list[RawSourceRecord] = []
        seen_dois: set[str] = set()

        for query in queries:
            items = self._search(query, rows=rows_per_query)
            for item in items:
                parsed = self._parse_item(item)
                doi = parsed["doi"]
                if not doi or doi in seen_dois:
                    continue
                seen_dois.add(doi)

                record = RawSourceRecord(
                    source_id=f"crossref_{doi.replace('/', '_').replace('.', '_')}",
                    source_kind="paper",
                    source_tier=self.source_tier,
                    title=parsed["title"],
                    authors=parsed["authors"],
                    year=parsed["year"],
                    url=parsed["url"],
                    doi=doi,
                    content_sections=[
                        {"type": "abstract", "text": parsed["abstract"]},
                    ],
                    metadata={
                        "doi": doi,
                        "subjects": parsed["subjects"],
                        "work_type": parsed["type"],
                        "query": query,
                    },
                )
                records.append(record)

        logger.info("Fetched %d records from Crossref", len(records))
        return records

    def extract_candidates(
        self, records: list[RawSourceRecord]
    ) -> list[CandidateProblem]:
        """Identify candidate open problems from Crossref paper metadata.

        Uses keyword matching on the title and abstract to surface papers that
        are likely to state or survey open problems.
        """
        keywords = [
            "open problem",
            "open question",
            "conjecture",
            "unsolved",
            "unresolved",
            "remains open",
            "still open",
        ]
        candidates: list[CandidateProblem] = []

        for record in records:
            abstract = ""
            for section in record.content_sections:
                if section.get("type") == "abstract":
                    abstract = section.get("text", "")
                    break

            searchable = f"{record.title} {abstract}".lower()
            matched_kws = [kw for kw in keywords if kw in searchable]
            if not matched_kws:
                continue

            # More keyword matches -> higher confidence.
            confidence = min(0.3 + 0.1 * len(matched_kws), 0.7)
            subjects = record.metadata.get("subjects", [])
            domain_hint = ""
            if any("math" in s.lower() for s in subjects):
                domain_hint = "mathematics"
            elif any("comput" in s.lower() for s in subjects):
                domain_hint = "theoretical-cs"

            candidate = CandidateProblem(
                title=record.title,
                statement=abstract if abstract else record.title,
                source_id=record.source_id,
                source_locator=record.url or "",
                domain_hint=domain_hint,
                subdomain_hint=", ".join(subjects[:3]),
                problem_type_hint="survey_mention",
                confidence=confidence,
                raw_text=abstract,
                extraction_method="crossref_keyword_match",
            )
            candidates.append(candidate)

        logger.info(
            "Extracted %d candidates from %d Crossref records",
            len(candidates),
            len(records),
        )
        return candidates
