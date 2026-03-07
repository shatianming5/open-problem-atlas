"""Erdos Problems adapter for ingesting open problems from erdosproblems.com."""

import base64
import logging

import httpx
import yaml

from .base import BaseAdapter, CandidateProblem, RawSourceRecord

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"
REPO_OWNER = "teorth"
REPO_NAME = "erdosproblems"
# The YAML problem data lives under the _problems/ directory in the repo.
PROBLEMS_PATH = "_problems"


class ErdosProblemsAdapter(BaseAdapter):
    """Adapter for Erdos Problems (erdosproblems.com).

    Fetches problem data in YAML format from the backing GitHub repository
    maintained by Terence Tao and collaborators.
    """

    def __init__(self, github_token: str | None = None):
        """Initialise the adapter.

        Args:
            github_token: Optional GitHub personal access token to raise the
                API rate limit from 60 to 5 000 requests/hour.
        """
        headers: dict[str, str] = {"Accept": "application/vnd.github.v3+json"}
        if github_token:
            headers["Authorization"] = f"token {github_token}"
        self.client = httpx.Client(timeout=30, headers=headers)

    # ------------------------------------------------------------------
    # BaseAdapter interface
    # ------------------------------------------------------------------

    @property
    def source_name(self) -> str:
        return "ErdosProblems"

    @property
    def source_tier(self) -> int:
        return 1

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _list_problem_files(self) -> list[dict]:
        """List YAML files under the _problems/ directory via the GitHub
        Contents API."""
        url = f"{GITHUB_API}/repos/{REPO_OWNER}/{REPO_NAME}/contents/{PROBLEMS_PATH}"
        try:
            resp = self.client.get(url)
            resp.raise_for_status()
            items = resp.json()
            return [
                item for item in items
                if isinstance(item, dict)
                and item.get("name", "").endswith((".yaml", ".yml", ".md"))
            ]
        except httpx.HTTPError as exc:
            logger.warning("Failed to list problem files from GitHub: %s", exc)
            return []

    def _fetch_file_content(self, file_info: dict) -> str | None:
        """Download and decode a single file from the GitHub Contents API."""
        download_url = file_info.get("download_url")
        if download_url:
            try:
                resp = self.client.get(download_url)
                resp.raise_for_status()
                return resp.text
            except httpx.HTTPError as exc:
                logger.warning("Failed to download %s: %s", download_url, exc)
                return None

        # Fallback: decode the base-64 content returned inline.
        content_b64 = file_info.get("content")
        if content_b64:
            try:
                return base64.b64decode(content_b64).decode("utf-8")
            except Exception as exc:
                logger.warning("Failed to decode base64 content: %s", exc)
        return None

    @staticmethod
    def _parse_yaml_front_matter(text: str) -> dict:
        """Parse YAML front-matter delimited by ``---`` from a Markdown file.

        Returns the parsed dict, or an empty dict on failure.
        """
        text = text.strip()
        if not text.startswith("---"):
            # Try to parse the whole file as plain YAML.
            try:
                data = yaml.safe_load(text)
                return data if isinstance(data, dict) else {}
            except yaml.YAMLError:
                return {}

        parts = text.split("---", 2)
        if len(parts) < 3:
            return {}
        try:
            data = yaml.safe_load(parts[1])
            return data if isinstance(data, dict) else {}
        except yaml.YAMLError:
            return {}

    @staticmethod
    def _extract_body(text: str) -> str:
        """Return the Markdown body after the YAML front-matter."""
        text = text.strip()
        if not text.startswith("---"):
            return ""
        parts = text.split("---", 2)
        if len(parts) < 3:
            return ""
        return parts[2].strip()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fetch(self, max_files: int = 500, **kwargs) -> list[RawSourceRecord]:
        """Fetch problem records from the GitHub-backed YAML data.

        Args:
            max_files: Maximum number of problem files to download.

        Returns:
            A list of ``RawSourceRecord`` instances.
        """
        files = self._list_problem_files()
        if not files:
            logger.warning("No problem files found in the repository.")
            return []

        files = files[:max_files]
        records: list[RawSourceRecord] = []

        for file_info in files:
            raw_text = self._fetch_file_content(file_info)
            if raw_text is None:
                continue

            meta = self._parse_yaml_front_matter(raw_text)
            body = self._extract_body(raw_text)
            file_name = file_info.get("name", "unknown")
            problem_id = file_name.rsplit(".", 1)[0]

            title = meta.get("title", problem_id)
            status = meta.get("status", "open")
            authors: list[str] = []
            if "author" in meta:
                a = meta["author"]
                authors = a if isinstance(a, list) else [str(a)]

            year = meta.get("year")
            if isinstance(year, str) and year.isdigit():
                year = int(year)
            elif not isinstance(year, int):
                year = None

            record = RawSourceRecord(
                source_id=f"erdos_{problem_id}",
                source_kind="problem_list",
                source_tier=self.source_tier,
                title=str(title),
                authors=authors,
                year=year,
                url=f"https://www.erdosproblems.com/problems/{problem_id}",
                content_sections=[
                    {"type": "description", "text": body},
                ],
                metadata={
                    "status": status,
                    "tags": meta.get("tags", []),
                    "category": meta.get("category", ""),
                    "file_name": file_name,
                    **{k: v for k, v in meta.items()
                       if k not in ("title", "status", "author", "year",
                                    "tags", "category")},
                },
            )
            records.append(record)

        logger.info("Fetched %d records from ErdosProblems", len(records))
        return records

    def extract_candidates(
        self, records: list[RawSourceRecord]
    ) -> list[CandidateProblem]:
        """Extract candidate open problems from fetched Erdos Problem records.

        Only problems whose status indicates they are still open are returned.
        """
        open_statuses = {"open", "partially solved", "partial"}
        candidates: list[CandidateProblem] = []

        for record in records:
            status = str(record.metadata.get("status", "open")).lower().strip()
            if status not in open_statuses:
                continue

            description = ""
            for section in record.content_sections:
                if section.get("type") == "description":
                    description = section.get("text", "")
                    break

            candidate = CandidateProblem(
                title=record.title,
                statement=description if description else record.title,
                source_id=record.source_id,
                source_locator=record.url or "",
                domain_hint="mathematics",
                subdomain_hint=record.metadata.get("category", ""),
                problem_type_hint="conjecture",
                confidence=0.85,
                raw_text=description,
                extraction_method="erdos_yaml_status_filter",
            )
            candidates.append(candidate)

        logger.info(
            "Extracted %d open candidates from %d ErdosProblems records",
            len(candidates),
            len(records),
        )
        return candidates
