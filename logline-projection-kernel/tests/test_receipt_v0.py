"""Conformance tests for logline.receipt.v0 against the Foundation.

The Foundation's conformance suite is the source of truth: these tests load
its fixtures and vectors directly, so the kernel cannot silently drift from
the canon again. If the Foundation directory is absent (standalone kernel
checkout), the vector tests skip rather than pass vacuously.
"""

import json
import unittest
from pathlib import Path

from logline_kernel.acts.act import Act
from logline_kernel.core import receipt_v0
from logline_kernel.core.receipts import NullReceipts

FOUNDATION = Path(__file__).resolve().parents[2] / "LogLine-Foundation" / "conformance"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _is_envelope(obj: dict) -> bool:
    return "content" in obj and "envelope_hash" in obj


class TestFixtureReproduction(unittest.TestCase):
    """emit() must reproduce the Foundation fixture byte-for-byte hashes."""

    @unittest.skipUnless(FOUNDATION.exists(), "Foundation checkout not present")
    def test_emit_reproduces_official_fixture(self):
        fx = _load(FOUNDATION / "fixtures" / "receipt.valid.json")
        emitted = receipt_v0.emit(
            who=fx["who"], did=fx["did"], this=fx["this"], when=fx["when"],
            confirmed_by=fx["confirmed_by"], if_ok=fx["if_ok"],
            if_doubt=fx["if_doubt"], if_not=fx["if_not"], status=fx["status"],
        )
        self.assertEqual(emitted["hashes"], fx["hashes"])
        self.assertEqual(emitted["id"], fx["id"])
        self.assertEqual(receipt_v0.receipt_problems(emitted), [])

    @unittest.skipUnless(FOUNDATION.exists(), "Foundation checkout not present")
    def test_official_invalid_fixture_rejected(self):
        fx = _load(FOUNDATION / "fixtures" / "receipt.invalid.json")
        self.assertNotEqual(receipt_v0.receipt_problems(fx), [])


class TestFoundationVectors(unittest.TestCase):
    """Every Foundation vector must classify identically here and in Node."""

    @unittest.skipUnless(FOUNDATION.exists(), "Foundation checkout not present")
    def test_valid_vectors_pass(self):
        vectors = sorted((FOUNDATION / "vectors" / "receipt" / "valid").glob("*.json"))
        self.assertTrue(vectors, "no valid vectors found")
        for path in vectors:
            obj = _load(path)
            if _is_envelope(obj):
                problems = receipt_v0.envelope_problems(obj)
            else:
                problems = receipt_v0.receipt_problems(obj)
            self.assertEqual(problems, [], msg=f"{path.name}: {problems}")

    @unittest.skipUnless(FOUNDATION.exists(), "Foundation checkout not present")
    def test_invalid_vectors_fail(self):
        vectors = sorted((FOUNDATION / "vectors" / "receipt" / "invalid").glob("*.json"))
        self.assertTrue(vectors, "no invalid vectors found")
        for path in vectors:
            obj = _load(path)
            if _is_envelope(obj):
                problems = receipt_v0.envelope_problems(obj)
            else:
                problems = receipt_v0.receipt_problems(obj)
            self.assertNotEqual(problems, [], msg=f"{path.name} wrongly accepted")


class TestEmission(unittest.TestCase):
    def test_emitted_receipt_is_conformant(self):
        r = receipt_v0.emit(
            who="kernel", did="sealed_diamond", this="d" * 64,
            aux={"detail": {"step": 1}},
        )
        self.assertEqual(receipt_v0.receipt_problems(r), [])
        self.assertEqual(r["id"], r["hashes"]["content_hash"])

    def test_aux_excluded_from_tuple_hash_included_in_content_hash(self):
        base = dict(who="a", did="b", this="c", when="2026-07-05T00:00:00Z")
        r1 = receipt_v0.emit(**base)
        r2 = receipt_v0.emit(**base, aux={"note": "extra"})
        self.assertEqual(r1["hashes"]["tuple_hash"], r2["hashes"]["tuple_hash"])
        self.assertNotEqual(r1["hashes"]["content_hash"], r2["hashes"]["content_hash"])

    def test_aux_cannot_shadow_reserved_or_legacy_names(self):
        base = dict(who="a", did="b", this="c", when="2026-07-05T00:00:00Z")
        for bad in ("who", "id", "hashes", "result", "evidence", "transport"):
            with self.assertRaises(ValueError, msg=bad):
                receipt_v0.emit(**base, aux={bad: "x"})

    def test_receipt_sink_emits_conformant_receipts(self):
        r = NullReceipts().emit("did_thing", {"a": 1}, actor="tester")
        self.assertEqual(receipt_v0.receipt_problems(r), [])
        self.assertEqual(r["who"], "tester")
        self.assertEqual(r["did"], "did_thing")
        self.assertEqual(r["detail"], {"a": 1})


class TestEnvelope(unittest.TestCase):
    def test_wrap_and_verify_roundtrip(self):
        r = receipt_v0.emit(who="a", did="b", this="c", when="2026-07-05T00:00:00Z")
        env = receipt_v0.wrap_envelope(
            r, sent_by="kernel", sent_to="custodian",
            sent_at="2026-07-05T00:00:01Z", channel="test",
        )
        self.assertEqual(receipt_v0.envelope_problems(env), [])

    def test_tampered_transport_detected(self):
        r = receipt_v0.emit(who="a", did="b", this="c", when="2026-07-05T00:00:00Z")
        env = receipt_v0.wrap_envelope(r, "kernel", "custodian", "2026-07-05T00:00:01Z")
        env["transport"]["sent_to"] = "attacker"
        self.assertTrue(any("envelope_hash mismatch" in p
                            for p in receipt_v0.envelope_problems(env)))


class TestActCanonIdentity(unittest.TestCase):
    def test_process_id_is_bare_content_hash(self):
        a = Act(who="x", did="y", this="z", when="2026-07-02T12:00:00Z",
                status="registered")
        self.assertRegex(a.process_id, r"^[0-9a-f]{64}$")

    def test_aux_is_top_level_in_content_body(self):
        a = Act(who="x", did="y", this="z", when="2026-07-02T12:00:00Z",
                status="registered", aux={"note": "n1"})
        self.assertEqual(a.body()["note"], "n1")
        self.assertNotIn("AUX", a.body())

    def test_tuple_hash_stable_across_aux(self):
        base = dict(who="x", did="y", this="z", when="2026-07-02T12:00:00Z",
                    status="registered")
        a = Act(**base)
        b = Act(**base, aux={"note": "n1"})
        self.assertEqual(a.tuple_hash, b.tuple_hash)
        self.assertNotEqual(a.process_id, b.process_id)

    def test_aux_shadowing_slot_rejected(self):
        a = Act(who="x", did="y", this="z", when="2026-07-02T12:00:00Z",
                status="registered", aux={"who": "impostor"})
        with self.assertRaises(ValueError):
            a.body()

    def test_to_receipt_is_conformant(self):
        a = Act(who="x", did="y", this="z", when="2026-07-02T12:00:00Z",
                status="registered", aux={"note": "n1"})
        r = a.to_receipt()
        self.assertEqual(receipt_v0.receipt_problems(r), [])
        self.assertEqual(r["note"], "n1")


if __name__ == "__main__":
    unittest.main()
