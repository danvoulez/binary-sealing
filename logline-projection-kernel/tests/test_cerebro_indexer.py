"""Tests for cerebro_indexer."""

import os
import tempfile
import unittest

from logline_kernel.acts.act import Act
from logline_kernel.core.receipts import NullReceipts
from logline_kernel.engines.cerebro.indexer import CerebroConfig, CerebroIndexer
from logline_kernel.engines.flux.engine import FluxEngine, LocalFixtureExporter
from logline_kernel.processes.contract import ProcessContract, SlotRule
from logline_kernel.processes.ledger import ProcessLedger


class TestCerebroIndexer(unittest.TestCase):
    def _flux_manifest(self, nas_root: str):
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
        engine = FluxEngine(nas_root=nas_root, exporter=LocalFixtureExporter(), receipts=NullReceipts())
        return engine.run_entry(entry)

    def test_index_flux_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            flux_result = self._flux_manifest(tmp)
            cerebro_root = os.path.join(tmp, "Cerebro")
            indexer = CerebroIndexer(CerebroConfig(cerebro_root=cerebro_root), receipts=NullReceipts())
            result = indexer.index_flux_manifest(manifest_path=flux_result.manifest_path)
            self.assertTrue(os.path.exists(result.source_card_path))
            self.assertTrue(len(result.concepts) > 0)


if __name__ == "__main__":
    unittest.main()
