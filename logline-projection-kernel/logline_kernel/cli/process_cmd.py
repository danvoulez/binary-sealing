"""logline process <sub> commands."""

import argparse
import json
import os
import tempfile

from logline_kernel.acts.act import Act
from logline_kernel.core.receipts import NullReceipts
from logline_kernel.processes.contract import ProcessContract, SlotRule
from logline_kernel.processes.ledger import ProcessLedger


def handle_register(args: argparse.Namespace) -> int:
    nas_root = args.nas_root or tempfile.mkdtemp(prefix="logline_nas_")
    fixture_path = args.fixture or os.path.join(nas_root, "fixture", "source.txt")
    os.makedirs(os.path.dirname(fixture_path), exist_ok=True)
    if not os.path.exists(fixture_path):
        with open(fixture_path, "w", encoding="utf-8") as f:
            f.write("# LogLine Source\n\nSample source text.\n")

    act = Act(
        who=args.actor,
        did=args.did,
        this=args.this,
        when=args.when,
        confirmed_by=args.confirmed_by,
        status="registered",
        aux={"origin": {"local_path": fixture_path}, "process_id": args.process_id},
    )

    contract = ProcessContract(
        process_id=args.process_id,
        version="0.1.0",
        title=f"Process {args.process_id}",
        colour=args.colour,
        engine=args.engine,
        lens_id=args.lens_id,
        slot_rules={
            "confirmed_by": SlotRule(meaning="revision identifier", required=True),
        } if args.confirmed_by else {},
        allowed_statuses={"registered", "qualified", "projectable"},
        required_aux=["origin"] if args.fixture else [],
        effects_allowed=True,
    )

    ledger_path = os.path.join(nas_root, "process_ledger.ndjson")
    ledger = ProcessLedger(path=ledger_path, receipts=NullReceipts())
    record = ledger.register(act, contract, registered_by=args.actor)
    print(json.dumps({"process_record_id": record["process_record_id"], "nas_root": nas_root}, indent=2))
    return 0


def register(sub: argparse._SubParsersAction) -> None:
    parser = sub.add_parser("process", help="Process commands")
    proc_sub = parser.add_subparsers(dest="process_command", required=True)

    p = proc_sub.add_parser("register", help="Register an Act into the process ledger")
    p.add_argument("--actor", default="op:cli")
    p.add_argument("--did", default="observed")
    p.add_argument("--this", default="gdoc:cli-source@1")
    p.add_argument("--when", default="2026-07-02T12:00:00Z")
    p.add_argument("--confirmed-by", default="cli")
    p.add_argument("--process-id", default="flux.google_doc.v0")
    p.add_argument("--colour", default="blue")
    p.add_argument("--engine", default="flux_engine")
    p.add_argument("--lens-id", default="flux.google_doc.v0")
    p.add_argument("--fixture")
    p.add_argument("--nas-root")
    p.set_defaults(func=handle_register)
