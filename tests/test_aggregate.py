import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from contribution_focus.aggregate import build_rows


class BuildRowsTests(unittest.TestCase):
    def test_top_five_repositories_and_other(self):
        repositories = {
            "KrelinnBios/YamiboReaderLite": [60, 77],
            "KrelinnBios/NeoDBLite": [50, 75],
            "KrelinnBios/AceSurvey": [20, 25],
            "KrelinnBios/github-profile-language-donut": [21, 20],
            "KrelinnBios/KrelinnBios": [8, 10],
            "KrelinnBios/PrismSelf": [4, 2],
            "KrelinnBios/Tiny": [1, 2],
        }

        rows = build_rows(repositories, unattributed=[2, 1])

        self.assertEqual(6, len(rows))
        self.assertEqual(
            [
                "KrelinnBios/YamiboReaderLite",
                "KrelinnBios/NeoDBLite",
                "KrelinnBios/AceSurvey",
                "KrelinnBios/github-profile-language-donut",
                "KrelinnBios/KrelinnBios",
                "Other",
            ],
            [row.name for row in rows],
        )
        self.assertEqual((7, 5), rows[-1].monthly)
        self.assertEqual(12, rows[-1].total)

    def test_other_is_omitted_when_five_or_fewer_repositories_exist(self):
        repositories = {f"owner/repo-{index}": [index + 1] for index in range(5)}

        rows = build_rows(repositories)

        self.assertEqual(5, len(rows))
        self.assertNotIn("Other", [row.name for row in rows])

    def test_max_named_cannot_exceed_five(self):
        with self.assertRaises(ValueError):
            build_rows({}, max_named=6)


if __name__ == "__main__":
    unittest.main()
