"""logline projection <sub> commands."""

import argparse
import json
import os

from logline_kernel.core.receipts import NullReceipts
from logline_kernel.engines.projection.builder import ProjectionBuilder, ProjectionLens


def handle_build(args: argparse.Namespace) -> int:
    cerebro_root = os.path.join(args.nas_root, "Cerebro")
    builder = ProjectionBuilder(cerebro_root=cerebro_root, receipts=NullReceipts())
    lens = ProjectionLens(
        lens_id=args.lens_id,
        title=args.title,
        purpose=args.purpose,
        include_any_concepts=args.concepts,
        allowed_fold_states=["indexed", "folding", "projectable", "stable", "sealable"],
        require_projection_ready=True,
        min_sources=1,
        max_sources=25,
        review_required=True,
    )
    result = builder.build(
        lens=lens,
        actor=args.actor,
        scope={"project": args.project},
    )
    print(json.dumps({"projection_path": result.projection_path, "projection_hash": result.projection_hash}, indent=2))
    return 0


def register(sub: argparse._SubParsersAction) -> None:
    parser = sub.add_parser("projection", help="Projection commands")
    proj_sub = parser.add_subparsers(dest="projection_command", required=True)

    p = proj_sub.add_parser("build", help="Build a projection from Cerebro sources")
    p.add_argument("--nas-root", required=True)
    p.add_argument("--actor", default="op:cli")
    p.add_argument("--lens-id", default="cli.lens.v1")
    p.add_argument("--title", default="CLI Projection")
    p.add_argument("--purpose", default="CLI-built projection")
    p.add_argument("--project", default="logline_cli")
    p.add_argument("--concepts", nargs="+", default=["logline", "diamond", "cerebro", "flux"])
    p.set_defaults(func=handle_build)
