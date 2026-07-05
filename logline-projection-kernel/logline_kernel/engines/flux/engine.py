"""Flux Engine v0 — custody transition engine for Google Docs -> NAS.

Core law:
    Flux does not decide truth.
    Flux does not seal Diamonds.
    Flux does not mutate canon.
    Flux only captures a process-registered source into sovereign custody.

Input:
    A process ledger entry whose light is blue / flux_engine.

Output:
    Hashed NAS custody folder, manifest, normalized text, receipts,
    and a projection-ready source object.

Dependency-free: stdlib only.

Real Google Docs export should be implemented as an adapter outside this file.
This engine only requires an exporter object with .export(act) -> list[ExportBlob].
"""
from __future__ import annotations

import os
import re
import json
import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import Any, Optional, Protocol

# ---------------------------------------------------------------------------
# Canonical hashing
# ---------------------------------------------------------------------------

def canonical_json(obj: Any) -> str:
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )

def content_hash(obj: Any, prefix: str = "") -> str:
    digest = hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()
    return f"{prefix}{digest}" if prefix else digest

def sha256_bytes(data: bytes, prefix: str = "sha256:") -> str:
    return f"{prefix}{hashlib.sha256(data).hexdigest()}"

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def safe_segment(s: str) -> str:
    """Filesystem-safe path segment."""
    s = s.strip().replace(":", "_").replace("/", "_")
    s = re.sub(r"[^A-Za-z0-9._@+=-]+", "_", s)
    return s[:180] or "unknown"

def write_bytes(path: str, data: bytes) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)

