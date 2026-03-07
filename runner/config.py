"""Path constants and defaults for the runner."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
PROBLEMS_DIR = DATA_DIR / "problems"
ATTEMPTS_DIR = DATA_DIR / "attempts"
CONTRACTS_DIR = ROOT / "verifiers" / "contracts"
CHECKERS_DIR = ROOT / "verifiers" / "checkers"
SCHEMA_DIR = ROOT / "schema"

DEFAULT_TIMEOUT = 300
DEFAULT_MEMORY_MB = 1024
