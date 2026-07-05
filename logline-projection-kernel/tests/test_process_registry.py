"""Tests for process_registry."""

import unittest

from logline_kernel.acts.act import Act
from logline_kernel.processes.contract import ProcessContract, SlotRule
from logline_kernel.processes.registry import MatchRule, ProcessRegistry, ProcessResolutionError


class TestProcessRegistry(unittest.TestCase):
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

    def test_resolve_explicit(self):
        registry = ProcessRegistry()
        contract = self._contract()
        registry.add(contract)
        act = Act(
            who="x", did="y", this="z", when="2026-07-02T12:00:00Z",
            status="registered", aux={"process_id": "flux.google_doc.v0"},
        )
        resolved = registry.resolve(act)
        self.assertEqual(resolved.process_id, contract.process_id)

    def test_resolve_no_match(self):
        registry = ProcessRegistry()
        act = Act(
            who="x", did="y", this="z", when="2026-07-02T12:00:00Z",
            status="registered",
        )
        with self.assertRaises(ProcessResolutionError):
            registry.resolve(act)

    def test_resolve_by_match_rule(self):
        registry = ProcessRegistry()
        contract = self._contract()
        registry.add(
            contract,
            match_rules=[MatchRule(slot="this", op="startswith", value="gdoc:", weight=5)],
        )
        act = Act(
            who="x", did="y", this="gdoc:doc@1", when="2026-07-02T12:00:00Z",
            status="registered",
        )
        resolved = registry.resolve(act)
        self.assertEqual(resolved.process_id, contract.process_id)


if __name__ == "__main__":
    unittest.main()
