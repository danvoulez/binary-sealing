"""Example: register a flux act into the process ledger."""

import os
import sys
import tempfile

# Allow running examples without installing the package.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from logline_kernel.acts.act import Act
from logline_kernel.core.receipts import NullReceipts
from logline_kernel.processes.contract import ProcessContract, SlotRule
from logline_kernel.processes.ledger import ProcessLedger


def main():
    nas_root = tempfile.mkdtemp(prefix="logline_nas_")
    fixture_path = os.path.join(nas_root, "fixture", "projection-kernel-pack.txt")
    os.makedirs(os.path.dirname(fixture_path), exist_ok=True)
    with open(fixture_path, "w", encoding="utf-8") as f:
        f.write("LogLine Projection Kernel Pack\nSample source document for flux.\n")

    act = Act(
        who="op:lab-512",
        did="observed",
        this="gdoc:projection-kernel-pack@rev42",
        when="2026-07-02T12:00:00Z",
        confirmed_by="drive-revision:42",
        if_ok="source becomes projection-ready",
        if_doubt="quarantine and review",
        if_not="reject and emit receipt",
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

    ledger = ProcessLedger(
        path=os.path.join(nas_root, "process_ledger.ndjson"),
        receipts=NullReceipts(),
    )

    record = ledger.register(act, contract, registered_by="op:lab-512")
    print("registered", record["process_record_id"])
    print("contract_hash", record["contract_hash"])
    print("light", record["light"])
    print("nas_root", nas_root)


if __name__ == "__main__":
    main()
