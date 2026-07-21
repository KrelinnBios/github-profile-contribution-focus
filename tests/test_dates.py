import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from contribution_focus.dates import github_datetime, month_windows


class MonthWindowTests(unittest.TestCase):
    def test_last_twelve_months_include_current_month(self):
        now = datetime(2026, 7, 22, 9, 30, tzinfo=timezone.utc)

        windows = month_windows(now)

        self.assertEqual(12, len(windows))
        self.assertEqual("2025-08", windows[0].key)
        self.assertEqual("08", windows[0].label)
        self.assertEqual("2026-07", windows[-1].key)
        self.assertEqual(now, windows[-1].end)
        self.assertTrue(windows[-1].current)
        self.assertEqual(1, sum(window.current for window in windows))

    def test_completed_month_ends_at_last_second(self):
        now = datetime(2026, 7, 22, tzinfo=timezone.utc)

        june = month_windows(now)[-2]

        self.assertEqual(
            datetime(2026, 6, 30, 23, 59, 59, tzinfo=timezone.utc), june.end
        )
        self.assertEqual("2026-06-30T23:59:59Z", github_datetime(june.end))

    def test_count_must_be_positive(self):
        with self.assertRaises(ValueError):
            month_windows(count=0)


if __name__ == "__main__":
    unittest.main()
