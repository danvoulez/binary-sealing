"""logline flux <sub> commands."""

import argparse
import json
import os

from logline_kernel.core.receipts import NullReceipts
from logline_kernel.engines.flux.engine import FluxEngine, LocalFixtureExporter
from logline_kernel.processes.ledger import ProcessLedger


def handle_run(args: argparse.Namespace) -> int:
    ledger = ProcessLedger(path=os.path.join(args.nas_root, "process_ledger.ndjson"), receipts=NullReceipts())
    entries = list(ledger.entries())
    if not entries:
        print("error: no process entries found", file=argparse._sys.stderr)
        return 1

    entry = entries[-1]
    engine = FluxEngine(
        nas_root=args.nas_root,
        exporter=LocalFixtureExporter(),
        receipts=NullReceipts(),
    )
    result = engine.run_entry(entry, actor=args.actor)
    print(json.dumps({"manifest_path": result.manifest_path, "source_record_id": result.source_record_id}, indent=2))
    return 0


def register(sub: argparse._SubParsersAction) -> None:
    parser = sub.add_parser("flux", help="Flux engine commands")
    flux_sub = parser.add_subparsers(dest="flux_command", required=True)

    p = flux_sub.add_parser("run", help="Run flux custody on the latest ledger entry")
    p.add_argument("--nas-root", required=True)
    p.add_argument("--actor", default="op:cli")
    p.set_defaults(func=handle_run)
