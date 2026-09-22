"""G20 is advisory; semantic cadence must not force cosmetic script rewrites."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import gate_opening_structure as gate


class CadenceAdvisoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = (ROOT / "docs/research/runs/american-debt-trap-20260920/"
                    "script-review/REVISED-V13-VO.txt").read_text(encoding="utf-8")

    def rows(self, text=None):
        rows, _ = gate.run(self.text if text is None else text, short=False)
        return {row.id: row for row in rows}

    def test_existing_long_gap_warns(self):
        row = self.rows()["G20"]
        self.assertEqual(row.level, "WARN")
        self.assertIn("34s", row.message)

    def test_missing_tags_warn_but_density_still_fails(self):
        rows = self.rows(self.text.replace("[new]", ""))
        self.assertEqual(rows["G20"].level, "WARN")
        self.assertEqual(rows["G22"].level, "FAIL")

    def test_in_range_passes(self):
        # Fixture-only annotation: do not alter the frozen production script.
        annotated = self.text.replace("[head-fake]", "[new] [head-fake]")
        self.assertEqual(self.rows(annotated)["G20"].level, "PASS")

    def test_hyphenated_take_tokens_do_not_shift_later_sentence(self):
        text = "Twenty-two dollars. Now compare."
        timeline = [
            {"w": "Twenty-two", "start": 0, "end": 1},
            {"w": "dollars.", "start": 1, "end": 2},
            {"w": "Now", "start": 3, "end": 4},
            {"w": "compare.", "start": 4, "end": 5},
        ]
        timed = gate._sentences_timed(text, timeline)
        self.assertEqual([(s[0], s[1]) for s in timed], [(0, 2), (3, 5)])


if __name__ == "__main__":
    unittest.main()
