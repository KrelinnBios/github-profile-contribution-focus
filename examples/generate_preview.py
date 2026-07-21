#!/usr/bin/env python3
"""Regenerate the deterministic README preview."""

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "src"))

from contribution_focus.aggregate import FocusRow
from contribution_focus.chart import build_svg
from contribution_focus.config import DEFAULT_COLORS, DEFAULT_THEME
from contribution_focus.dates import month_windows


def main():
    months = month_windows(datetime(2026, 7, 22, tzinfo=timezone.utc))
    rows = [
        FocusRow(
            "KrelinnBios/YamiboReaderLite",
            (4, 7, 12, 16, 21, 18, 10, 6, 3, 4, 14, 22),
        ),
        FocusRow(
            "KrelinnBios/NeoDBLite",
            (0, 2, 5, 9, 14, 21, 24, 18, 12, 8, 4, 8),
        ),
        FocusRow(
            "KrelinnBios/AceSurvey",
            (3, 5, 8, 6, 2, 0, 0, 1, 4, 7, 6, 3),
        ),
        FocusRow(
            "KrelinnBios/github-profile-language-donut",
            (0, 0, 0, 0, 0, 0, 0, 0, 2, 8, 17, 14),
        ),
        FocusRow(
            "KrelinnBios/KrelinnBios",
            (0, 0, 0, 0, 0, 0, 0, 0, 1, 3, 5, 9),
        ),
        FocusRow("Other", (0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3), True),
    ]
    config = {
        "theme": DEFAULT_THEME.copy(),
        "colors": {
            **DEFAULT_COLORS,
            "KrelinnBios/YamiboReaderLite": "#7F52FF",
            "KrelinnBios/NeoDBLite": "#00B8D9",
            "KrelinnBios/AceSurvey": "#22C55E",
            "KrelinnBios/github-profile-language-donut": "#EC4899",
            "KrelinnBios/KrelinnBios": "#F59E0B",
        },
    }
    (ROOT / "examples" / "preview.svg").write_text(
        build_svg(rows, months, 6, config), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
