"""Example: find a safe anchor for a lost agent."""

import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from logline_kernel.acts.act import Act
from logline_kernel.core.receipts import NullReceipts
from logline_kernel.engines.anchor.finder import AnchorFinder, AnchorRequest
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
        purpose="Bounded view over the LogLine product spine.",
        include_any_concepts=["dynamic_projection", "projection_kernel", "diamond", "cerebro", "flux", "operator_mesh"],
        allowed_fold_states=["indexed", "folding", "projectable", "stable", "sealable"],
        require_projection_ready=True,
        min_sources=1,
        max_sources=25,
        review_required=True,
    )
    builder.build(lens=lens, actor="op:lab-512", scope={"project": "logline_projection_kernel"})

    finder = AnchorFinder(cerebro_root=cerebro_root, receipts=NullReceipts())
    request = AnchorRequest(
        actor="op:cloud",
        task="Explain the LogLine product spine without drifting.",
        purpose="Find a safe anchor for reasoning about the Projection Kernel.",
        query_concepts=["projection_kernel", "dynamic_projection", "flux", "cerebro", "diamond"],
        max_doubt_severity=4,
    )
    result = finder.find(request)

    print("anchor_state", result.anchor_state)
    print("anchor_path", result.anchor_path)
    print("selected_anchor_id", result.selected_anchor_id)
    print("alternative_count", result.alternative_count)
    print("nas_root", nas_root)


if __name__ == "__main__":
    main()
