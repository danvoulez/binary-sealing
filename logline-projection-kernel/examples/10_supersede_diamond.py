"""Example: supersede a sealed Diamond with a newer one."""

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
from logline_kernel.diamonds.state.gate import DiamondStateGate, StateChangeAuthority, StateChangeRequest
from logline_kernel.engines.cerebro.indexer import CerebroConfig, CerebroIndexer
from logline_kernel.engines.flux.engine import FluxEngine, LocalFixtureExporter
from logline_kernel.engines.projection.builder import ProjectionBuilder, ProjectionLens
from logline_kernel.processes.contract import ProcessContract, SlotRule
from logline_kernel.processes.ledger import ProcessLedger


def build_and_seal_diamond(nas_root: str, this_value: str):
    fixture_path = os.path.join(nas_root, "fixture", f"{this_value.replace(':', '_')}.txt")
    os.makedirs(os.path.dirname(fixture_path), exist_ok=True)
    with open(fixture_path, "w", encoding="utf-8") as f:
        f.write(f"# {this_value}\n\nSource text for diamond.\n")

    act = Act(
        who="op:lab-512",
        did="observed",
        this=this_value,
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

    ledger = ProcessLedger(path=os.path.join(nas_root, "process_ledger.ndjson"), receipts=NullReceipts())
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
        purpose="Bounded view.",
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
        "rights": {"attached": True, "license": "internal", "constraints": ["no_public_export_without_approval"]},
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
        purpose="Candidate Diamond.",
        created_by="op:lab-256",
    )

    sealer = DiamondSealer(nas_root=nas_root, receipts=NullReceipts(), signer=HashOnlySigner())
    authority = SealingAuthority(
        authority_id="dan",
        name="Daniel Amarilho",
        role="Final sealing authority",
        allowed_diamond_kinds=["D.PROJ"],
        public_key_ref=None,
        policy_ref="diamond.sealing.policy.v0",
    )
    return sealer.seal_candidate(
        candidate_manifest_path=candidate.manifest_path,
        authority=authority,
        actor="op:lab-256",
        seal_note="Seal.",
    )


def main():
    nas_root = tempfile.mkdtemp(prefix="logline_nas_")
    old_seal = build_and_seal_diamond(nas_root, "gdoc:projection-kernel-pack@rev42")
    new_seal = build_and_seal_diamond(nas_root, "gdoc:projection-kernel-pack@rev43")

    gate = DiamondStateGate(nas_root=nas_root, receipts=NullReceipts())
    authority = StateChangeAuthority(
        authority_id="dan",
        name="Daniel Amarilho",
        role="Diamond state authority",
        allowed_modes=["supersede", "revoke", "mark_historical", "affirm_current"],
    )
    request = StateChangeRequest(
        mode="supersede",
        reason="A newer Diamond has the same intended role with a stronger source boundary and lower doubt.",
        evidence_refs=[f"diamond:{new_seal.diamond_id}"],
        successor_manifest_path=new_seal.sealed_manifest_path,
        note="Old Diamond remains historically valid but is not the current safe anchor.",
    )

    result = gate.change_state(
        sealed_manifest_path=old_seal.sealed_manifest_path,
        request=request,
        authority=authority,
        actor="op:lab-256",
    )

    print("new_state", result.new_state)
    print("diamond_id", result.diamond_id)
    print("state_event_path", result.state_event_path)
    print("nas_root", nas_root)


if __name__ == "__main__":
    main()
