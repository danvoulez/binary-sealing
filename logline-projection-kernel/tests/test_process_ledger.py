"""Tests for process_ledger."""

import os
import tempfile
import unittest

from logline_kernel.acts.act import Act
from logline_kernel.core.receipts import NullReceipts
from logline_kernel.processes.contract import ProcessContract, SlotRule
from logline_kernel.processes.ledger import ProcessLedger


class TestProcessLedger(unittest.TestCase):
    def _contract(self):
        return ProcessContract(
            process_id="flux.google_doc.v0",
            version="0.1.0",
            title="Flux",
            colour="blue",
            engine="flux_engine",
            lens_id="flux.v0",
            slot_rules={},
            allowed_statuses={"registered"},
        )

    def test_register_and_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = ProcessLedger(path=os.path.join(tmp, "ledger.ndjson"), receipts=NullReceipts())
            act = Act(
                who="x", did="y", this="z", when="2026-07-02T12:00:00Z",
                status="registered",
            )
            record = ledger.register(act, self._contract())
            self.assertEqual(record["registration_state"], "ignited")
            self.assertEqual(len(ledger.records()), 1)

    def test_verify_chain(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = ProcessLedger(path=os.path.join(tmp, "ledger.ndjson"), receipts=NullReceipts())
            act = Act(
                who="x", did="y", this="z", when="2026-07-02T12:00:00Z",
                status="registered",
            )
            ledger.register(act, self._contract())
            ok, problems = ledger.verify_chain()
            self.assertTrue(ok)
            self.assertEqual(problems, [])


if __name__ == "__main__":
    unittest.main()
