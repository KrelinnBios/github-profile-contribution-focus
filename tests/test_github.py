import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from contribution_focus.dates import month_windows
from contribution_focus.github import (
    MONTH_QUERY,
    RANGE_QUERY,
    contribution_windows,
    fetch_activity,
    graphql_endpoint,
)


class GitHubDataTests(unittest.TestCase):
    def test_default_profile_range_is_used(self):
        def fake_client(query, variables):
            self.assertEqual(RANGE_QUERY, query)
            self.assertEqual({"login": "owner"}, variables)
            return {
                "user": {
                    "contributionsCollection": {
                        "startedAt": "2025-07-20T00:00:00Z",
                        "endedAt": "2026-07-22T09:30:00Z",
                    }
                }
            }

        windows = contribution_windows("owner", client=fake_client)

        self.assertEqual(13, len(windows))
        self.assertEqual("2025-07", windows[0].key)
        self.assertEqual("2026-07", windows[-1].key)

    def test_monthly_contributions_and_exclusions_are_aggregated(self):
        windows = month_windows(
            datetime(2026, 7, 22, tzinfo=timezone.utc), count=2
        )

        def fake_client(query, variables):
            self.assertEqual(MONTH_QUERY, query)
            first_month = variables["from"].startswith("2026-06")
            commits = (
                [
                    ("owner/A", [4]),
                    ("owner/B", [1]),
                    ("owner/Hidden", [1]),
                ]
                if first_month
                else [("owner/A", [1]), ("owner/D", [1])]
            )
            grouped = (
                {
                    "issueContributionsByRepository": [
                        ("owner/A", 2),
                        ("community/shared", 1),
                    ],
                    "pullRequestContributionsByRepository": [("owner/B", 1)],
                    "pullRequestReviewContributionsByRepository": [
                        ("community/shared", 1)
                    ],
                }
                if first_month
                else {
                    "issueContributionsByRepository": [("community/shared", 1)],
                    "pullRequestContributionsByRepository": [("owner/A", 1)],
                    "pullRequestReviewContributionsByRepository": [("owner/D", 2)],
                }
            )
            return {
                "user": {
                    "contributionsCollection": {
                        "contributionCalendar": {
                            "totalContributions": 13 if first_month else 7
                        },
                        "commitContributionsByRepository": [
                            {
                                "repository": {"nameWithOwner": name},
                                "contributions": {
                                    "nodes": [
                                        {"commitCount": count} for count in counts
                                    ]
                                },
                            }
                            for name, counts in commits
                        ],
                        **{
                            field: [
                                {
                                    "repository": {"nameWithOwner": name},
                                    "contributions": {"totalCount": count},
                                }
                                for name, count in contributions
                            ]
                            for field, contributions in grouped.items()
                        },
                        "repositoryContributions": {
                            "nodes": (
                                [
                                    {
                                        "repository": {
                                            "nameWithOwner": "owner/New"
                                        }
                                    }
                                ]
                                if first_month
                                else []
                            )
                        },
                    }
                }
            }

        activity = fetch_activity(
            "owner",
            windows,
            {"excluded_repositories": {"owner/hidden"}},
            client=fake_client,
        )

        self.assertEqual((6, 2), activity.repositories["owner/A"])
        self.assertEqual((2, 0), activity.repositories["owner/B"])
        self.assertEqual((2, 1), activity.repositories["community/shared"])
        self.assertEqual((0, 3), activity.repositories["owner/D"])
        self.assertEqual((1, 0), activity.repositories["owner/New"])
        self.assertNotIn("owner/Hidden", activity.repositories)
        self.assertEqual((1, 1), activity.unattributed)
        self.assertEqual(19, activity.total_contributions)
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
