"""Director tests (ADR-0004): fog-of-war selection rules."""

import unittest

from agents.voice.director import Director
from agents.voice.playsheets import SheetError, load

SHEET = {
    "sheet_version": "1.0.0",
    "game": "test",
    "policies": {"min_gap_s": 10, "repeat_window_s": 100, "confidence_floor": 0.6},
    "facts": [
        {"id": "f1", "tags": ["zone"],
         "diction": {"inner": "rotate north", "broadcast": "good read"}},
        {"id": "f2", "tags": ["buy"],
         "diction": {"inner": "hold the buys", "broadcast": "he's saving"}},
    ],
}


class TestDirector(unittest.TestCase):
    def setUp(self):
        self.d = Director(SHEET)

    def test_tag_match_speaks(self):
        dec = self.d.decide({"t_stream": 0.0, "tags": ["zone"], "confidence": 0.9})
        self.assertEqual(dec.action, "speak")
        self.assertEqual(dec.line, "rotate north")

    def test_low_confidence_holds_even_on_match(self):
        dec = self.d.decide({"t_stream": 0.0, "tags": ["zone"], "confidence": 0.3})
        self.assertEqual(dec.action, "hold")

    def test_cooldown_holds(self):
        self.assertEqual(self.d.decide({"t_stream": 0.0, "tags": ["zone"], "confidence": 1.0}).action, "speak")
        dec = self.d.decide({"t_stream": 5.0, "tags": ["buy"], "confidence": 1.0})
        self.assertEqual(dec.action, "hold")  # min_gap is 10

    def test_separation_window(self):
        self.d.decide({"t_stream": 0.0, "tags": ["zone"], "confidence": 1.0})
        self.d.decide({"t_stream": 20.0, "tags": ["buy"], "confidence": 1.0})  # different fact, ok
        dec = self.d.decide({"t_stream": 1000.0, "tags": ["zone"], "confidence": 1.0})
        self.assertEqual(dec.action, "speak")  # window (100s) elapsed

    def test_no_match_holds(self):
        dec = self.d.decide({"t_stream": 0.0, "tags": ["irrelevant"], "confidence": 1.0})
        self.assertEqual(dec.action, "hold")

    def test_sheet_loader_validates(self):
        sheet = load("agents/voice/playsheets/verdansk.json")
        self.assertEqual(len(sheet["facts"]), 3)

    def test_sheet_loader_rejects_bad_sheet(self):
        bad = {"game": "x", "facts": [{"no_id": True}]}
        import tempfile, json
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(bad, f)
            path = f.name
        with self.assertRaises(SheetError):
            load(path)


if __name__ == "__main__":
    unittest.main()
