"""Tests for flux_engine."""

import os
import tempfile
import unittest

from logline_kernel.acts.act import Act
from logline_kernel.core.receipts import NullReceipts
from logline_kernel.engines.flux.engine import FluxEngine, LocalFixtureExporter
from logline_kernel.processes.contract import ProcessContract, SlotRule
from logline_kernel.processes.ledger import ProcessLedger


class TestFluxEngine(unittest.TestCase):
    def _entry(self, nas_root: str):
        fixture_path = os.path.join(nas_root, "doc.txt")
        with open(fixture_path, "w", encoding="utf-8") as f:
            f.write("source text")

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
        return ledger.register(act, contract)

    def test_run_entry(self):
        with tempfile.TemporaryDirectory() as tmp:
            entry = self._entry(tmp)
            engine = FluxEngine(nas_root=tmp, exporter=LocalFixtureExporter(), receipts=NullReceipts())
            result = engine.run_entry(entry)
            self.assertTrue(os.path.exists(result.manifest_path))
            self.assertTrue(result.manifest_path.endswith("manifest.json"))


if __name__ == "__main__":
    unittest.main()
