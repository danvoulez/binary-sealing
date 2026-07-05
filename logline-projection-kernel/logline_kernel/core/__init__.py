"""Core shared primitive utilities."""

from logline_kernel.core.errors import (
    AccessDeniedError,
    AdmissionError,
    LogLineError,
    ProjectionError,
    RegistrationError,
    SealingError,
)
from logline_kernel.core.hashing import canonical_json, content_hash
from logline_kernel.core.paths import ensure_dir, safe_join
from logline_kernel.core.receipts import NullReceipts, ReceiptLog
from logline_kernel.core.time import is_iso8601, now_iso

__all__ = [
    "AccessDeniedError",
    "AdmissionError",
    "LogLineError",
    "ProjectionError",
    "RegistrationError",
    "SealingError",
    "canonical_json",
    "content_hash",
    "ensure_dir",
    "safe_join",
    "NullReceipts",
    "ReceiptLog",
    "is_iso8601",
    "now_iso",
]
