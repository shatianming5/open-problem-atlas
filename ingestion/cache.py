"""Simple file-system-based JSON cache with TTL support."""

import hashlib
import json
import os
import time
from pathlib import Path


_DEFAULT_CACHE_DIR = Path(".cache")


class FetchCache:
    """Key-value cache backed by JSON files on disk.

    Each entry is stored as a separate ``.json`` file inside *cache_dir*.
    A time-to-live (TTL) mechanism allows entries to expire automatically.

    Parameters
    ----------
    cache_dir:
        Directory where cache files are stored.
        Defaults to ``.cache/`` in the current working directory.
    """

    def __init__(self, cache_dir: str | Path | None = None) -> None:
        self._dir = Path(cache_dir) if cache_dir else _DEFAULT_CACHE_DIR
        self._dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _key_to_filename(key: str) -> str:
        """Derive a safe filename from an arbitrary key string."""
        h = hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]
        # Prefix with a short alphanumeric slug for debugging.
        slug = "".join(c if c.isalnum() else "_" for c in key[:40])
        return f"{slug}__{h}.json"

    def _path_for(self, key: str) -> Path:
        return self._dir / self._key_to_filename(key)

    @staticmethod
    def _is_expired(record: dict) -> bool:
        """Return True if *record* has a TTL that has elapsed."""
        expires_at = record.get("expires_at")
        if expires_at is None:
            return False
        return time.time() > expires_at

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def has(self, key: str) -> bool:
        """Return ``True`` if a non-expired entry for *key* exists."""
        path = self._path_for(key)
        if not path.exists():
            return False
        try:
            with open(path, "r", encoding="utf-8") as f:
                record = json.load(f)
        except (json.JSONDecodeError, OSError):
            return False
        if self._is_expired(record):
            path.unlink(missing_ok=True)
            return False
        return True

    def get(self, key: str, default=None):
        """Retrieve the cached value for *key*, or *default* if missing/expired."""
        path = self._path_for(key)
        if not path.exists():
            return default
        try:
            with open(path, "r", encoding="utf-8") as f:
                record = json.load(f)
        except (json.JSONDecodeError, OSError):
            return default
        if self._is_expired(record):
            path.unlink(missing_ok=True)
            return default
        return record.get("value", default)

    def set(self, key: str, value, *, ttl_hours: float | None = None) -> None:
        """Store *value* under *key*.

        Parameters
        ----------
        key:
            Cache key (arbitrary string).
        value:
            Any JSON-serializable value.
        ttl_hours:
            Optional time-to-live in hours.  After this period the entry
            is treated as expired.  ``None`` means the entry never expires.
        """
        record: dict = {
            "key": key,
            "value": value,
            "stored_at": time.time(),
        }
        if ttl_hours is not None:
            record["expires_at"] = time.time() + ttl_hours * 3600
        path = self._path_for(key)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)

    def delete(self, key: str) -> bool:
        """Remove the entry for *key*.  Returns ``True`` if it existed."""
        path = self._path_for(key)
        if path.exists():
            path.unlink()
            return True
        return False

    def clear(self) -> int:
        """Remove **all** cache files.  Returns the number of files deleted."""
        count = 0
        for p in self._dir.glob("*.json"):
            p.unlink()
            count += 1
        return count

    def purge_expired(self) -> int:
        """Remove expired entries.  Returns the number of entries purged."""
        count = 0
        for p in self._dir.glob("*.json"):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    record = json.load(f)
                if self._is_expired(record):
                    p.unlink()
                    count += 1
            except (json.JSONDecodeError, OSError):
                p.unlink()
                count += 1
        return count
