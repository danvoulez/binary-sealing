"""Run the full golden path: register -> flux -> cerebro -> project -> anchor -> seal."""

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
from logline_kernel.diamonds.sealing.sealer import DiamondSealer, HashOnlySigner, SealingAuthority
from logline_kernel.engines.anchor.finder import AnchorFinder, AnchorRequest
from logline_kernel.engines.cerebro.indexer import CerebroConfig, CerebroIndexer
from logline_kernel.engines.flux.engine import FluxEngine, LocalFixtureExporter
from logline_kernel.engines.projection.builder import ProjectionBuilder, ProjectionLens
from logline_kernel.processes.contract import ProcessContract, SlotRule
from logline_kernel.processes.ledger import ProcessLedger


def main():
    nas_root = tempfile.mkdtemp(prefix="logline_golden_")
    print("nas_root", nas_root)

    fixture_path = os.path.join(nas_root, "fixture", "projection-kernel-pack.txt")
    os.makedirs(os.path.dirname(fixture_path), exist_ok=True)
    with open(fixture_path, "w", encoding="utf-8") as f:
        f.write("# LogLine Projection Kernel Pack\n\n")
        f.write("This document describes the LogLine Projection Kernel, ")
        f.write("Cerebro, Flux, Diamond, and operator mesh.\n")

    act = Act(
        who="op:golden",
        did="observed",
        this="gdoc:projection-kernel-pack@rev42",
        when="2026-07-02T12:00:00Z",
        confirmed_by="drive-revision:42",
        status="registered",
        aux={"origin": {"local_path": fixture_path}, "process_id": "flux.google_doc.v0"},
    )
    contract = ProcessContract(
        process_id="flux.google_doc.v0",
        version="0.1.0",
        title="Flux Google Doc custody",
        colour="blue",
        engine="flux_engine",
        lens_id="flux.google_doc.v0",
        slot_rules={"confirmed_by": SlotRule(meaning="revision", required=True)},
        allowed_statuses={"registered", "qualified", "projectable"},
        required_aux=["origin"],
        effects_allowed=True,
    )

    ledger = ProcessLedger(path=os.path.join(nas_root, "process_ledger.ndjson"), receipts=NullReceipts())
    entry = ledger.register(act, contract, registered_by="op:golden")
    print("1. registered", entry["process_record_id"])

    flux = FluxEngine(nas_root=nas_root, exporter=LocalFixtureExporter(), receipts=NullReceipts())
    flux_result = flux.run_entry(entry, actor="op:golden")
    print("2. flux", flux_result.manifest_path)

    cerebro_root = os.path.join(nas_root, "Cerebro")
    indexer = CerebroIndexer(CerebroConfig(cerebro_root=cerebro_root), receipts=NullReceipts())
    index_result = indexer.index_flux_manifest(manifest_path=flux_result.manifest_path, actor="op:golden")
    print("3. cerebro", index_result.cerebro_source_id, index_result.fold_state)

    builder = ProjectionBuilder(cerebro_root=cerebro_root, receipts=NullReceipts())
    lens = ProjectionLens(
        lens_id="kernel.product_spine.v1",
        title="LogLine Projection Kernel Product Spine",
        purpose="Golden path projection.",
        include_any_concepts=["dynamic_projection", "projection_kernel", "diamond", "cerebro", "flux", "operator_mesh"],
        allowed_fold_states=["indexed", "folding", "projectable", "stable", "sealable"],
        require_projection_ready=True,
        min_sources=1,
        max_sources=25,
        review_required=True,
    )
    projection_result = builder.build(lens=lens, actor="op:golden", scope={"project": "logline_projection_kernel"})
    print("4. projection", projection_result.projection_hash)

    finder = AnchorFinder(cerebro_root=cerebro_root, receipts=NullReceipts())
    anchor = finder.find(
        AnchorRequest(
            actor="op:golden",
            task="Explain the LogLine product spine",
            purpose="Golden path grounding",
            query_concepts=["projection_kernel", "dynamic_projection", "flux", "cerebro", "diamond"],
        )
    )
    print("5. anchor", anchor.anchor_state, anchor.selected_anchor_id)

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
        "rights": {"attached": True, "license": "internal", "constraints": []},
        "scorecard": {"exists": True, "trust_score": 0.82, "method": "manual_v0"},
        "custody_policy": {"exists": True, "vault": "nas:minivault", "path": os.path.join(nas_root, "Minivault")},
        "revocation": {"exists": True, "method": "supersede_or_revoke_manifest"},
        "receipts": {"configured": True, "kinds": ["diamond.candidate", "diamond.sealed", "diamond.revoked"]},
        "human_review": {"approved": True, "reviewed_by": "dan", "receipt": "receipt:manual-review-placeholder"},
    }
    sealability_result = tester.test_projection(
        projection_path=projection_result.projection_path,
        context=context,
        actor="op:golden",
    )
    print("6. sealability", sealability_result.sealable)

    diamond_builder = DiamondManifestBuilder(nas_root=nas_root, receipts=NullReceipts())
    candidate = diamond_builder.build_candidate(
        projection_path=projection_result.projection_path,
        sealability_report_path=sealability_result.report_path,
        sealability_context=context,
        diamond_kind="D.PROJ",
        title="LogLine Projection Kernel Product Spine",
        purpose="Golden path diamond.",
        created_by="op:golden",
    )
    print("7. candidate", candidate.diamond_candidate_id)

    sealer = DiamondSealer(nas_root=nas_root, receipts=NullReceipts(), signer=HashOnlySigner())
    authority = SealingAuthority(
        authority_id="dan",
        name="Daniel Amarilho",
        role="Golden path sealer",
        allowed_diamond_kinds=["D.PROJ"],
    )
    seal = sealer.seal_candidate(
        candidate_manifest_path=candidate.manifest_path,
        authority=authority,
        actor="op:golden",
        seal_note="Golden path seal.",
    )
    print("8. sealed", seal.diamond_id)
    print("golden_path_complete")


if __name__ == "__main__":
    main()
