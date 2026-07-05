"""Tests for act process_id."""

import unittest

from logline_kernel.acts.act import Act


class TestActProcessId(unittest.TestCase):
    def test_process_id_stable(self):
        a = Act(who="x", did="y", this="z", when="2026-07-02T12:00:00Z", status="registered")
        b = Act(who="x", did="y", this="z", when="2026-07-02T12:00:00Z", status="registered")
        self.assertEqual(a.process_id, b.process_id)

    def test_process_id_changes_with_body(self):
        a = Act(who="x", did="y", this="z", when="2026-07-02T12:00:00Z", status="registered")
        b = Act(who="x", did="y", this="w", when="2026-07-02T12:00:00Z", status="registered")
        self.assertNotEqual(a.process_id, b.process_id)

    def test_act_id_alias(self):
        a = Act(who="x", did="y", this="z", when="2026-07-02T12:00:00Z", status="registered")
        self.assertEqual(a.act_id, a.process_id)


if __name__ == "__main__":
    unittest.main()
