import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from contribution_focus.config import load_config


class ConfigTests(unittest.TestCase):
    def test_user_settings_extend_defaults(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(
                json.dumps(
                    {
                        "owner": "KrelinnBios",
                        "excluded_repositories": ["Owner/Hidden"],
                        "colors": {"Owner/Repo": "#123456"},
                        "theme": {"dark_text": "#FFFFFF"},
                    }
                ),
                encoding="utf-8",
            )

            result = load_config(path)

            self.assertEqual("KrelinnBios", result["owner"])
            self.assertEqual({"owner/hidden"}, result["excluded_repositories"])
            self.assertEqual("#123456", result["colors"]["Owner/Repo"])
            self.assertEqual("#FFFFFF", result["theme"]["dark_text"])
            self.assertIn("light_text", result["theme"])


if __name__ == "__main__":
    unittest.main()
