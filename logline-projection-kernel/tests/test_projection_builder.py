"""Tests for projection_builder."""

import os
import tempfile
import unittest

from logline_kernel.acts.act import Act
from logline_kernel.core.receipts import NullReceipts
from logline_kernel.engines.cerebro.indexer import CerebroConfig, CerebroIndexer
from logline_kernel.engines.flux.engine import FluxEngine, LocalFixtureExporter
from logline_kernel.engines.projection.builder import ProjectionBuilder, ProjectionLens
from logline_kernel.processes.contract import ProcessContract, SlotRule
from logline_kernel.processes.ledger import ProcessLedger


class TestProjectionBuilder(unittest.TestCase):
    def _seed(self, nas_root: str):
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
        return cerebro_root

    def test_build_projection(self):
        with tempfile.TemporaryDirectory() as tmp:
            cerebro_root = self._seed(tmp)
            builder = ProjectionBuilder(cerebro_root=cerebro_root, receipts=NullReceipts())
            lens = ProjectionLens(
                lens_id="test.lens",
                title="Test",
                purpose="Test lens",
                include_any_concepts=["logline"],
                min_sources=1,
            )
            result = builder.build(lens=lens, actor="x", scope={"project": "test"})
            self.assertTrue(os.path.exists(result.projection_path))
            self.assertEqual(result.included_count, 1)


if __name__ == "__main__":
    unittest.main()
