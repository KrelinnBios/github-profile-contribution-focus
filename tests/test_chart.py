import re
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from contribution_focus.aggregate import FocusRow
from contribution_focus.chart import build_svg, intensity_level
from contribution_focus.config import DEFAULT_COLORS, DEFAULT_THEME
from contribution_focus.dates import month_windows


def config():
    return {
        "theme": DEFAULT_THEME.copy(),
        "colors": DEFAULT_COLORS.copy(),
    }


class BuildSvgTests(unittest.TestCase):
    def setUp(self):
        self.months = month_windows(
            datetime(2026, 7, 22, tzinfo=timezone.utc)
        )

    def test_chart_renders_five_repositories_and_other(self):
        rows = [
            FocusRow(
                f"KrelinnBios/Repository-{index}",
                tuple(index + month for month in range(12)),
            )
            for index in range(1, 6)
        ]
        rows.append(FocusRow("Other", (1,) * 12, is_other=True))

        svg = build_svg(rows, self.months, 8, config())

        self.assertIn("Contribution Focus · Last 12 Months", svg)
        self.assertIn("8 repositories", svg)
        self.assertIn(">Other</text>", svg)
        self.assertEqual(72, len(re.findall(r'<rect class="cell(?: |\-)', svg)))
        self.assertEqual(6, len(re.findall(r'<text class="total"', svg)))
        self.assertIn("@media (prefers-color-scheme: dark)", svg)
        self.assertIn('class="month current-month"', svg)
        self.assertIn('class="current-marker"', svg)

    def test_duplicate_short_names_use_full_repository_name(self):
        rows = [
            FocusRow("first/shared", (1,) * 12),
            FocusRow("second/shared", (2,) * 12),
        ]

        svg = build_svg(rows, self.months, 2, config())

        self.assertIn(">first/shared</text>", svg)
        self.assertIn(">second/shared</text>", svg)

    def test_empty_data_has_a_clear_zero_state(self):
        svg = build_svg([], self.months, 0, config())

        self.assertIn("No public commit contributions", svg)
        self.assertNotIn('<text class="total"', svg)

    def test_intensity_is_relative_and_keeps_small_values_visible(self):
        self.assertEqual(0, intensity_level(0, 100))
        self.assertEqual(1, intensity_level(1, 100))
        self.assertEqual(2, intensity_level(25, 100))
        self.assertEqual(3, intensity_level(50, 100))
        self.assertEqual(4, intensity_level(100, 100))

    def test_requires_twelve_months(self):
        with self.assertRaises(ValueError):
            build_svg([], self.months[:-1], 0, config())


if __name__ == "__main__":
    unittest.main()
