"""Test all checkers can be imported and run with small default params."""
import importlib.util
from pathlib import Path

CHECKERS_DIR = Path(__file__).resolve().parent.parent / "verifiers" / "checkers" / "math"

def test_all_math_checkers_importable():
    for py_file in sorted(CHECKERS_DIR.glob("*_checker.py")):
        spec = importlib.util.spec_from_file_location(py_file.stem, py_file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        assert hasattr(mod, "verify"), f"{py_file.stem} missing verify()"

def test_checkers_return_valid_format():
    for py_file in sorted(CHECKERS_DIR.glob("*_checker.py")):
        spec = importlib.util.spec_from_file_location(py_file.stem, py_file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        result = mod.verify({"upper_bound": 100, "max_order": 10, "max_n": 20, "limit": 100, "n_runners": 3, "max_k": 5, "max_vertices": 6, "num_primes": 100, "max_row": 50, "max_ground_set": 4, "paley_prime": 5, "max_dim": 4, "grid_size": 10, "num_steps": 100, "num_angles": 50, "max_steps": 50, "max_base": 20, "max_q": 5, "max_c": 100, "max_rows": 20, "max_d": 2, "max_degree": 5, "max_h": 3, "max_mn": 4, "n_max": 20, "degree": 5, "trials": 10, "num_samples": 50, "dim": 5, "samples": 20, "n": 6, "n_points": 4, "max_mk": 3, "size": 20, "steps": 100})
        assert isinstance(result, dict), f"{py_file.stem} didn't return dict"
        assert "status" in result, f"{py_file.stem} missing status"
        assert result["status"] in ("pass", "fail", "error", "timeout", "unknown"), f"{py_file.stem} invalid status: {result['status']}"
        assert "summary" in result, f"{py_file.stem} missing summary"