def write_text(path: str, data: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(data)

def write_json(path: str, data: dict) -> None:
    write_text(path, json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n")

# ---------------------------------------------------------------------------
# Minimal Act compatibility
# ---------------------------------------------------------------------------

ACT_SLOTS = [
    "who",
    "did",
    "this",
    "when",
    "confirmed_by",
    "if_ok",
    "if_doubt",
    "if_not",
    "status",
]

@dataclass
class Act:
    who: str
    did: str
    this: str
    when: str
    confirmed_by: Optional[str] = None
    if_ok: Optional[str] = None
    if_doubt: Optional[str] = None
    if_not: Optional[str] = None
    status: str = "registered"
    aux: dict = field(default_factory=dict)

    def body(self) -> dict:
        d = {k: getattr(self, k) for k in ACT_SLOTS}
        d["AUX"] = self.aux
        return d

    @property
    def process_id(self) -> str:
        return content_hash(self.body(), "proc:")

    @classmethod
    def from_dict(cls, d: dict) -> "Act":
        return cls(
            who=d.get("who", ""),
            did=d.get("did", ""),
            this=d.get("this", ""),
            when=d.get("when", ""),
            confirmed_by=d.get("confirmed_by"),
            if_ok=d.get("if_ok"),
            if_doubt=d.get("if_doubt"),
            if_not=d.get("if_not"),
            status=d.get("status", "registered"),
            aux=d.get("AUX", d.get("aux", {})) or {},
        )

# ---------------------------------------------------------------------------
# Receipts
# ---------------------------------------------------------------------------

class ReceiptSink(Protocol):
    def emit(self, kind: str, payload: dict, actor: str = "flux_engine") -> dict:
        ...

class NullReceipts:
    def emit(self, kind: str, payload: dict, actor: str = "flux_engine") -> dict:
        return {
            "kind": kind,
            "payload": payload,
            "actor": actor,
            "at": utc_now(),
        }

# ---------------------------------------------------------------------------
# Export adapter boundary
# ---------------------------------------------------------------------------

@dataclass
class ExportBlob:
    """One exported representation of a source document."""

    role: str
    filename: str
    media_type: str
    data: bytes

    @property
    def bytes(self) -> int:
        return len(self.data)

    @property
    def sha256(self) -> str:
        return sha256_bytes(self.data)

class SourceExporter(Protocol):
    """Adapter interface.

    Implement Google Docs export outside the kernel.
    The engine does not care whether blobs came from Drive API, local files,
    email attachment, or test fixture.
    """

    def export(self, act: Act) -> list[ExportBlob]:
        ...

class LocalFixtureExporter:
    """Test exporter.

    Reads local files declared in act.aux["origin"]["exports"].

    Example:
        "origin": {
          "exports": [
            {"role":"txt", "path":"/tmp/doc.txt", "media_type":"text/plain"},
            {"role":"html", "path":"/tmp/doc.html", "media_type":"text/html"}
          ]
        }
    """

    def export(self, act: Act) -> list[ExportBlob]:
        origin = act.aux.get("origin", {})
        exports = origin.get("exports", [])

        if not exports and origin.get("local_path"):
            exports = [{
                "role": "raw",
                "path": origin["local_path"],
                "media_type": "application/octet-stream",
            }]

        blobs: list[ExportBlob] = []

        for item in exports:
            path = item["path"]
            with open(path, "rb") as f:
                data = f.read()

            blobs.append(
                ExportBlob(
                    role=item.get("role", "raw"),
                    filename=item.get("filename") or os.path.basename(path),
                    media_type=item.get("media_type", "application/octet-stream"),
                    data=data,
                )
            )

        return blobs

# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------

class _HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if text:
            self.parts.append(text)

    def text(self) -> str:
        return "\n".join(self.parts)

def normalize_blob(blob: ExportBlob) -> Optional[str]:
    """Best-effort normalization to text.

    This is deliberately conservative. It does not pretend to understand every
    format. It extracts text only from plain text, markdown, json, and html.
    """

    mt = blob.media_type.lower()
    name = blob.filename.lower()

    if mt.startswith("text/plain") or name.endswith(".txt") or name.endswith(".md"):
        return blob.data.decode("utf-8", errors="replace")

    if mt.startswith("application/json") or name.endswith(".json"):
        try:
            obj = json.loads(blob.data.decode("utf-8", errors="replace"))
            return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True)
        except json.JSONDecodeError:
            return blob.data.decode("utf-8", errors="replace")

    if mt.startswith("text/html") or name.endswith(".html") or name.endswith(".htm"):
        parser = _HTMLTextExtractor()
        parser.feed(blob.data.decode("utf-8", errors="replace"))
        return parser.text()

    return None

def choose_best_text(blobs: list[ExportBlob]) -> str:
    """Choose best available normalized text from exported blobs."""

    preferred = [
        "text/markdown",
        "text/plain",
        "text/html",
        "application/json",
    ]

    for mt in preferred:
        for blob in blobs:
            if blob.media_type.lower().startswith(mt):
                text = normalize_blob(blob)
                if text and text.strip():
                    return text

    for blob in blobs:
        text = normalize_blob(blob)
        if text and text.strip():
            return text

    return ""

# ---------------------------------------------------------------------------
# Flux result
# ---------------------------------------------------------------------------

@dataclass
class FluxResult:
    flux_id: str
    process_record_id: str
    source_record_id: str
    custody_root: str
    manifest_path: str
    normalized_path: str
    combined_hash: str
    blobs: list[dict]
    projection_ready: bool
    next_actions: list[str]

    def to_dict(self) -> dict:
        return asdict(self)

# ---------------------------------------------------------------------------
# Flux Engine
# ---------------------------------------------------------------------------

class FluxError(Exception):
    pass

class FluxEngine:
    """Blue engine: move mutable source document into sovereign custody."""

    def __init__(
        self,
        nas_root: str,
        exporter: SourceExporter,
        receipts: Optional[ReceiptSink] = None,
    ):
        self.nas_root = nas_root
        self.exporter = exporter
        self.receipts = receipts or NullReceipts()

    def run_entry(self, process_entry: dict, actor: str = "flux_engine") -> FluxResult:
        """Run Flux on a process-ledger entry.

        The entry must already have been registered through a process contract.
        Flux checks the blue light and refuses non-flux work.
        """

        light = process_entry.get("light", {})
        if light.get("colour") != "blue" or light.get("engine") != "flux_engine":
            raise FluxError(
                f"wrong_engine:{light.get('colour')}:{light.get('engine')}"
            )

        act = Act.from_dict(process_entry["record"])
        process_record_id = process_entry["process_record_id"]

        return self.run_act(
            act=act,
            process_record_id=process_record_id,
            process_entry_hash=process_entry.get("entry_hash"),
            light=light,
            actor=actor,
        )

    def run_act(
        self,
        act: Act,
        process_record_id: str,
        process_entry_hash: Optional[str],
        light: dict,
        actor: str = "flux_engine",
    ) -> FluxResult:
        self.receipts.emit(
            "flux.started",
            {
                "process_record_id": process_record_id,
                "record_id": act.process_id,
                "this": act.this,
                "light": light,
            },
            actor=actor,
        )

        blobs = self.exporter.export(act)
        if not blobs:
            self.receipts.emit(
                "flux.failed",
                {
                    "process_record_id": process_record_id,
                    "reason": "no_export_blobs",
                },
                actor=actor,
            )
            raise FluxError("no_export_blobs")

        custody_root = self._custody_root(act)
        raw_dir = os.path.join(custody_root, "raw")
        normalized_dir = os.path.join(custody_root, "normalized")

        written_blobs: list[dict] = []

        for blob in blobs:
            filename = safe_segment(blob.filename)
            raw_path = os.path.join(raw_dir, filename)
            write_bytes(raw_path, blob.data)

            blob_record = {
                "role": blob.role,
                "filename": filename,
                "path": raw_path,
                "media_type": blob.media_type,
                "bytes": blob.bytes,
                "sha256": blob.sha256,
            }
            written_blobs.append(blob_record)

            self.receipts.emit(
                "flux.blob_written",
                {
                    "process_record_id": process_record_id,
                    "path": raw_path,
                    "sha256": blob.sha256,
                    "bytes": blob.bytes,
                    "role": blob.role,
                },
                actor=actor,
            )

        normalized_text = choose_best_text(blobs)
        projection_ready = bool(normalized_text.strip())

        normalized_path = os.path.join(normalized_dir, "source.md")
        if normalized_text:
            write_text(normalized_path, normalized_text)
        else:
            write_text(
                normalized_path,
                "# No normalized text available\n\n"
                "Flux captured raw blobs, but no text extraction was possible.\n",
            )

        combined_hash = content_hash(
            {
                "record_id": act.process_id,
                "blobs": [
                    {
                        "role": b["role"],
                        "filename": b["filename"],
                        "sha256": b["sha256"],
                        "bytes": b["bytes"],
                    }
                    for b in written_blobs
                ],
            },
            "flux-content:",
        )

        source_record_id = content_hash(
            {
                "process_record_id": process_record_id,
                "combined_hash": combined_hash,
            },
            "source:",
        )

        manifest = {
            "kind": "flux.manifest.v0",
            "flux_id": "",  # filled below
            "source_record_id": source_record_id,
            "process_record_id": process_record_id,
            "process_entry_hash": process_entry_hash,
            "record_id": act.process_id,
            "record": act.body(),
            "captured_at": utc_now(),
            "custody_root": custody_root,
            "combined_hash": combined_hash,
            "projection_ready": projection_ready,
            "origin": act.aux.get("origin", {}),
            "custody": act.aux.get("custody", {}),
            "light": light,
            "blobs": written_blobs,
            "normalized": {
                "path": normalized_path,
                "available": projection_ready,
                "sha256": sha256_bytes(
                    normalized_text.encode("utf-8")
                    if normalized_text
                    else b""
                ),
            },
            "next_actions": self._next_actions(projection_ready),
            "warnings": [] if projection_ready else ["no_normalized_text"],
        }

        manifest["flux_id"] = content_hash(
            {
                "source_record_id": source_record_id,
                "combined_hash": combined_hash,
                "custody_root": custody_root,
            },
            "flux:",
        )

        manifest_path = os.path.join(custody_root, "manifest.json")
        write_json(manifest_path, manifest)

        # Useful lightweight index file for Cerebro.
        index_md_path = os.path.join(custody_root, "index.md")
        write_text(index_md_path, self._index_markdown(manifest))

        result = FluxResult(
            flux_id=manifest["flux_id"],
            process_record_id=process_record_id,
            source_record_id=source_record_id,
            custody_root=custody_root,
            manifest_path=manifest_path,
            normalized_path=normalized_path,
            combined_hash=combined_hash,
            blobs=written_blobs,
            projection_ready=projection_ready,
            next_actions=manifest["next_actions"],
        )

        self.receipts.emit(
            "flux.completed",
            result.to_dict(),
            actor=actor,
        )

        return result

    def _custody_root(self, act: Act) -> str:
        origin = act.aux.get("origin", {})

        doc_id = (
            origin.get("doc_id")
            or origin.get("document_id")
            or act.this
            or act.process_id
        )

        revision_id = (
            origin.get("revision_id")
            or origin.get("revision")
            or origin.get("updated_at")
            or act.when
        )

        return os.path.join(
            self.nas_root,
            "Minivault",
            "flux",
            "00_raw_google_docs",
            safe_segment(str(doc_id)),
            safe_segment(str(revision_id)),
        )

    def _next_actions(self, projection_ready: bool) -> list[str]:
        if projection_ready:
            return [
                "update_cerebro_source_index",
                "summarize_source",
                "extract_concepts",
                "candidate_projection",
                "emit_flux_source_record",
            ]

        return [
            "quarantine_for_manual_review",
            "attempt_alternate_export",
            "do_not_project",
        ]

    def _index_markdown(self, manifest: dict) -> str:
        lines = [
            "---",
            f"kind: flux_source",
            f"flux_id: {manifest['flux_id']}",
            f"source_record_id: {manifest['source_record_id']}",
            f"combined_hash: {manifest['combined_hash']}",
            f"projection_ready: {str(manifest['projection_ready']).lower()}",
            f"captured_at: {manifest['captured_at']}",
            "---",
            "",
            f"# Flux Source {manifest['source_record_id']}",
            "",
            "## Origin",
            "",
            "```json",
            json.dumps(manifest.get("origin", {}), ensure_ascii=False, indent=2),
            "```",
            "",
            "## Custody",
            "",
            f"- Root: `{manifest['custody_root']}`",
            f"- Manifest: `manifest.json`",
            f"- Normalized: `{manifest['normalized']['path']}`",
            "",
            "## Blobs",
            "",
        ]

        for blob in manifest["blobs"]:
            lines.append(
                f"- `{blob['filename']}` — {blob['media_type']} — "
                f"{blob['bytes']} bytes — `{blob['sha256']}`"
            )

        lines += [
            "",
            "## Next actions",
            "",
        ]

        for action in manifest["next_actions"]:
            lines.append(f"- {action}")

        lines.append("")
        return "\n".join(lines)
