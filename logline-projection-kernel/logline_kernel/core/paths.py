"""Path helpers for NAS/vault directories."""
from __future__ import annotations
import os


def ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path


def safe_join(*parts: str) -> str:
    return os.path.join(*parts)
