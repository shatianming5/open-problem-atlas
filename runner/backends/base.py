"""Abstract base class for verification backends."""

from abc import ABC, abstractmethod

from ..verdict import Verdict


class Backend(ABC):
    """Base class that all verification backends must implement."""

    @abstractmethod
    def run(self, contract: dict) -> Verdict:
        """Run a verification contract and return a verdict."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check whether this backend's dependencies are available."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable backend name."""
        ...
