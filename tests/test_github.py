import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from contribution_focus.dates import month_windows
from contribution_focus.github import (
    MONTH_QUERY,
    SUMMARY_QUERY,
    fetch_activity,
    graphql_endpoint,
)


class GitHubDataTests(unittest.TestCase):
    def test_monthly_contributions_and_exclusions_are_aggregated(self):
        windows = month_windows(
            datetime(2026, 7, 22, tzinfo=timezone.utc), count=2
        )

        def fake_client(query, variables):
            if query == SUMMARY_QUERY:
                return {
                    "user": {
                        "contributionsCollection": {
                            "totalCommitContributions": 9,
                            "totalRepositoriesWithContributedCommits": 6,
                        }
                    }
                }

            self.assertEqual(MONTH_QUERY, query)
            first_month = variables["from"].startswith("2026-06")
            repositories = (
                [
                    ("owner/A", [4]),
                    ("owner/B", [1]),
                    ("owner/Hidden", [1]),
                ]
                if first_month
                else [("owner/A", [1]), ("owner/D", [1])]
            )
            return {
                "user": {
                    "contributionsCollection": {
                        "totalCommitContributions": 6 if first_month else 3,
                        "commitContributionsByRepository": [
                            {
                                "repository": {"nameWithOwner": name},
                                "contributions": {
                                    "nodes": [
                                        {"commitCount": count} for count in counts
                                    ]
                                },
                            }
                            for name, counts in repositories
                        ],
                    }
                }
            }

        activity = fetch_activity(
            "owner",
            windows,
            {"excluded_repositories": {"owner/hidden"}},
            client=fake_client,
        )

        self.assertEqual((4, 1), activity.repositories["owner/A"])
        self.assertEqual((1, 0), activity.repositories["owner/B"])
        self.assertEqual((0, 1), activity.repositories["owner/D"])
        self.assertEqual((0, 1), activity.unattributed)
        self.assertEqual(8, activity.total_commits)
        self.assertEqual(5, activity.repository_count)

    def test_graphql_endpoint_supports_dotcom_and_enterprise(self):
        self.assertEqual(
            "https://api.github.com/graphql",
            graphql_endpoint("https://api.github.com"),
        )
        self.assertEqual(
            "https://github.example/api/graphql",
            graphql_endpoint("https://github.example/api/v3"),
        )


if __name__ == "__main__":
    unittest.main()
