"""Tests for process_contract."""

import unittest

from logline_kernel.acts.act import Act
from logline_kernel.processes.contract import ProcessContract, SlotRule


class TestProcessContract(unittest.TestCase):
    def _contract(self):
        return ProcessContract(
            process_id="flux.google_doc.v0",
            version="0.1.0",
            title="Flux",
            colour="blue",
            engine="flux_engine",
            lens_id="flux.v0",
            slot_rules={"confirmed_by": SlotRule(meaning="revision", required=True)},
            allowed_statuses={"registered"},
            required_aux=["origin"],
        )

    def test_valid_act_passes(self):
        act = Act(
            who="x", did="y", this="z", when="2026-07-02T12:00:00Z",
            confirmed_by="rev:1", status="registered",
            aux={"origin": {"local_path": "/tmp/x"}},
        )
        self.assertEqual(self._contract().registration_problems(act), [])

    def test_missing_required_slot(self):
        act = Act(
            who="x", did="y", this="z", when="2026-07-02T12:00:00Z",
            status="registered",
            aux={"origin": {"local_path": "/tmp/x"}},
        )
        problems = self._contract().registration_problems(act)
        self.assertTrue(any("missing_slot:confirmed_by" in p for p in problems))

    def test_invalid_status(self):
        act = Act(
            who="x", did="y", this="z", when="2026-07-02T12:00:00Z",
            confirmed_by="rev:1", status="draft",
            aux={"origin": {"local_path": "/tmp/x"}},
        )
        problems = self._contract().registration_problems(act)
        self.assertTrue(any("invalid_status" in p for p in problems))

    def test_contract_hash_stable(self):
        c = self._contract()
        self.assertEqual(c.contract_hash, c.contract_hash)


if __name__ == "__main__":
    unittest.main()
