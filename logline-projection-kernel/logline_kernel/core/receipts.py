"""Receipt log — every external effect emits a receipt.

Receipts are canon logline.receipt.v0 objects (see core/receipt_v0.py):
nine slots, three-layer hashes, id == content_hash. The engine-facing
mapping is:

    who   = actor
    did   = kind
    this  = content hash of the effect detail (semantic address)
    when  = emission time
    status= "executed"
    detail= full effect payload, carried as an AUX field

`detail` is AUX by canon rules: free top-level field, included in
content_hash, excluded from tuple_hash. The legacy names result/evidence/
transport are forbidden at the receipt level and are not used.
"""
from __future__ import annotations
import json, os

from logline_kernel.core import receipt_v0
from logline_kernel.core.hashing import content_hash


def _build_receipt(kind: str, payload: dict, actor: str) -> dict:
    return receipt_v0.emit(
        who=actor,
        did=kind,
        this=content_hash(payload),
        status="executed",
        aux={"detail": payload},
    )


class NullReceipts:
    """Receipt sink that builds conformant receipts without persisting them."""

    def emit(self, kind: str, payload: dict, actor: str = "kernel") -> dict:
        return _build_receipt(kind, payload, actor)


class ReceiptLog:
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    def emit(self, kind: str, payload: dict, actor: str = "kernel") -> dict:
        receipt = _build_receipt(kind, payload, actor)
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
