"""Verification backends registry."""

from .base import Backend

_REGISTRY: dict[str, type[Backend]] = {}


def register(name: str):
    """Decorator to register a backend class."""
    def wrapper(cls):
        _REGISTRY[name] = cls
        return cls
    return wrapper


def get_backend(name: str) -> Backend:
    """Get an instantiated backend by name."""
    if name not in _REGISTRY:
        # Try to import the module to trigger registration
        if name == "python_checker":
            from . import python_checker  # noqa: F401
        elif name == "sat_smt":
            from . import sat_smt  # noqa: F401
        elif name == "lean4":
            from . import lean4  # noqa: F401
    if name not in _REGISTRY:
        raise ValueError(f"Unknown backend: {name}")
    return _REGISTRY[name]()


def list_backends() -> list[str]:
    """List all registered backend names."""
    # Force import all backends
    for mod in ["python_checker", "sat_smt", "lean4"]:
        try:
            if mod == "python_checker":
                from . import python_checker  # noqa: F401
            elif mod == "sat_smt":
                from . import sat_smt  # noqa: F401
            elif mod == "lean4":
                from . import lean4  # noqa: F401
        except ImportError:
            pass
    return list(_REGISTRY.keys())
