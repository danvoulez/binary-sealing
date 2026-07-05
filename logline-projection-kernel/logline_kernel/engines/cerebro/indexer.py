"""Cerebro Indexer v0 — semantic custody layer over Minivault Flux sources.

Core law:
    Cerebro organizes.
    Cerebro does not canonize.
    Cerebro does not decide truth.
    Cerebro makes sources addressable, linkable, and projection-ready.

Input:
    flux.manifest.v0 produced by Flux Engine.

Output:
    Markdown source card, source summary, concept pages, graph edges,
    source index, and receipts.

Dependency-free: stdlib only.
"""
from __future__ import annotations

import os
import re
import json
import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
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

def sha256_text(text: str, prefix: str = "sha256:") -> str:
    return f"{prefix}{hashlib.sha256(text.encode('utf-8')).hexdigest()}"

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def safe_slug(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s[:120] or "unknown"

def write_text(path: str, data: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(data)

def append_text(path: str, data: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(data)

def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_json(path: str, data: dict) -> None:
    write_text(path, json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n")

def append_ndjson(path: str, obj: dict) -> None:
    append_text(path, json.dumps(obj, ensure_ascii=False, sort_keys=True) + "\n")

# ---------------------------------------------------------------------------
# Receipts
# ---------------------------------------------------------------------------

class ReceiptSink(Protocol):
    def emit(self, kind: str, payload: dict, actor: str = "cerebro_indexer") -> dict:
        ...

class NullReceipts:
    def emit(self, kind: str, payload: dict, actor: str = "cerebro_indexer") -> dict:
        return {
            "kind": kind,
            "payload": payload,
            "actor": actor,
            "at": utc_now(),
        }

# ---------------------------------------------------------------------------
# Indexer config
# ---------------------------------------------------------------------------

DEFAULT_GLOSSARY = {
    "logline": ["logline", "loglineos"],
    "act": ["act", "acts", "nine slots", "9 slots"],
    "process": ["process", "processual", "process contract"],
    "dynamic_projection": ["dynamic projection", "dynamic projections", "projection kernel"],
    "diamond": ["diamond", "diamonds", "non-collapsing span", "non collapsing span"],
    "cerebro": ["cerebro", "wiki", "second brain"],
    "minivault": ["minivault", "vault", "nas", "sovereign vault"],
    "flux": ["flux", "google docs", "drive export"],
    "operator_mesh": ["operator mesh", "four operators", "personal agents"],
    "doubt": ["doubt", "uncertainty", "contested", "missing evidence"],
    "anchor": ["anchor", "safe port", "safe anchor"],
}

@dataclass
class CerebroConfig:
    cerebro_root: str
    glossary: dict[str, list[str]] = field(default_factory=lambda: dict(DEFAULT_GLOSSARY))
    max_summary_chars: int = 1400
    max_quote_chars: int = 700

# ---------------------------------------------------------------------------
# Concept extraction
# ---------------------------------------------------------------------------

def extract_headings(text: str) -> list[str]:
    headings: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            title = stripped.lstrip("#").strip()
            if title:
                headings.append(title)
    return headings

def extract_glossary_concepts(text: str, glossary: dict[str, list[str]]) -> list[str]:
    lowered = text.lower()
    found: list[str] = []

    for concept, aliases in glossary.items():
        for alias in aliases:
            if alias.lower() in lowered:
                found.append(concept)
                break

    return sorted(set(found))

def extract_candidate_concepts(text: str, glossary: dict[str, list[str]]) -> list[str]:
    concepts = set(extract_glossary_concepts(text, glossary))

    # Headings are treated as weak concepts.
    for heading in extract_headings(text):
        slug = safe_slug(heading)
        if 3 <= len(slug) <= 80:
            concepts.add(slug)

    return sorted(concepts)

def extract_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            title = stripped.lstrip("#").strip()
            if title:
                return title[:160]
    return fallback[:160]

def extract_summary(text: str, max_chars: int) -> str:
    """Deterministic extractive summary.

    This is not an LLM summary. It simply preserves the first meaningful
    paragraphs so no semantic claim is invented.
    """
    paragraphs = [
        p.strip()
        for p in re.split(r"\n\s*\n", text)
        if p.strip()
    ]

    out = ""
    for p in paragraphs:
        candidate = (out + "\n\n" + p).strip() if out else p
        if len(candidate) > max_chars:
            break
        out = candidate

    return out or text[:max_chars].strip()

def extract_quote(text: str, max_chars: int) -> str:
    summary = extract_summary(text, max_chars)
    return summary.replace("```", "'''").strip()

# ---------------------------------------------------------------------------
# Fold state
# ---------------------------------------------------------------------------

def classify_fold_state(concepts: list[str], text: str, manifest: dict) -> str:
    """Cheap deterministic fold-state classifier.

    Mini-LLMs can improve this later. For v0, keep it boring.
    """
    if not manifest.get("projection_ready"):
        return "raw"

    if not text.strip():
        return "mirrored"

    if len(concepts) == 0:
        return "normalized"

    if len(concepts) < 3:
        return "indexed"

    if len(concepts) < 7:
        return "folding"

    return "projectable"

# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------

@dataclass
class CerebroIndexResult:
    source_record_id: str
    cerebro_source_id: str
    source_card_path: str
    summary_path: str
    concepts: list[str]
    concept_paths: list[str]
    graph_path: str
    source_index_path: str
    fold_state: str
    projection_ready: bool
    next_actions: list[str]

    def to_dict(self) -> dict:
        return asdict(self)

# ---------------------------------------------------------------------------
# Cerebro Indexer
# ---------------------------------------------------------------------------

class CerebroIndexError(Exception):
    pass

class CerebroIndexer:
    def __init__(
        self,
        config: CerebroConfig,
        receipts: Optional[ReceiptSink] = None,
    ):
        self.config = config
        self.receipts = receipts or NullReceipts()

    def index_flux_manifest(
        self,
        manifest_path: str,
        actor: str = "cerebro_indexer",
    ) -> CerebroIndexResult:
        manifest = self._load_manifest(manifest_path)

        if manifest.get("kind") != "flux.manifest.v0":
            raise CerebroIndexError(f"wrong_manifest_kind:{manifest.get('kind')}")

        self.receipts.emit(
            "cerebro.index_started",
            {
                "manifest_path": manifest_path,
                "flux_id": manifest.get("flux_id"),
                "source_record_id": manifest.get("source_record_id"),
            },
            actor=actor,
        )

        text = self._read_normalized_text(manifest)
        source_record_id = manifest["source_record_id"]
        source_slug = safe_slug(source_record_id)

        title = extract_title(text, fallback=manifest.get("record", {}).get("this", source_record_id))
        concepts = extract_candidate_concepts(text, self.config.glossary)
        fold_state = classify_fold_state(concepts, text, manifest)

        cerebro_source_id = content_hash(
            {
                "source_record_id": source_record_id,
                "flux_id": manifest.get("flux_id"),
                "combined_hash": manifest.get("combined_hash"),
                "concepts": concepts,
                "fold_state": fold_state,
            },
            "csrc:",
        )

        source_card_path = os.path.join(
            self.config.cerebro_root,
            "10_sources",
            f"{source_slug}.md",
        )

        summary_path = os.path.join(
            self.config.cerebro_root,
            "20_source_summaries",
            f"{source_slug}.md",
        )

        source_index_path = os.path.join(
            self.config.cerebro_root,
            "00_index",
            "source_index.ndjson",
        )

        graph_path = os.path.join(
            self.config.cerebro_root,
            "00_index",
            "graph.json",
        )

        source_card = self._render_source_card(
            manifest=manifest,
            title=title,
            text=text,
            concepts=concepts,
            fold_state=fold_state,
            cerebro_source_id=cerebro_source_id,
        )
        write_text(source_card_path, source_card)

        summary = self._render_summary_card(
            manifest=manifest,
            title=title,
            text=text,
            concepts=concepts,
            fold_state=fold_state,
            cerebro_source_id=cerebro_source_id,
        )
        write_text(summary_path, summary)

        concept_paths = []
        for concept in concepts:
            concept_path = self._upsert_concept_page(
                concept=concept,
                source_record_id=source_record_id,
                cerebro_source_id=cerebro_source_id,
                title=title,
                source_card_path=source_card_path,
                fold_state=fold_state,
            )
            concept_paths.append(concept_path)

        index_entry = {
            "kind": "cerebro.source_index.v0",
            "cerebro_source_id": cerebro_source_id,
            "source_record_id": source_record_id,
            "flux_id": manifest.get("flux_id"),
            "title": title,
            "fold_state": fold_state,
            "projection_ready": manifest.get("projection_ready", False),
            "concepts": concepts,
            "source_card_path": source_card_path,
            "summary_path": summary_path,
            "indexed_at": utc_now(),
        }
        append_ndjson(source_index_path, index_entry)

        graph = self._build_or_update_graph(
            graph_path=graph_path,
            source=index_entry,
            concepts=concepts,
        )
        write_json(graph_path, graph)

        result = CerebroIndexResult(
            source_record_id=source_record_id,
            cerebro_source_id=cerebro_source_id,
            source_card_path=source_card_path,
            summary_path=summary_path,
            concepts=concepts,
            concept_paths=concept_paths,
            graph_path=graph_path,
            source_index_path=source_index_path,
            fold_state=fold_state,
            projection_ready=manifest.get("projection_ready", False),
            next_actions=self._next_actions(fold_state),
        )

        self.receipts.emit(
            "cerebro.index_completed",
            result.to_dict(),
            actor=actor,
        )

        return result

    def _load_manifest(self, manifest_path: str) -> dict:
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _read_normalized_text(self, manifest: dict) -> str:
        normalized = manifest.get("normalized", {})
        path = normalized.get("path")

        if not path or not os.path.exists(path):
            return ""

        return read_text(path)

    def _render_frontmatter(self, data: dict) -> str:
        lines = ["---"]
        for key, value in data.items():
            if isinstance(value, list):
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {json.dumps(item, ensure_ascii=False)}")
            elif isinstance(value, bool):
                lines.append(f"{key}: {str(value).lower()}")
            else:
                lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
        lines.append("---")
        return "\n".join(lines)

    def _render_source_card(
        self,
        manifest: dict,
        title: str,
        text: str,
        concepts: list[str],
        fold_state: str,
        cerebro_source_id: str,
    ) -> str:
        frontmatter = self._render_frontmatter({
            "kind": "cerebro_source",
            "cerebro_source_id": cerebro_source_id,
            "source_record_id": manifest["source_record_id"],
            "flux_id": manifest.get("flux_id"),
            "combined_hash": manifest.get("combined_hash"),
            "fold_state": fold_state,
            "projection_ready": manifest.get("projection_ready", False),
            "concepts": concepts,
            "status": "indexed",
        })

        return "\n".join([
            frontmatter,
            "",
            f"# {title}",
            "",
            "## Source identity",
            "",
            f"- Source record: `{manifest['source_record_id']}`",
            f"- Flux: `{manifest.get('flux_id')}`",
            f"- Combined hash: `{manifest.get('combined_hash')}`",
            f"- Fold state: `{fold_state}`",
            "",
            "## Concepts",
            "",
            *[f"- [[{concept}]]" for concept in concepts],
            "",
            "## Custody",
            "",
            f"- Custody root: `{manifest.get('custody_root')}`",
            f"- Normalized path: `{manifest.get('normalized', {}).get('path')}`",
            "",
            "## Origin",
            "",
            "```json",
            json.dumps(manifest.get("origin", {}), ensure_ascii=False, indent=2, sort_keys=True),
            "```",
            "",
            "## Extracted source text",
            "",
            "```text",
            text[:8000].replace("```", "'''"),
            "```",
            "",
        ])

    def _render_summary_card(
        self,
        manifest: dict,
        title: str,
        text: str,
        concepts: list[str],
        fold_state: str,
        cerebro_source_id: str,
    ) -> str:
        summary = extract_summary(text, self.config.max_summary_chars)
        quote = extract_quote(text, self.config.max_quote_chars)

        frontmatter = self._render_frontmatter({
            "kind": "cerebro_source_summary",
            "cerebro_source_id": cerebro_source_id,
            "source_record_id": manifest["source_record_id"],
            "fold_state": fold_state,
            "status": "extractive_summary",
            "concepts": concepts,
        })

        return "\n".join([
            frontmatter,
            "",
            f"# Summary — {title}",
            "",
            "> This is a deterministic extractive summary. It is not canon.",
            "",
            "## Summary",
            "",
            summary or "_No normalized text available._",
            "",
            "## Representative excerpt",
            "",
            "```text",
            quote or "No excerpt available.",
            "```",
            "",
            "## Concepts",
            "",
            *[f"- [[{concept}]]" for concept in concepts],
            "",
        ])

    def _upsert_concept_page(
        self,
        concept: str,
        source_record_id: str,
        cerebro_source_id: str,
        title: str,
        source_card_path: str,
        fold_state: str,
    ) -> str:
        slug = safe_slug(concept)
        path = os.path.join(
            self.config.cerebro_root,
            "30_concepts",
            f"{slug}.md",
        )

        link_line = (
            f"- `{source_record_id}` — {title} — "
            f"fold_state=`{fold_state}` — source=`{source_card_path}`"
        )

        if not os.path.exists(path):
            frontmatter = self._render_frontmatter({
                "kind": "cerebro_concept",
                "concept": concept,
                "concept_id": content_hash({"concept": concept}, "concept:"),
                "status": "emerging",
            })

            write_text(path, "\n".join([
                frontmatter,
                "",
                f"# {concept}",
                "",
                "## Meaning",
                "",
                "_Emerging concept. Meaning must be stabilized by projections and review._",
                "",
                "## Sources",
                "",
                link_line,
                "",
            ]))
            return path

        existing = read_text(path)
        if source_record_id not in existing:
            append_text(path, link_line + "\n")

        return path

    def _build_or_update_graph(
        self,
        graph_path: str,
        source: dict,
        concepts: list[str],
    ) -> dict:
        if os.path.exists(graph_path):
            with open(graph_path, "r", encoding="utf-8") as f:
                graph = json.load(f)
        else:
            graph = {
                "kind": "cerebro.graph.v0",
                "nodes": {},
                "edges": [],
                "updated_at": "",
            }

        source_node_id = source["cerebro_source_id"]

        graph["nodes"][source_node_id] = {
            "id": source_node_id,
            "type": "source",
            "label": source["title"],
            "source_record_id": source["source_record_id"],
            "fold_state": source["fold_state"],
        }

        for concept in concepts:
            concept_node_id = content_hash({"concept": concept}, "concept:")
            graph["nodes"][concept_node_id] = {
                "id": concept_node_id,
                "type": "concept",
                "label": concept,
            }

            edge = {
                "from": source_node_id,
                "to": concept_node_id,
                "type": "mentions",
            }

            if edge not in graph["edges"]:
                graph["edges"].append(edge)

        graph["updated_at"] = utc_now()
        return graph

    def _next_actions(self, fold_state: str) -> list[str]:
        if fold_state in {"projectable", "folding"}:
            return [
                "build_dynamic_projection",
                "mini_llm_concept_review",
                "detect_supersession",
                "score_projection_readiness",
            ]

        if fold_state == "indexed":
            return [
                "await_more_sources",
                "mini_llm_link_review",
                "human_review_if_canon_like",
            ]

        return [
            "improve_normalization",
            "manual_review",
            "do_not_seal",
        ]
