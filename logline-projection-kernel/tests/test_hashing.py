"""Tests for hashing (canon profile jcs-rfc8785)."""

import unittest

from logline_kernel.core.hashing import canonical_json, content_hash


class TestHashing(unittest.TestCase):
    def test_canonical_json_deterministic(self):
        a = canonical_json({"b": 2, "a": 1})
        b = canonical_json({"a": 1, "b": 2})
        self.assertEqual(a, b)

    def test_content_hash_prefix(self):
        h = content_hash({"x": 1}, "test:")
        self.assertTrue(h.startswith("test:"))
        self.assertEqual(len(h), len("test:") + 64)

    def test_content_hash_no_prefix(self):
        h = content_hash({"x": 1})
        self.assertEqual(len(h), 64)
        self.assertFalse(h.startswith("test:"))


class TestJcsConformance(unittest.TestCase):
    """Vectors from LogLine-Foundation/conformance/hash-profiles/jcs-rfc8785.md
    and RFC 8785 (ECMAScript number serialization, UTF-16 key sorting)."""

    def test_foundation_worked_example(self):
        obj = {"b": 2, "a": [1, 0.5], "c": "hi"}
        self.assertEqual(canonical_json(obj), b'{"a":[1,0.5],"b":2,"c":"hi"}')
        self.assertEqual(
            content_hash(obj),
            "54927d21fad3946f67210fdacd35b9eecc06842b4a0c4fcf33e382a301f7246f",
        )

    def test_es_number_formatting(self):
        vectors = [
            (0.0, "0"),
            (-0.0, "0"),
            (1.0, "1"),
            (-5.0, "-5"),
            (4.5, "4.5"),
            (0.002, "0.002"),
            (1e-6, "0.000001"),
            (1e-7, "1e-7"),
            (1e16, "10000000000000000"),
            (1e20, "100000000000000000000"),
            (1e21, "1e+21"),
            (1.5e-8, "1.5e-8"),
            (333333333.33333329, "333333333.3333333"),
            (9007199254740994.0, "9007199254740994"),
        ]
        for x, want in vectors:
            self.assertEqual(canonical_json(x).decode(), want, msg=repr(x))

    def test_keys_sort_by_utf16_code_units(self):
        # U+10000 encodes as surrogates D800 DC00 in UTF-16, which sort
        # BEFORE U+E000; a code-point sort puts U+E000 first. RFC 8785
        # requires the UTF-16 order.
        obj = {"": 1, "\U00010000": 2}
        got = canonical_json(obj).decode()
        self.assertEqual(got, '{"\U00010000":2,"":1}')

    def test_string_escaping_minimal(self):
        self.assertEqual(
            canonical_json({"k": "a\"b\\c\nd\x01é"}),
            '{"k":"a\\"b\\\\c\\nd\\u0001é"}'.encode("utf-8"),
        )

    def test_arrays_preserve_order(self):
        self.assertEqual(canonical_json([3, 1, 2]), b"[3,1,2]")

    def test_rejects_nan_and_infinity(self):
        for bad in (float("nan"), float("inf"), float("-inf")):
            with self.assertRaises(ValueError):
                canonical_json(bad)

    def test_rejects_unsafe_integers(self):
        with self.assertRaises(ValueError):
            canonical_json(2**53 + 1)
        # boundary itself is fine
        self.assertEqual(canonical_json(2**53).decode(), str(2**53))


if __name__ == "__main__":
    unittest.main()
