"""Example: build a Diamond candidate from a sealable projection."""

import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from logline_kernel.acts.act import Act
from logline_kernel.core.receipts import NullReceipts
from logline_kernel.diamonds.manifest.builder import DiamondManifestBuilder
from logline_kernel.diamonds.sealability.tester import (
    SealabilityConfig,
    SealabilityTester,
    DOUBT_SEVERITY,
)
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
    projection_result = builder.build(
        lens=lens,
        actor="op:lab-512",
        scope={"project": "logline_projection_kernel"},
    )

    tester = SealabilityTester(
        cerebro_root=cerebro_root,
        receipts=NullReceipts(),
        config=SealabilityConfig(
            min_sources=1,
            max_allowed_doubt_severity=DOUBT_SEVERITY["inferred"],
            require_human_review=True,
        ),
    )

    context = {
        "rights": {
            "attached": True,
            "license": "internal",
            "constraints": ["no_public_export_without_approval"],
        },
        "scorecard": {"exists": True, "trust_score": 0.82, "method": "manual_v0"},
        "custody_policy": {"exists": True, "vault": "nas:minivault", "path": os.path.join(nas_root, "Minivault")},
        "revocation": {"exists": True, "method": "supersede_or_revoke_manifest"},
        "receipts": {"configured": True, "kinds": ["diamond.candidate", "diamond.sealed", "diamond.revoked"]},
        "human_review": {"approved": True, "reviewed_by": "dan", "receipt": "receipt:manual-review-placeholder"},
    }
    sealability_result = tester.test_projection(
        projection_path=projection_result.projection_path,
        context=context,
        actor="op:lab-256",
    )

    diamond_builder = DiamondManifestBuilder(nas_root=nas_root, receipts=NullReceipts())
    candidate = diamond_builder.build_candidate(
        projection_path=projection_result.projection_path,
        sealability_report_path=sealability_result.report_path,
        sealability_context=context,
        diamond_kind="D.PROJ",
        title="LogLine Projection Kernel Product Spine",
        purpose="Candidate Diamond preserving the bounded projection of the LogLine product spine.",
        created_by="op:lab-256",
    )

    print("manifest_path", candidate.manifest_path)
    print("diamond_candidate_id", candidate.diamond_candidate_id)
    print("manifest_hash", candidate.manifest_hash)
    print("nas_root", nas_root)


if __name__ == "__main__":
    main()
