"""Tests for the t_stream clock domain (ADR-0003)."""

import time
import unittest

from common.clock import StreamClock


class TestStreamClock(unittest.TestCase):
    def test_events_carry_t_stream(self):
        clock = StreamClock()
        ev = clock.stamp_event({"type": "test"})
        self.assertIn("t_stream", ev)
        self.assertIn("t_wall", ev)
        self.assertEqual(ev["type"], "test")

    def test_monotonic(self):
        clock = StreamClock()
        t1 = clock.now()
        time.sleep(0.01)
        t2 = clock.now()
        self.assertGreater(t2, t1)

    def test_ordering(self):
        clock = StreamClock()
        evs = [clock.stamp_event({"i": i}) for i in range(5)]
        ts = [e["t_stream"] for e in evs]
        self.assertEqual(ts, sorted(ts))


if __name__ == "__main__":
    unittest.main()
