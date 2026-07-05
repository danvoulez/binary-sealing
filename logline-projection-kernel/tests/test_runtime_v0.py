"""Conformance tests for diamond.runtime.v0.

The chain tests are the substance: a released output resolves only through
a conformant, unsuperseded attestation + capability chain, on one Diamond,
in the granted mode. The honesty clause is enforced structurally — nothing
here claims to verify runtime truth, only claim well-formedness and links.
"""

import json
import unittest
from pathlib import Path

from logline_kernel.core import receipt_v0
from logline_kernel.diamonds import receipts_v0, runtime_v0

FOUNDATION = Path(__file__).resolve().parents[2] / "LogLine-Foundation" / "conformance"
VECTORS = FOUNDATION / "vectors" / "diamond-runtime"

H = lambda c: c * 64


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class TestVocabularySingleSource(unittest.TestCase):
    @unittest.skipUnless(FOUNDATION.exists(), "Foundation checkout not present")
    def test_kernel_kinds_match_foundation_vocabulary(self):
        vocab = _load(FOUNDATION / "vocabularies" / "diamond.runtime.v0.json")
        self.assertEqual(vocab["vocabulary_version"], runtime_v0.VOCABULARY_VERSION)
        self.assertEqual(vocab["over"], receipt_v0.RECEIPT_VERSION)
        self.assertEqual(vocab["status"], runtime_v0.STATUS)
        self.assertEqual(vocab["kinds"], runtime_v0.KINDS)


class TestFoundationVectors(unittest.TestCase):
    @unittest.skipUnless(VECTORS.exists(), "diamond-runtime vectors not present")
    def test_valid_vectors_pass_both_layers(self):
        vectors = sorted((VECTORS / "valid").glob("*.json"))
        self.assertTrue(vectors)
        for path in vectors:
            obj = _load(path)
            self.assertEqual(receipt_v0.receipt_problems(obj), [], msg=path.name)
            self.assertEqual(runtime_v0.runtime_receipt_problems(obj), [], msg=path.name)

    @unittest.skipUnless(VECTORS.exists(), "diamond-runtime vectors not present")
    def test_invalid_vectors_fail_vocabulary_only(self):
        vectors = sorted((VECTORS / "invalid").glob("*.json"))
        self.assertTrue(vectors)
        for path in vectors:
            obj = _load(path)
            self.assertEqual(receipt_v0.receipt_problems(obj), [],
                             msg=f"{path.name} must stay hash-conformant")
            self.assertNotEqual(runtime_v0.runtime_receipt_problems(obj), [],
                                msg=f"{path.name} wrongly accepted")


class TestChain(unittest.TestCase):
    """Full chain: access grant -> attestation -> invocation -> output."""

    def setUp(self):
        self.diamond_id = H("d")
        self.access = receipts_v0.emit_diamond_receipt(
            "access", who="rights.lab.v1", this=self.diamond_id,
            aux={"grantee": "buyer", "mode": "train", "rights_policy_hash": H("f")})
        self.attestation = runtime_v0.emit_runtime_receipt(
            "attestation", who="runtime.enclave.v1", this=H("7"),
            aux={"trust_anchor": "amd.sev-snp", "quote_digest": H("2")})
        self.invocation = runtime_v0.emit_runtime_receipt(
            "invocation", who="runtime.enclave.v1", this=self.diamond_id,
            aux={"capability_receipt_id": self.access["id"],
                 "attestation_receipt_id": self.attestation["id"],
                 "mode": "train"})
        self.output = runtime_v0.emit_runtime_receipt(
            "output", who="runtime.enclave.v1", this=self.diamond_id,
            aux={"invocation_receipt_id": self.invocation["id"],
                 "output_digest": H("5"), "output_class": "model_delta",
                 "firewall_policy_hash": H("6")})
        self.ledger = [self.access, self.attestation, self.invocation, self.output]

    def test_happy_chain_resolves_clean(self):
        self.assertEqual(runtime_v0.verify_output_chain(self.output, self.ledger), [])

    def test_dangling_invocation_link_fails(self):
        ledger = [self.access, self.attestation]
        problems = runtime_v0.verify_output_chain(self.output, ledger)
        self.assertTrue(any("not found in ledger" in p for p in problems))

    def test_superseded_attestation_breaks_chain(self):
        sup = receipts_v0.emit_diamond_receipt(
            "supersession", who="authority", this=self.attestation["id"],
            aux={"diamond_id": self.diamond_id,
                 "reason": "TEE vulnerability disclosed"})
        problems = runtime_v0.verify_output_chain(self.output, self.ledger + [sup])
        self.assertTrue(any("superseded" in p for p in problems))

    def test_superseded_capability_breaks_chain(self):
        sup = receipts_v0.emit_diamond_receipt(
            "supersession", who="authority", this=self.access["id"],
            aux={"diamond_id": self.diamond_id, "reason": "license revoked"})
        problems = runtime_v0.verify_output_chain(self.output, self.ledger + [sup])
        self.assertTrue(any("capability link" in p and "superseded" in p
                            for p in problems))

    def test_mode_mismatch_fails(self):
        query_access = receipts_v0.emit_diamond_receipt(
            "access", who="rights.lab.v1", this=self.diamond_id,
            aux={"grantee": "buyer", "mode": "query", "rights_policy_hash": H("f")})
        invocation = runtime_v0.emit_runtime_receipt(
            "invocation", who="runtime.enclave.v1", this=self.diamond_id,
            aux={"capability_receipt_id": query_access["id"],
                 "attestation_receipt_id": self.attestation["id"],
                 "mode": "train"})
        output = runtime_v0.emit_runtime_receipt(
            "output", who="runtime.enclave.v1", this=self.diamond_id,
            aux={"invocation_receipt_id": invocation["id"],
                 "output_digest": H("5"), "output_class": "model_delta",
                 "firewall_policy_hash": H("6")})
        ledger = [query_access, self.attestation, invocation, output]
        problems = runtime_v0.verify_output_chain(output, ledger)
        self.assertTrue(any("mode mismatch" in p for p in problems))

    def test_diamond_mismatch_fails(self):
        other_output = runtime_v0.emit_runtime_receipt(
            "output", who="runtime.enclave.v1", this=H("9"),
            aux={"invocation_receipt_id": self.invocation["id"],
                 "output_digest": H("5"), "output_class": "model_delta",
                 "firewall_policy_hash": H("6")})
        problems = runtime_v0.verify_output_chain(other_output, self.ledger)
        self.assertTrue(any("diamond mismatch" in p for p in problems))

    def test_transfer_mode_is_not_invocable(self):
        with self.assertRaises(ValueError):
            runtime_v0.emit_runtime_receipt(
                "invocation", who="runtime.enclave.v1", this=self.diamond_id,
                aux={"capability_receipt_id": self.access["id"],
                     "attestation_receipt_id": self.attestation["id"],
                     "mode": "transfer"})

    def test_firewall_vocabulary_cannot_release_raw_source(self):
        with self.assertRaises(ValueError):
            runtime_v0.emit_runtime_receipt(
                "output", who="runtime.enclave.v1", this=self.diamond_id,
                aux={"invocation_receipt_id": self.invocation["id"],
                     "output_digest": H("5"), "output_class": "raw_source_text",
                     "firewall_policy_hash": H("6")})


if __name__ == "__main__":
    unittest.main()
