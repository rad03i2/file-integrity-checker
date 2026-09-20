"""File Integrity Checker — local SHA-256 integrity baselines."""

__version__ = "1.0.0"
__author__ = "Radwan Abdulhadi Ahmed / @rad03i2"

from .core import build_baseline, load_baseline, report_dict, save_baseline, sha256_file, verify

__all__ = ["build_baseline", "load_baseline", "report_dict", "save_baseline", "sha256_file", "verify"]
