"""Example: index a flux manifest into Cerebro."""

import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from logline_kernel.acts.act import Act
from logline_kernel.core.receipts import NullReceipts
from logline_kernel.engines.cerebro.indexer import CerebroConfig, CerebroIndexer
from logline_kernel.engines.flux.engine import FluxEngine, LocalFixtureExporter
from logline_kernel.processes.contract import ProcessContract, SlotRule
from logline_kernel.processes.ledger import ProcessLedger


def main():
    nas_root = tempfile.mkdtemp(prefix="logline_nas_")
    fixture_path = os.path.join(nas_root, "fixture", "projection-kernel-pack.txt")
    os.makedirs(os.path.dirname(fixture_path), exist_ok=True)
    with open(fixture_path, "w", encoding="utf-8") as f:
        f.write("# LogLine Projection Kernel Pack\n\n")
        f.write("This document describes the LogLine Projection Kernel, ")
        f.write("Cerebro, Flux, and Diamond lifecycle.\n")

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

    engine = FluxEngine(
        nas_root=nas_root,
        exporter=LocalFixtureExporter(),
        receipts=NullReceipts(),
    )
    flux_result = engine.run_entry(entry, actor="op:lab-512")

    indexer = CerebroIndexer(
        CerebroConfig(cerebro_root=os.path.join(nas_root, "Cerebro")),
        receipts=NullReceipts(),
    )
    result = indexer.index_flux_manifest(
        manifest_path=flux_result.manifest_path,
        actor="op:lab-8gb",
    )

    print("source_record_id", result.source_record_id)
    print("cerebro_source_id", result.cerebro_source_id)
    print("fold_state", result.fold_state)
    print("concepts", result.concepts)
    print("nas_root", nas_root)


if __name__ == "__main__":
    main()
