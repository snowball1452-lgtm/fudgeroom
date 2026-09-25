"""Tests for the chat rollup (spec §3.2 step 3)."""

import unittest

from agents.knower.rollup import Rollup


class TestRollup(unittest.TestCase):
    def test_terms_and_questions(self):
        r = Rollup(window=10.0)
        r.add(0.0, "how do I beat the boss")
        r.add(0.5, "nice shot")
        s = r.summarize(0.6)
        self.assertEqual(s["n"], 2)
        self.assertIn("beat", s["top_terms"])
        self.assertEqual(s["questions"], 1)

    def test_window_eviction(self):
        r = Rollup(window=10.0)
        r.add(0.0, "old message")
        r.add(20.0, "fresh message")
        s = r.summarize(20.0)
        self.assertEqual(s["n"], 1)
        self.assertEqual(s["recent"], ["fresh message"])


if __name__ == "__main__":
    unittest.main()
