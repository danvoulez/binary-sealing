"""logline cerebro <sub> commands."""

import argparse
import json
import os

from logline_kernel.core.receipts import NullReceipts
from logline_kernel.engines.cerebro.indexer import CerebroConfig, CerebroIndexer


def handle_index(args: argparse.Namespace) -> int:
    manifest_path = args.manifest_path
    if not manifest_path:
        flux_dir = os.path.join(args.nas_root, "Minivault", "flux", "00_raw_google_docs")
        if not os.path.exists(flux_dir):
            print("error: no flux manifest found", file=argparse._sys.stderr)
            return 1
        # Find the deepest manifest.json under flux_dir.
        candidates = []
        for root, _dirs, files in os.walk(flux_dir):
            if "manifest.json" in files:
                candidates.append(os.path.join(root, "manifest.json"))
        if not candidates:
            print("error: no manifest.json found", file=argparse._sys.stderr)
            return 1
        manifest_path = sorted(candidates)[-1]

    cerebro_root = os.path.join(args.nas_root, "Cerebro")
    indexer = CerebroIndexer(CerebroConfig(cerebro_root=cerebro_root), receipts=NullReceipts())
    result = indexer.index_flux_manifest(manifest_path=manifest_path, actor=args.actor)
    print(json.dumps({"cerebro_source_id": result.cerebro_source_id, "fold_state": result.fold_state}, indent=2))
    return 0


def register(sub: argparse._SubParsersAction) -> None:
    parser = sub.add_parser("cerebro", help="Cerebro commands")
    cerebro_sub = parser.add_subparsers(dest="cerebro_command", required=True)

    p = cerebro_sub.add_parser("index", help="Index the latest flux manifest")
    p.add_argument("--nas-root", required=True)
    p.add_argument("--manifest-path")
    p.add_argument("--actor", default="op:cli")
    p.set_defaults(func=handle_index)
