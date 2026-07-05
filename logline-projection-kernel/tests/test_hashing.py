"""Tests for hashing."""

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


if __name__ == "__main__":
    unittest.main()
