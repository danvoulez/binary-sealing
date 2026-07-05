"""logline CLI entry point."""

import argparse
import sys

from logline_kernel.cli import (
    anchor_cmd,
    cerebro_cmd,
    diamond_cmd,
    flux_cmd,
    process_cmd,
    projection_cmd,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="logline", description="LogLine Projection Kernel CLI")
    sub = parser.add_subparsers(dest="command", help="Engine commands")

    process_cmd.register(sub)
    flux_cmd.register(sub)
    cerebro_cmd.register(sub)
    projection_cmd.register(sub)
    anchor_cmd.register(sub)
    diamond_cmd.register(sub)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 1

    if not hasattr(args, "func"):
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
