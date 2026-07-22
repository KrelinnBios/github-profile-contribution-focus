"""GitHub GraphQL access for repository contribution data."""

import json
import os
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from typing import Callable

from .dates import MonthWindow, github_datetime, month_windows_between

API_ROOT = os.environ.get("GITHUB_API_URL", "https://api.github.com").rstrip("/")

RANGE_QUERY = """
query ContributionFocusRange($login: String!) {
  user(login: $login) {
    contributionsCollection {
      startedAt
      endedAt
    }
  }
}
"""

MONTH_QUERY = """
query ContributionFocusMonth($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
      }
      commitContributionsByRepository(maxRepositories: 100) {
        repository {
          nameWithOwner
        }
        contributions(first: 31) {
          nodes {
            commitCount
          }
        }
      }
      issueContributionsByRepository(maxRepositories: 100) {
        repository {
          nameWithOwner
        }
        contributions {
          totalCount
        }
      }
      pullRequestContributionsByRepository(maxRepositories: 100) {
        repository {
          nameWithOwner
        }
        contributions {
          totalCount
        }
      }
      pullRequestReviewContributionsByRepository(maxRepositories: 100) {
        repository {
          nameWithOwner
        }
        contributions {
          totalCount
        }
      }
      repositoryContributions(first: 100) {
        nodes {
          repository {
            nameWithOwner
          }
        }
      }
    }
  }
}
"""


@dataclass(frozen=True)
class ContributionActivity:
    """Contribution counts before chart row aggregation."""

    repositories: dict[str, tuple[int, ...]]
    unattributed: tuple[int, ...]
    total_contributions: int
    repository_count: int


def repository_context(config: dict) -> str:
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    context_owner = os.environ.get("GITHUB_REPOSITORY_OWNER", "")
    if not context_owner and "/" in repository:
        context_owner = repository.split("/", 1)[0]

    owner = config["owner"] or context_owner
    if not owner:
        raise RuntimeError(
            "Unable to determine the GitHub username. Set owner in the configuration."
        )
    return owner


def graphql_endpoint(api_root: str = API_ROOT) -> str:
    root = api_root.rstrip("/")
    if root.endswith("/api/v3"):
        return f"{root[:-3]}/graphql"
    return f"{root}/graphql"


def github_graphql(query: str, variables: dict) -> dict:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN is required to query the GitHub GraphQL API.")

    payload = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    request = urllib.request.Request(
        graphql_endpoint(),
        data=payload,
        method="POST",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "github-profile-contribution-focus",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.load(response)
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"GitHub GraphQL request failed ({error.code}).\n{detail}"
        ) from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"GitHub GraphQL request failed: {error.reason}") from error

    if result.get("errors"):
        messages = "; ".join(
            str(item.get("message", item)) for item in result["errors"]
        )
        raise RuntimeError(f"GitHub GraphQL returned errors: {messages}")
    return result.get("data", {})


def _variables(owner: str, start, end) -> dict:
    return {
        "login": owner,
        "from": github_datetime(start),
        "to": github_datetime(end),
    }


def _collection(data: dict, owner: str) -> dict:
    user = data.get("user")
    if user is None:
        raise RuntimeError(f"GitHub user not found: {owner}")
    collection = user.get("contributionsCollection")
    if collection is None:
        raise RuntimeError(f"GitHub returned no contribution data for {owner}.")
    return collection


def _excluded(repository: str, excluded: set[str]) -> bool:
    normalized = repository.casefold()
    short_name = repository.rsplit("/", 1)[-1].casefold()
    return normalized in excluded or short_name in excluded


def contribution_windows(
    owner: str,
    client: Callable[[str, dict], dict] = github_graphql,
) -> list[MonthWindow]:
    """Return month buckets for GitHub's default past-year profile range."""

    collection = _collection(client(RANGE_QUERY, {"login": owner}), owner)
    start = datetime.fromisoformat(collection["startedAt"].replace("Z", "+00:00"))
    end = datetime.fromisoformat(collection["endedAt"].replace("Z", "+00:00"))
    return month_windows_between(start, end)


def _grouped_count(item: dict, field: str) -> int:
    if field == "commitContributionsByRepository":
        return sum(
            int(node.get("commitCount", 0))
            for node in item.get("contributions", {}).get("nodes", [])
        )
    return int(item.get("contributions", {}).get("totalCount", 0))


def fetch_activity(
    owner: str,
    windows: list[MonthWindow],
    config: dict,
    client: Callable[[str, dict], dict] = github_graphql,
) -> ContributionActivity:
    """Fetch and aggregate all GitHub profile contributions by repository."""

    if not windows:
        raise ValueError("at least one month window is required")

    def fetch_month(window: MonthWindow) -> dict:
        data = client(MONTH_QUERY, _variables(owner, window.start, window.end))
        return _collection(data, owner)

    worker_count = min(4, len(windows))
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        monthly_collections = list(executor.map(fetch_month, windows))

    month_count = len(windows)
    repository_months: dict[str, list[int]] = {}
    unattributed = [0] * month_count
    excluded = config["excluded_repositories"]

    for month_index, collection in enumerate(monthly_collections):
        known_total = 0
        grouped_fields = (
            "commitContributionsByRepository",
            "issueContributionsByRepository",
            "pullRequestContributionsByRepository",
            "pullRequestReviewContributionsByRepository",
        )
        for field in grouped_fields:
            for item in collection.get(field, []):
                repository = item["repository"]["nameWithOwner"]
                count = _grouped_count(item, field)
                known_total += count
                if count <= 0 or _excluded(repository, excluded):
                    continue
                repository_months.setdefault(repository, [0] * month_count)[
                    month_index
                ] += count

        for node in collection.get("repositoryContributions", {}).get("nodes", []):
            repository = node["repository"]["nameWithOwner"]
            known_total += 1
            if _excluded(repository, excluded):
                continue
            repository_months.setdefault(repository, [0] * month_count)[
                month_index
            ] += 1

        month_total = int(
            collection.get("contributionCalendar", {}).get(
                "totalContributions", known_total
            )
        )
        unattributed[month_index] = max(0, month_total - known_total)

    repositories = {
        repository: tuple(monthly)
        for repository, monthly in repository_months.items()
        if sum(monthly) > 0
    }
    included_total = sum(sum(monthly) for monthly in repositories.values()) + sum(
        unattributed
    )

    return ContributionActivity(
        repositories=repositories,
        unattributed=tuple(unattributed),
        total_contributions=included_total,
        repository_count=len(repositories),
    )
