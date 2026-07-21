import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from contribution_focus.output import write_outputs


class OutputTests(unittest.TestCase):
    def test_versioned_output_replaces_readme_and_cleans_old_images(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            readme = root / "README.md"
            old_image = root / "contribution-focus-000000000000.svg"
            readme.write_text(
                '<img src="./contribution-focus-000000000000.svg" alt="chart" />',
                encoding="utf-8",
            )
            old_image.write_text("old", encoding="utf-8")

            image, changed = write_outputs(
                "<svg></svg>", readme, root, "contribution-focus"
            )

            self.assertTrue(changed)
            self.assertTrue(image.exists())
            self.assertFalse(old_image.exists())
            self.assertIn(image.name, readme.read_text(encoding="utf-8"))

    def test_missing_placeholder_has_a_clear_error(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            readme = root / "README.md"
            readme.write_text("# Profile", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "No contribution focus"):
                write_outputs("<svg></svg>", readme, root, "contribution-focus")


if __name__ == "__main__":
    unittest.main()
