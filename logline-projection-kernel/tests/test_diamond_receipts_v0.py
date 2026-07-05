"""Conformance tests for diamond.receipts.v0.

Two invariants proven here:
1. Every valid diamond receipt vector is ALSO a valid plain receipt —
   vocabularies constrain the canon shape, they never replace it.
2. The kernel's embedded KINDS table equals the Foundation's
   machine-readable vocabulary byte-for-byte, so they cannot drift.
"""

import json
import unittest
from pathlib import Path

from logline_kernel.core import receipt_v0
from logline_kernel.diamonds import receipts_v0

FOUNDATION = Path(__file__).resolve().parents[2] / "LogLine-Foundation" / "conformance"
VECTORS = FOUNDATION / "vectors" / "diamond-receipts"

H = lambda c: c * 64


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class TestVocabularySingleSource(unittest.TestCase):
    @unittest.skipUnless(FOUNDATION.exists(), "Foundation checkout not present")
    def test_kernel_kinds_match_foundation_vocabulary(self):
        vocab = _load(FOUNDATION / "vocabularies" / "diamond.receipts.v0.json")
        self.assertEqual(vocab["vocabulary_version"], receipts_v0.VOCABULARY_VERSION)
        self.assertEqual(vocab["over"], receipt_v0.RECEIPT_VERSION)
        self.assertEqual(vocab["status"], receipts_v0.STATUS)
        self.assertEqual(vocab["kinds"], receipts_v0.KINDS)


class TestFoundationVectors(unittest.TestCase):
    @unittest.skipUnless(VECTORS.exists(), "diamond-receipt vectors not present")
    def test_valid_vectors_pass_both_layers(self):
        vectors = sorted((VECTORS / "valid").glob("*.json"))
        self.assertTrue(vectors)
        for path in vectors:
            obj = _load(path)
            self.assertEqual(receipt_v0.receipt_problems(obj), [],
                             msg=f"{path.name} must be a valid plain receipt")
            self.assertEqual(receipts_v0.diamond_receipt_problems(obj), [],
                             msg=f"{path.name} must satisfy its vocabulary")

    @unittest.skipUnless(VECTORS.exists(), "diamond-receipt vectors not present")
    def test_invalid_vectors_fail_vocabulary_but_not_base_layer(self):
        vectors = sorted((VECTORS / "invalid").glob("*.json"))
        self.assertTrue(vectors)
        for path in vectors:
            obj = _load(path)
            self.assertEqual(receipt_v0.receipt_problems(obj), [],
                             msg=f"{path.name} must stay hash-conformant (vocabulary-only break)")
            self.assertNotEqual(receipts_v0.diamond_receipt_problems(obj), [],
                                msg=f"{path.name} wrongly accepted by vocabulary")


class TestEmission(unittest.TestCase):
    def test_emit_all_kinds(self):
        cases = {
            "custody": (H("e"), {"custody_policy_hash": H("1")}),
            "compilation": (H("d"), {
                "compiler_hash": H("c"), "process_contract_hash": H("a"),
                "payload_digest": H("b"), "source_merkle_root": H("e")}),
            "evaluation": (H("d"), {
                "baseline_score": 0.61, "trained_score": 0.74,
                "improvement_delta": 0.13, "target_tasks": "clause-extraction",
                "evaluator": "eval.lab.v1"}),
            "privacy": (H("d"), {"privacy_mode": "dp", "epsilon": 2.5}),
            "access": (H("d"), {"grantee": "buyer", "mode": "query",
                                "rights_policy_hash": H("f")}),
            "supersession": (H("9"), {"diamond_id": H("d"), "reason": "new attack"}),
        }
        for kind, (this, aux) in cases.items():
            r = receipts_v0.emit_diamond_receipt(kind, who="w", this=this, aux=aux)
            self.assertEqual(receipts_v0.diamond_receipt_problems(r), [], msg=kind)

    def test_emit_refuses_nonconformant(self):
        with self.assertRaises(ValueError):
            receipts_v0.emit_diamond_receipt(
                "privacy", who="w", this=H("d"), aux={"privacy_mode": "dp"})
        with self.assertRaises(ValueError):
            receipts_v0.emit_diamond_receipt(
                "supersession", who="w", this="receipt:" + H("9"),
                aux={"diamond_id": H("d"), "reason": "r"})
        with self.assertRaises(ValueError):
            receipts_v0.emit_diamond_receipt("nonsense", who="w", this=H("d"), aux={})

    def test_number_aux_survives_jcs_roundtrip(self):
        # evaluation scores are floats — the exact case the old naive
        # canonicalization would have forked hashes on
        r = receipts_v0.emit_diamond_receipt(
            "evaluation", who="w", this=H("d"),
            aux={"baseline_score": 0.61, "trained_score": 1e-7,
                 "improvement_delta": -0.5, "target_tasks": "t",
                 "evaluator": "e"})
        rehydrated = json.loads(json.dumps(r))
        self.assertEqual(receipts_v0.diamond_receipt_problems(rehydrated), [])
        self.assertEqual(receipt_v0.receipt_content_hash(rehydrated), r["id"])


class TestSupersessionResolution(unittest.TestCase):
    def _claim_and_supersession(self):
        claim = receipts_v0.emit_diamond_receipt(
            "privacy", who="redteam", this=H("d"),
            aux={"privacy_mode": "empirical", "attack_suite": "s.v1",
                 "attack_budget": "1e6"})
        sup = receipts_v0.emit_diamond_receipt(
            "supersession", who="authority", this=claim["id"],
            aux={"diamond_id": H("d"), "reason": "attack published"})
        return claim, sup

    def test_claim_active_until_superseded(self):
        claim, sup = self._claim_and_supersession()
        self.assertTrue(receipts_v0.is_active_claim(claim, []))
        self.assertFalse(receipts_v0.is_active_claim(claim, [sup]))

    def test_nonconformant_supersession_does_not_close_claim(self):
        claim, sup = self._claim_and_supersession()
        broken = dict(sup)
        del broken["reason"]  # vocabulary violation, hashes now stale too
        self.assertTrue(receipts_v0.is_active_claim(claim, [broken]))

    def test_supersession_of_other_claim_is_ignored(self):
        claim, _ = self._claim_and_supersession()
        other_sup = receipts_v0.emit_diamond_receipt(
            "supersession", who="authority", this=H("0"),
            aux={"diamond_id": H("d"), "reason": "unrelated"})
        self.assertTrue(receipts_v0.is_active_claim(claim, [other_sup]))


if __name__ == "__main__":
    unittest.main()
