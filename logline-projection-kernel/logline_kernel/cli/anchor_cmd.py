"""logline anchor <sub> commands."""

import argparse
import json
import os

from logline_kernel.core.receipts import NullReceipts
from logline_kernel.engines.anchor.finder import AnchorFinder, AnchorRequest


def handle_find(args: argparse.Namespace) -> int:
    cerebro_root = os.path.join(args.nas_root, "Cerebro")
    finder = AnchorFinder(cerebro_root=cerebro_root, receipts=NullReceipts())
    request = AnchorRequest(
        actor=args.actor,
        task=args.task,
        purpose=args.purpose,
        query_concepts=args.concepts,
        max_doubt_severity=args.max_doubt_severity,
    )
    result = finder.find(request)
    print(json.dumps({
        "anchor_state": result.anchor_state,
        "anchor_path": result.anchor_path,
        "selected_anchor_id": result.selected_anchor_id,
    }, indent=2))
    return 0


def register(sub: argparse._SubParsersAction) -> None:
    parser = sub.add_parser("anchor", help="Anchor commands")
    anchor_sub = parser.add_subparsers(dest="anchor_command", required=True)

    p = anchor_sub.add_parser("find", help="Find a safe anchor")
    p.add_argument("--nas-root", required=True)
    p.add_argument("--actor", default="op:cli")
    p.add_argument("--task", default="Explain LogLine")
    p.add_argument("--purpose", default="Agent grounding")
    p.add_argument("--concepts", nargs="+", default=["logline", "diamond", "cerebro", "flux"])
    p.add_argument("--max-doubt-severity", type=int, default=4)
    p.set_defaults(func=handle_find)
