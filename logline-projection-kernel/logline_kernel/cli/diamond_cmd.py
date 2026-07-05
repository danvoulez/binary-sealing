"""logline diamond <sub> commands."""

import argparse
import json
import os

from logline_kernel.core.receipts import NullReceipts
from logline_kernel.diamonds.manifest.builder import DiamondManifestBuilder
from logline_kernel.diamonds.resolution.resolver import DiamondResolveRequest, DiamondResolver
from logline_kernel.diamonds.sealability.tester import (
    SealabilityConfig,
    SealabilityTester,
    DOUBT_SEVERITY,
)
from logline_kernel.diamonds.sealing.sealer import DiamondSealer, HashOnlySigner, SealingAuthority


def _last_projection_path(nas_root: str) -> str:
    active_dir = os.path.join(nas_root, "Cerebro", "60_projections", "active")
    if not os.path.exists(active_dir):
        raise FileNotFoundError("no projections")
    candidates = []
    for root, _dirs, files in os.walk(active_dir):
        if "projection.json" in files:
            candidates.append(os.path.join(root, "projection.json"))
    if not candidates:
        raise FileNotFoundError("no projection.json")
    return sorted(candidates)[-1]


def _last_sealability_report_path(nas_root: str) -> str:
    seal_dir = os.path.join(nas_root, "Cerebro", "60_projections", "sealability")
    if not os.path.exists(seal_dir):
        raise FileNotFoundError("no sealability reports")
    candidates = []
    for root, _dirs, files in os.walk(seal_dir):
        for f in files:
            if f.endswith("sealability_report.json"):
                candidates.append(os.path.join(root, f))
    if not candidates:
        raise FileNotFoundError("no sealability report")
    return sorted(candidates)[-1]


def _default_context(nas_root: str) -> dict:
    return {
        "rights": {"attached": True, "license": "internal", "constraints": []},
        "scorecard": {"exists": True, "trust_score": 0.82, "method": "manual_v0"},
        "custody_policy": {"exists": True, "vault": "nas:minivault", "path": os.path.join(nas_root, "Minivault")},
        "revocation": {"exists": True, "method": "supersede_or_revoke_manifest"},
        "receipts": {"configured": True, "kinds": ["diamond.candidate", "diamond.sealed", "diamond.revoked"]},
        "human_review": {"approved": True, "reviewed_by": "dan", "receipt": "receipt:manual-review-placeholder"},
    }


def handle_sealability_test(args: argparse.Namespace) -> int:
    cerebro_root = os.path.join(args.nas_root, "Cerebro")
    projection_path = args.projection_path or _last_projection_path(args.nas_root)
    tester = SealabilityTester(
        cerebro_root=cerebro_root,
        receipts=NullReceipts(),
        config=SealabilityConfig(
            min_sources=1,
            max_allowed_doubt_severity=DOUBT_SEVERITY["inferred"],
            require_human_review=True,
        ),
    )
    result = tester.test_projection(
        projection_path=projection_path,
        context=_default_context(args.nas_root),
        actor=args.actor,
    )
    print(json.dumps({"report_path": result.report_path, "sealable": result.sealable}, indent=2))
    return 0


def handle_candidate_build(args: argparse.Namespace) -> int:
    projection_path = args.projection_path or _last_projection_path(args.nas_root)
    report_path = args.sealability_report_path or _last_sealability_report_path(args.nas_root)
    builder = DiamondManifestBuilder(nas_root=args.nas_root, receipts=NullReceipts())
    result = builder.build_candidate(
        projection_path=projection_path,
        sealability_report_path=report_path,
        sealability_context=_default_context(args.nas_root),
        diamond_kind="D.PROJ",
        title=args.title,
        purpose=args.purpose,
        created_by=args.actor,
    )
    print(json.dumps({"manifest_path": result.manifest_path, "diamond_candidate_id": result.diamond_candidate_id}, indent=2))
    return 0


