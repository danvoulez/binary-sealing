"""Example: build a projection from indexed Cerebro sources."""

import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from logline_kernel.acts.act import Act
from logline_kernel.core.receipts import NullReceipts
from logline_kernel.engines.cerebro.indexer import CerebroConfig, CerebroIndexer
from logline_kernel.engines.flux.engine import FluxEngine, LocalFixtureExporter
from logline_kernel.engines.projection.builder import ProjectionBuilder, ProjectionLens
from logline_kernel.processes.contract import ProcessContract, SlotRule
from logline_kernel.processes.ledger import ProcessLedger


def main():
    nas_root = tempfile.mkdtemp(prefix="logline_nas_")
    fixture_path = os.path.join(nas_root, "fixture", "projection-kernel-pack.txt")
    os.makedirs(os.path.dirname(fixture_path), exist_ok=True)
    with open(fixture_path, "w", encoding="utf-8") as f:
        f.write("# LogLine Projection Kernel Pack\n\n")
        f.write("This document describes the LogLine Projection Kernel, ")
        f.write("Cerebro, Flux, Diamond, and operator mesh.\n")

    act = Act(
        who="op:lab-512",
        did="observed",
        this="gdoc:projection-kernel-pack@rev42",
        when="2026-07-02T12:00:00Z",
        confirmed_by="drive-revision:42",
        status="registered",
        aux={
            "origin": {"local_path": fixture_path},
            "process_id": "flux.google_doc.v0",
        },
    )

    contract = ProcessContract(
        process_id="flux.google_doc.v0",
        version="0.1.0",
        title="Flux Google Doc custody",
        colour="blue",
        engine="flux_engine",
        lens_id="flux.google_doc.v0",
        slot_rules={
            "confirmed_by": SlotRule(meaning="revision identifier", required=True),
        },
        allowed_statuses={"registered", "qualified", "projectable"},
        required_aux=["origin"],
        effects_allowed=True,
    )

    ledger_path = os.path.join(nas_root, "process_ledger.ndjson")
    ledger = ProcessLedger(path=ledger_path, receipts=NullReceipts())
    entry = ledger.register(act, contract, registered_by="op:lab-512")

    flux = FluxEngine(nas_root=nas_root, exporter=LocalFixtureExporter(), receipts=NullReceipts())
    flux_result = flux.run_entry(entry, actor="op:lab-512")

    cerebro_root = os.path.join(nas_root, "Cerebro")
    indexer = CerebroIndexer(CerebroConfig(cerebro_root=cerebro_root), receipts=NullReceipts())
    indexer.index_flux_manifest(manifest_path=flux_result.manifest_path, actor="op:lab-8gb")

    builder = ProjectionBuilder(cerebro_root=cerebro_root, receipts=NullReceipts())
    lens = ProjectionLens(
        lens_id="kernel.product_spine.v1",
        title="LogLine Projection Kernel Product Spine",
        purpose="Build a bounded view over sources related to the Projection Kernel, Diamonds, Cerebro, Flux, and Operator Mesh.",
        include_any_concepts=["dynamic_projection", "projection_kernel", "diamond", "cerebro", "flux", "operator_mesh"],
        allowed_fold_states=["indexed", "folding", "projectable", "stable", "sealable"],
        require_projection_ready=True,
        min_sources=1,
        max_sources=25,
        review_required=True,
    )

    result = builder.build(
        lens=lens,
        actor="op:lab-512",
        scope={
            "project": "logline_projection_kernel",
            "concepts": ["dynamic_projection", "diamond", "cerebro", "flux", "operator_mesh"],
        },
    )

    print("projection_path", result.projection_path)
    print("projection_hash", result.projection_hash)
    print("source_boundary_hash", result.source_boundary_hash)
    print("included_count", result.included_count)
    print("nas_root", nas_root)


if __name__ == "__main__":
    main()
