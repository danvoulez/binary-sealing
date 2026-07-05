"""Tests for sealability."""

import os
import tempfile
import unittest

from logline_kernel.acts.act import Act
from logline_kernel.core.receipts import NullReceipts
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


class TestSealability(unittest.TestCase):
    def _projection(self, nas_root: str):
        fixture_path = os.path.join(nas_root, "doc.txt")
        with open(fixture_path, "w", encoding="utf-8") as f:
            f.write("# LogLine\n\nThis document describes Cerebro, Flux, Diamond and operator mesh.\n")

        act = Act(
            who="x", did="y", this="gdoc:doc@1", when="2026-07-02T12:00:00Z",
            status="registered",
            aux={"origin": {"local_path": fixture_path}},
        )
        contract = ProcessContract(
            process_id="flux.google_doc.v0",
            version="0.1.0",
            title="Flux",
            colour="blue",
            engine="flux_engine",
            lens_id="flux.v0",
            slot_rules={},
            allowed_statuses={"registered"},
            required_aux=["origin"],
        )
        ledger = ProcessLedger(path=os.path.join(nas_root, "ledger.ndjson"), receipts=NullReceipts())
        entry = ledger.register(act, contract)
        flux = FluxEngine(nas_root=nas_root, exporter=LocalFixtureExporter(), receipts=NullReceipts())
        flux_result = flux.run_entry(entry)
        cerebro_root = os.path.join(nas_root, "Cerebro")
        indexer = CerebroIndexer(CerebroConfig(cerebro_root=cerebro_root), receipts=NullReceipts())
        indexer.index_flux_manifest(manifest_path=flux_result.manifest_path)
        builder = ProjectionBuilder(cerebro_root=cerebro_root, receipts=NullReceipts())
        lens = ProjectionLens(
            lens_id="test.lens",
            title="Test",
            purpose="Test lens",
            include_any_concepts=["logline"],
            min_sources=1,
        )
        return builder.build(lens=lens, actor="x", scope={"project": "test"})

    def test_sealable(self):
        with tempfile.TemporaryDirectory() as tmp:
            projection_result = self._projection(tmp)
            tester = SealabilityTester(
                cerebro_root=os.path.join(tmp, "Cerebro"),
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
                "custody_policy": {"exists": True, "vault": "nas:minivault", "path": tmp},
                "revocation": {"exists": True, "method": "supersede"},
                "receipts": {"configured": True, "kinds": []},
                "human_review": {"approved": True, "reviewed_by": "dan", "receipt": "r"},
            }
            result = tester.test_projection(
                projection_path=projection_result.projection_path,
                context=context,
            )
            self.assertTrue(result.sealable)
            self.assertTrue(os.path.exists(result.report_path))


if __name__ == "__main__":
    unittest.main()