def handle_seal(args: argparse.Namespace) -> int:
    manifest_path = args.candidate_manifest_path or _last_candidate_manifest(args.nas_root)
    sealer = DiamondSealer(nas_root=args.nas_root, receipts=NullReceipts(), signer=HashOnlySigner())
    authority = SealingAuthority(
        authority_id="dan",
        name="Daniel Amarilho",
        role="Sealing authority",
        allowed_diamond_kinds=["D.PROJ"],
    )
    result = sealer.seal_candidate(
        candidate_manifest_path=manifest_path,
        authority=authority,
        actor=args.actor,
        seal_note=args.note,
    )
    print(json.dumps({"diamond_id": result.diamond_id, "sealed_manifest_path": result.sealed_manifest_path}, indent=2))
    return 0


def _last_candidate_manifest(nas_root: str) -> str:
    cand_dir = os.path.join(nas_root, "Minivault", "30_diamonds", "candidates")
    if not os.path.exists(cand_dir):
        raise FileNotFoundError("no candidates")
    candidates = []
    for root, _dirs, files in os.walk(cand_dir):
        if "diamond_manifest.json" in files:
            candidates.append(os.path.join(root, "diamond_manifest.json"))
    if not candidates:
        raise FileNotFoundError("no candidate manifest")
    return sorted(candidates)[-1]


def handle_resolve(args: argparse.Namespace) -> int:
    resolver = DiamondResolver(nas_root=args.nas_root, receipts=NullReceipts())
    request = DiamondResolveRequest(
        actor=args.actor,
        task=args.task,
        purpose=args.purpose,
        query_concepts=args.concepts,
        intended_access_mode=args.mode,
        max_doubt_severity=args.max_doubt_severity,
    )
    result = resolver.resolve(request)
    print(json.dumps({
        "resolution_state": result.resolution_state,
        "selected_diamond_id": result.selected_diamond_id,
        "resolution_path": result.resolution_path,
    }, indent=2))
    return 0


def register(sub: argparse._SubParsersAction) -> None:
    parser = sub.add_parser("diamond", help="Diamond commands")
    diamond_sub = parser.add_subparsers(dest="diamond_command", required=True)

    p = diamond_sub.add_parser("sealability", help="Diamond sealability")
    p.add_argument("sub", choices=["test"], default="test", nargs="?")
    p.add_argument("--nas-root", required=True)
    p.add_argument("--projection-path")
    p.add_argument("--actor", default="op:cli")
    p.set_defaults(func=handle_sealability_test)

    p = diamond_sub.add_parser("candidate", help="Diamond candidate")
    p.add_argument("sub", choices=["build"], default="build", nargs="?")
    p.add_argument("--nas-root", required=True)
    p.add_argument("--projection-path")
    p.add_argument("--sealability-report-path")
    p.add_argument("--title", default="CLI Diamond")
    p.add_argument("--purpose", default="CLI-built diamond")
    p.add_argument("--actor", default="op:cli")
    p.set_defaults(func=handle_candidate_build)

    p = diamond_sub.add_parser("seal", help="Seal a diamond candidate")
    p.add_argument("--nas-root", required=True)
    p.add_argument("--candidate-manifest-path")
    p.add_argument("--note", default="CLI seal")
    p.add_argument("--actor", default="op:cli")
    p.set_defaults(func=handle_seal)

    p = diamond_sub.add_parser("resolve", help="Resolve the current diamond")
    p.add_argument("--nas-root", required=True)
    p.add_argument("--task", default="Explain LogLine")
    p.add_argument("--purpose", default="Grounding")
    p.add_argument("--concepts", nargs="+", default=["logline", "diamond", "cerebro", "flux"])
    p.add_argument("--mode", default="anchor")
    p.add_argument("--max-doubt-severity", type=int, default=DOUBT_SEVERITY["missing"])
    p.add_argument("--actor", default="op:cli")
    p.set_defaults(func=handle_resolve)
