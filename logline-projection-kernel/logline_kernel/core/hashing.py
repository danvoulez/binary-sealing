"""Content-addressed hashing for the LogLine Kernel.

Uses canonical JSON (sorted keys, no whitespace) + SHA-256.
"""
from __future__ import annotations
import hashlib, json


def canonical_json(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def content_hash(obj, prefix: str = "") -> str:
    raw = canonical_json(obj)
    digest = hashlib.sha256(raw).hexdigest()
    return f"{prefix}{digest}" if prefix else digest
