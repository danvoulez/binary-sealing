"""Tests for the first real sealer.

The anchor test: seal() must reproduce the sealed-binary.v0 spec's
published worked example byte-for-byte — same payload, same sources, same
diamond_id. The sealer and the published profile can never drift apart.
"""

import hashlib
import unittest

from logline_kernel.diamonds import receipts_v0, seal_binary, shell_v0

H = lambda c: c * 64

SPEC_DIAMOND_ID = "0167d3b3348a9db022a66392087cbeed2292872238cbc0a992597f3be07c620a"
SPEC_PAYLOAD_DIGEST = "8a851ff82ee7048ad09ec3847f1ddf44944104d2cbd17ef4e3db22c6785a0d45"
SPEC_MERKLE_ROOT = "9469af92426bc4ce62e6a20800ab62031aac6ee0be72e2fef4a6692d6e0d75f0"


class TestSpecWorkedExample(unittest.TestCase):
    def test_seal_reproduces_published_vector(self):
        payload = bytes(range(8))
        digests = [hashlib.sha256(s.encode()).hexdigest()
                   for s in ("source-a", "source-b", "source-c")]
        result = seal_binary.seal(
            payload, digests,
            process_contract_hash=H("0"),
            compiler_hash=H("0"),
            rights_policy_hash=H("0"),
        )
        self.assertEqual(result.payload_digest, SPEC_PAYLOAD_DIGEST)
        self.assertEqual(result.source_merkle_root, SPEC_MERKLE_ROOT)
        self.assertEqual(result.diamond_id, SPEC_DIAMOND_ID)
        self.assertFalse(result.portable)  # identity object, no receipts


class TestSealDiscipline(unittest.TestCase):
    def test_seal_self_verifies(self):
        result = seal_binary.seal(b"artifact", compiler_hash=H("c"))
        self.assertEqual(
            shell_v0.verify_sealed_binary(
                result.manifest, b"artifact", None, result.diamond_id),
            [],
        )

    def test_seal_refuses_prefixed_identity_input(self):
        with self.assertRaises(seal_binary.SealError):
            seal_binary.seal(b"artifact", compiler_hash="compiler:" + H("c"))

    def test_unverified_quarantine_survives_sealing(self):
        result = seal_binary.seal(
            b"artifact", unverified={"pitch": "very shiny"})
        classification, problems = shell_v0.classify_shell(result.manifest)
        self.assertEqual(problems, [])
        self.assertEqual(classification["unverified"], shell_v0.UNVERIFIED)

    def test_manifest_kwargs_cannot_inject_free_claims(self):
        # build_manifest only places declared fields; there is no path for
        # arbitrary keys into the shell
        with self.assertRaises(TypeError):
            seal_binary.seal(b"artifact", marketing_promise="10x")


class TestSealPortable(unittest.TestCase):
    def _seal(self):
        return seal_binary.seal_portable(
            bytes(range(10)),
            [b"src-1", b"src-2"],
            who="compiler.lab.v1",
            compiler_hash=H("c"),
            process_contract_hash=H("a"),
            rights_policy_hash=H("f"),
        )

    def test_portable_shell_with_conformant_receipts(self):
        result = self._seal()
        self.assertTrue(result.portable)
        self.assertEqual(len(result.receipts), 2)
        for receipt in result.receipts:
            self.assertEqual(receipts_v0.diamond_receipt_problems(receipt), [])
        self.assertEqual(
            [r["did"] for r in result.receipts],
            ["accepted_custody", "compiled_diamond"],
        )

    def test_binding_order_no_cycles(self):
        """Embedded receipts address pre-sealing objects, never diamond_id."""
        result = self._seal()
        custody, compilation = result.receipts
        self.assertEqual(custody["this"], result.source_merkle_root)
        self.assertEqual(compilation["this"], result.payload_digest)
        for receipt in result.receipts:
            self.assertNotEqual(receipt["this"], result.diamond_id)
        # and the manifest embeds exactly those receipt ids
        self.assertEqual(
            result.manifest["receipts"],
            [custody["id"], compilation["id"]],
        )

    def test_compilation_receipt_matches_manifest(self):
        result = self._seal()
        compilation = result.receipts[1]
        self.assertEqual(compilation["payload_digest"],
                         result.manifest["payload"]["digest"])
        self.assertEqual(compilation["source_merkle_root"],
                         result.manifest["source_commitments"]["merkle_root"])
        self.assertEqual(compilation["compiler_hash"],
                         result.manifest["compiler_hash"])

    def test_requires_sources(self):
        with self.assertRaises(seal_binary.SealError):
            seal_binary.seal_portable(
                b"artifact", [],
                who="w", compiler_hash=H("c"),
                process_contract_hash=H("a"), rights_policy_hash=H("f"))

    def test_sealed_shell_supports_post_seal_access_chain(self):
        """After sealing, an access receipt addresses the diamond_id —
        the ledger-side half of the binding order."""
        result = self._seal()
        access = receipts_v0.emit_diamond_receipt(
            "access", who="rights.lab.v1", this=result.diamond_id,
            aux={"grantee": "buyer", "mode": "train",
                 "rights_policy_hash": result.manifest["rights_policy_hash"]})
        self.assertEqual(receipts_v0.diamond_receipt_problems(access), [])
        self.assertEqual(access["this"], result.diamond_id)


if __name__ == "__main__":
    unittest.main()
