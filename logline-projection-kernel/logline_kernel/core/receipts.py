"""Receipt log — every external effect emits a receipt."""
from __future__ import annotations
import json, os
from datetime import datetime, timezone

from logline_kernel.core.hashing import content_hash


class NullReceipts:
    """Receipt sink that discards to stdout-like dicts."""

    def emit(self, kind: str, payload: dict, actor: str = "kernel") -> dict:
        receipt = {
            "kind": kind,
            "actor": actor,
            "emitted_at": datetime.now(timezone.utc).isoformat(),
            "payload": payload,
        }
        return receipt


class ReceiptLog:
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    def emit(self, kind: str, payload: dict, actor: str = "kernel") -> dict:
        receipt = {
            "kind": kind,
            "actor": actor,
            "emitted_at": datetime.now(timezone.utc).isoformat(),
            "payload": payload,
        }
        receipt["receipt_id"] = content_hash(receipt, "receipt:")
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(receipt, ensure_ascii=False) + "\n")
        return receipt

    def entries(self):
        if not os.path.exists(self.path):
            return
        with open(self.path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    yield json.loads(line)
