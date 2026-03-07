"""Google DeepMind formal-conjectures adapter.

Ingests formalised conjectures from the ``google-deepmind/formal-conjectures``
GitHub repository, which contains Lean 4 files with structured metadata
comments.
"""

import base64
import logging
import re

import httpx

from .base import BaseAdapter, CandidateProblem, RawSourceRecord

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"
REPO_OWNER = "google-deepmind"
REPO_NAME = "formal-conjectures"
# Lean source files typically reside under a top-level directory.
LEAN_ROOT = "FormalConjectures"


class FormalConjecturesAdapter(BaseAdapter):
    """Adapter for Google DeepMind's formal-conjectures repository.

    The repository stores open conjectures formalised in Lean 4.  Each ``.lean``
    file may contain one or more conjectures annotated with structured doc
    comments (``/-- ... -/``) that include metadata such as status and subject
    tags.
    """

    def __init__(self, github_token: str | None = None):
        """Initialise the adapter.

        Args:
            github_token: Optional GitHub personal access token for higher rate
                limits.
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
        return "FormalConjectures"

    @property
    def source_tier(self) -> int:
        return 1

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _list_lean_files(self, path: str = LEAN_ROOT) -> list[dict]:
        """Recursively list ``.lean`` files via the GitHub Trees API."""
        url = (
            f"{GITHUB_API}/repos/{REPO_OWNER}/{REPO_NAME}"
            f"/git/trees/main?recursive=1"
        )
        try:
            resp = self.client.get(url)
            resp.raise_for_status()
            tree = resp.json().get("tree", [])
            return [
                item for item in tree
                if item.get("path", "").startswith(path)
                and item.get("path", "").endswith(".lean")
                and item.get("type") == "blob"
            ]
        except httpx.HTTPError as exc:
            logger.warning(
                "Failed to list Lean files from %s/%s: %s",
                REPO_OWNER, REPO_NAME, exc,
            )
            return []

    def _fetch_file_content(self, file_path: str) -> str | None:
        """Download a single file's content from the GitHub Contents API."""
        url = (
            f"{GITHUB_API}/repos/{REPO_OWNER}/{REPO_NAME}"
            f"/contents/{file_path}"
        )
        try:
            resp = self.client.get(url)
            resp.raise_for_status()
            data = resp.json()
            # Prefer download_url for large files.
            download_url = data.get("download_url")
            if download_url:
                dl_resp = self.client.get(download_url)
                dl_resp.raise_for_status()
                return dl_resp.text
            content_b64 = data.get("content", "")
            return base64.b64decode(content_b64).decode("utf-8")
        except (httpx.HTTPError, Exception) as exc:
            logger.warning("Failed to fetch %s: %s", file_path, exc)
            return None

    # Regex patterns for parsing Lean 4 doc comments and theorem/conjecture
    # declarations.
    _DOC_COMMENT_RE = re.compile(
        r"/--\s*(.*?)\s*-/", re.DOTALL
    )
    _CONJECTURE_DECL_RE = re.compile(
        r"(?:theorem|lemma|def)\s+([\w.]+)", re.MULTILINE
    )
    _STATUS_RE = re.compile(r"status\s*:\s*(\w[\w\s]*)", re.IGNORECASE)
    _SUBJECT_RE = re.compile(r"subject\s*:\s*(.+)", re.IGNORECASE)
    _TAGS_RE = re.compile(r"tags?\s*:\s*(.+)", re.IGNORECASE)

    def _parse_lean_conjectures(
        self, text: str, file_path: str
    ) -> list[dict]:
        """Extract conjecture metadata from a Lean 4 source file.

        Heuristics:
        1. Find doc-comment blocks (``/-- ... -/``).
        2. Find the immediately following ``theorem``/``lemma``/``def`` name.
        3. Parse structured tags out of the doc comment.
        """
        results: list[dict] = []
        # Split the file by doc-comment boundaries so we can pair each comment
        # with the declaration that follows it.
        parts = self._DOC_COMMENT_RE.split(text)
        # parts alternates: [before, comment_body, after, comment_body, ...]
        for i in range(1, len(parts), 2):
            comment_body = parts[i]
            after_comment = parts[i + 1] if i + 1 < len(parts) else ""

            decl_match = self._CONJECTURE_DECL_RE.search(after_comment[:500])
            name = decl_match.group(1) if decl_match else f"unnamed_{i}"

            status_match = self._STATUS_RE.search(comment_body)
            status = status_match.group(1).strip() if status_match else "open"

            subject_match = self._SUBJECT_RE.search(comment_body)
            subject = subject_match.group(1).strip() if subject_match else ""

            tags_match = self._TAGS_RE.search(comment_body)
            tags_str = tags_match.group(1).strip() if tags_match else ""
            tags = [t.strip() for t in tags_str.split(",") if t.strip()]

            # Use the first line of the comment as a summary, the rest as body.
            lines = [l.strip() for l in comment_body.strip().splitlines() if l.strip()]
            summary = lines[0] if lines else name
            body = "\n".join(lines[1:]) if len(lines) > 1 else ""

            results.append({
                "name": name,
                "summary": summary,
                "body": body,
                "status": status,
                "subject": subject,
                "tags": tags,
                "file_path": file_path,
            })

        # Fallback: if no doc comments found, look for bare declarations.
        if not results:
            for m in self._CONJECTURE_DECL_RE.finditer(text):
                results.append({
                    "name": m.group(1),
                    "summary": m.group(1),
                    "body": "",
                    "status": "open",
                    "subject": "",
                    "tags": [],
                    "file_path": file_path,
                })

        return results

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fetch(self, max_files: int = 300, **kwargs) -> list[RawSourceRecord]:
        """Fetch formalised conjecture records from the repository.

        Args:
            max_files: Maximum number of ``.lean`` files to process.

        Returns:
            A list of ``RawSourceRecord`` instances, one per Lean file.
        """
        lean_files = self._list_lean_files()
        if not lean_files:
            logger.warning("No Lean files found in %s/%s.", REPO_OWNER, REPO_NAME)
            return []

        lean_files = lean_files[:max_files]
        records: list[RawSourceRecord] = []

        for item in lean_files:
            file_path = item["path"]
            content = self._fetch_file_content(file_path)
            if content is None:
                continue

            conjectures = self._parse_lean_conjectures(content, file_path)
            file_name = file_path.rsplit("/", 1)[-1]
            safe_id = file_name.replace(".lean", "").replace("/", "_")

            record = RawSourceRecord(
                source_id=f"formalconj_{safe_id}",
                source_kind="problem_list",
                source_tier=self.source_tier,
                title=file_name.replace(".lean", ""),
                url=f"https://github.com/{REPO_OWNER}/{REPO_NAME}/blob/main/{file_path}",
                content_sections=[
                    {"type": "lean_source", "text": content},
                ],
                metadata={
                    "file_path": file_path,
                    "conjectures": conjectures,
                },
            )
            records.append(record)

        logger.info("Fetched %d Lean files from FormalConjectures", len(records))
        return records

    def extract_candidates(
        self, records: list[RawSourceRecord]
    ) -> list[CandidateProblem]:
        """Extract candidate open conjectures from the fetched Lean file records."""
        candidates: list[CandidateProblem] = []

        for record in records:
            conjectures = record.metadata.get("conjectures", [])
            for conj in conjectures:
                status = str(conj.get("status", "open")).lower().strip()
                if status not in ("open", ""):
                    continue

                statement = conj.get("body") or conj.get("summary", "")
                candidate = CandidateProblem(
                    title=conj.get("name", record.title),
                    statement=statement,
                    source_id=record.source_id,
                    source_locator=record.url or "",
                    domain_hint="mathematics",
                    subdomain_hint=conj.get("subject", ""),
                    problem_type_hint="formal_conjecture",
                    confidence=0.9,
                    raw_text=f"{conj.get('summary', '')}\n{conj.get('body', '')}".strip(),
                    extraction_method="lean_doccomment_parse",
                )
                candidates.append(candidate)

        logger.info(
            "Extracted %d candidates from %d FormalConjectures records",
            len(candidates),
            len(records),
        )
        return candidates
