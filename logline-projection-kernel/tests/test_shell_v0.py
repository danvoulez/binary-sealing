"""Tests for the portable-claim classifier and sealed-binary verification.

Runs the Foundation's vectors/sealed-binary/ vectors end to end (manifest +
payload bytes + source strings), plus unit tests for field-awareness: the
register check applies to identity-bearing fields only, never to vocabulary
strings like kind or container_profile.
"""

import hashlib
import json
import unittest
from pathlib import Path

from logline_kernel.core.hashing import content_hash
from logline_kernel.diamonds import shell_v0

FOUNDATION = Path(__file__).resolve().parents[2] / "LogLine-Foundation" / "conformance"
VECTORS = FOUNDATION / "vectors" / "sealed-binary"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _run_vector(vector: dict) -> list[str]:
    manifest = vector["manifest"]
    payload = bytes.fromhex(vector["payload_hex"])
    digests = [hashlib.sha256(s.encode()).hexdigest()
               for s in vector["source_strings_utf8"]]
    if vector.get("check") == "portability":
        _, problems = shell_v0.is_portable(manifest)
        return problems
    return shell_v0.verify_sealed_binary(
        manifest, payload, digests, vector["expected"].get("diamond_id"))


class TestFoundationVectors(unittest.TestCase):
    @unittest.skipUnless(VECTORS.exists(), "sealed-binary vectors not present")
    def test_valid_vectors_verify_clean(self):
        vectors = sorted((VECTORS / "valid").glob("*.json"))
        self.assertTrue(vectors)
        for path in vectors:
            vector = _load(path)
            self.assertEqual(_run_vector(vector), [], msg=path.name)
            portable, _ = shell_v0.is_portable(vector["manifest"])
            self.assertEqual(portable, vector["expected"]["portable"], msg=path.name)

    @unittest.skipUnless(VECTORS.exists(), "sealed-binary vectors not present")
    def test_invalid_vectors_fail_with_expected_problem(self):
        vectors = sorted((VECTORS / "invalid").glob("*.json"))
        self.assertTrue(vectors)
        for path in vectors:
            vector = _load(path)
            problems = _run_vector(vector)
            expected = vector["expected"]["problem_contains"]
            self.assertTrue(any(expected in p for p in problems),
                            msg=f"{path.name}: wanted {expected!r} in {problems}")


class TestFieldAwareness(unittest.TestCase):
    """identity-registers.v0: classify fields, never raw strings."""

    def _manifest(self, **over):
        payload = bytes(range(4))
        m = {
            "seal_version": "sealed-binary.v0",
            "kind": "compiled_training_diamond.v1",
            "payload": {"digest": hashlib.sha256(payload).hexdigest(),
                        "algorithm": "sha256", "length": 4,
                        "container_profile": "safetensors.sorted.v0"},
            "receipts": [],
            "json_canonicalization": "jcs-rfc8785",
        }
        m.update(over)
        return m

    def test_vocabulary_strings_with_dots_are_not_violations(self):
        # kind and container_profile carry dots and version suffixes —
        # vocabulary, not identity. Must pass.
        _, problems = shell_v0.classify_shell(self._manifest())
        self.assertEqual(problems, [])

    def test_prefixed_identity_field_fails(self):
        m = self._manifest()
        m["compiler_hash"] = "compiler:" + "a" * 64
        _, problems = shell_v0.classify_shell(m)
        self.assertTrue(any("compiler_hash" in p for p in problems))

    def test_unverified_quarantine_allows_free_claims(self):
        m = self._manifest(unverified={"pitch": "best diamond ever"})
        classification, problems = shell_v0.classify_shell(m)
        self.assertEqual(problems, [])
        self.assertEqual(classification["unverified"], shell_v0.UNVERIFIED)

    def test_free_claim_outside_quarantine_fails(self):
        m = self._manifest(pitch="best diamond ever")
        _, problems = shell_v0.classify_shell(m)
        self.assertTrue(any("unclassifiable portable claim" in p for p in problems))


class TestMerkle(unittest.TestCase):
    def test_root_is_order_independent_and_deduplicated(self):
        d = [hashlib.sha256(s.encode()).hexdigest() for s in ("a", "b", "c")]
        self.assertEqual(shell_v0.merkle_root(d), shell_v0.merkle_root(d[::-1]))
        self.assertEqual(shell_v0.merkle_root(d), shell_v0.merkle_root(d + [d[0]]))

    def test_single_leaf_root(self):
        d = hashlib.sha256(b"only").hexdigest()
        leaf = hashlib.sha256(b"\x00" + bytes.fromhex(d)).hexdigest()
        self.assertEqual(shell_v0.merkle_root([d]), leaf)

    def test_spec_worked_example_root(self):
        d = [hashlib.sha256(f"source-{c}".encode()).hexdigest() for c in "abc"]
        self.assertEqual(
            shell_v0.merkle_root(d),
            "9469af92426bc4ce62e6a20800ab62031aac6ee0be72e2fef4a6692d6e0d75f0",
        )

    def test_rejects_prefixed_digests(self):
        with self.assertRaises(ValueError):
            shell_v0.merkle_root(["sha256:" + "a" * 64])


class TestDiamondIdBinding(unittest.TestCase):
    def test_manifest_mutation_changes_diamond_id(self):
        payload = bytes(range(4))
        m = {
            "seal_version": "sealed-binary.v0",
            "kind": "compiled_training_diamond.v1",
            "payload": {"digest": hashlib.sha256(payload).hexdigest(),
                        "algorithm": "sha256", "length": 4},
            "receipts": [],
            "json_canonicalization": "jcs-rfc8785",
        }
        diamond_id = content_hash(m)
        self.assertEqual(shell_v0.verify_sealed_binary(m, payload, None, diamond_id), [])
        m2 = dict(m, receipts=["b" * 64])
        problems = shell_v0.verify_sealed_binary(m2, payload, None, diamond_id)
        self.assertTrue(any("diamond_id mismatch" in p for p in problems))


if __name__ == "__main__":
    unittest.main()
