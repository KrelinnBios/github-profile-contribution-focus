# GitHub Profile Contribution Focus

<p align="center">
  <strong>Repositories × Months · Contribution Focus · Automatic Updates</strong><br>
  Generate a concise 12-month code contribution timeline for a GitHub profile
</p>

<p align="center">
  <a href="https://github.com/KrelinnBios/github-profile-contribution-focus/releases"><img src="https://img.shields.io/github/v/release/KrelinnBios/github-profile-contribution-focus?style=flat-square&label=release&color=7F52FF" alt="Latest release"></a>
  <img src="https://img.shields.io/badge/platform-GitHub%20Actions-247344?style=flat-square" alt="GitHub Actions">
  <img src="https://img.shields.io/badge/license-MIT-1f5f9c?style=flat-square" alt="MIT License">
</p>

<p align="center">
  <a href="README.md">简体中文</a> ·
  <a href="README.zh-TW.md">繁體中文</a> ·
  <a href="README.en.md">English</a>
</p>

## Overview

GitHub Profile Contribution Focus is a reusable GitHub Action. It reads public commit contributions from the last 12 months and generates a repository-by-month SVG timeline, showing what someone worked on and how their project focus changed over the year.

The chart names the 5 repositories with the most commits. Every remaining repository is combined month by month into `Other`. The generated image stays in the profile repository and does not depend on an external image service.

## Features

- Twelve-month timeline: shows the current month and the preceding 11 calendar months.
- Repository rows: each row represents a repository, and each cell represents its commit contributions for one month.
- Relative intensity: four levels distinguish quiet and active months, while empty months use the theme track.
- Contribution focus: names the top 5 repositories by total commits and combines the rest month by month into `Other`.
- Commit totals: shows each repository's total for the period at the right.
- Theme support: one SVG automatically responds to GitHub light and dark themes.
- Cache handling: generates versioned filenames from content hashes and removes older charts automatically.

## Preview

<p align="center">
  <img src="examples/preview.svg" alt="Repository contribution focus over the last 12 months">
</p>

## Usage

### 1. Add an image placeholder to the profile README

```html
<p align="left">
  <img src="./contribution-focus.svg" alt="Contribution focus over the last 12 months" />
</p>
```

On the first run, the Action replaces the placeholder with a versioned filename such as `contribution-focus-a1b2c3d4e5f6.svg` to avoid stale GitHub image caches.

### 2. Add a configuration file

Copy [`examples/contribution-focus.config.json`](./examples/contribution-focus.config.json) to the profile repository root.

An empty object is enough inside the public repository whose name matches the account:

```json
{}
```

You can also select an account and override repository colors explicitly:

```json
{
  "owner": "YOUR_GITHUB_USERNAME",
  "excluded_repositories": [],
  "colors": {
    "YOUR_GITHUB_USERNAME/your-repository": "#7F52FF",
    "Other": "#8B949E"
  }
}
```

### 3. Add the update workflow

Copy [`examples/update-contribution-focus.yml`](./examples/update-contribution-focus.yml) to `.github/workflows/update-contribution-focus.yml` in the profile repository.

The core steps resolve and check out the latest stable release at runtime:

```yaml
- name: Resolve latest contribution focus release
  id: contribution-focus-release
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    release_tag=$(gh api repos/KrelinnBios/github-profile-contribution-focus/releases/latest --jq .tag_name)
    echo tag=$release_tag >> $GITHUB_OUTPUT

- name: Check out contribution focus action
  uses: actions/checkout@v4
  with:
    repository: KrelinnBios/github-profile-contribution-focus
    ref: ${{ steps.contribution-focus-release.outputs.tag }}
    path: .github/actions/github-profile-contribution-focus

- name: Generate contribution focus chart
  id: contribution-focus
  uses: ./.github/actions/github-profile-contribution-focus
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    config-path: contribution-focus.config.json
```

The example updates once a day and can also be run manually. No cross-repository token is required.

## Counting rules

- Data comes from the GitHub GraphQL API `contributionsCollection` field.
- Only commit contributions counted by GitHub are included; issue, pull request, and review counts are not mixed in.
- The range is the current UTC month plus the preceding 11 calendar months. The incomplete current month is bold and underlined.
- Each month is queried separately, so one repository can have at most 31 daily contribution nodes in a query and monthly data is not truncated by connection pagination.
- By default, only public contributions visible to the supplied token are included. Private repository names are never exposed in the chart.
- Ranking uses totals for the full period, while `Other` is aggregated separately for each month.

## Configuration

| Field | Default | Purpose |
| --- | --- | --- |
| `owner` | Current repository owner | GitHub username to analyze |
| `excluded_repositories` | `[]` | Repositories to ignore, as `owner/repo` or a short name |
| `colors` | Stable generated colors | Overrides keyed by full repository name, short name, or `Other` |
| `theme` | GitHub light/dark colors | Overrides for text and empty cells |

Full `owner/repo` color keys are recommended to avoid collisions between repositories with the same short name.

Theme fields are `light_text`, `light_muted`, `light_empty`, `dark_text`, `dark_muted`, and `dark_empty`.

## Action inputs and outputs

### Inputs

| Name | Required | Default | Purpose |
| --- | --- | --- | --- |
| `github-token` | Yes | None | Query public GitHub contribution data |
| `config-path` | No | `contribution-focus.config.json` | Configuration file path |
| `readme-path` | No | `README.md` | README whose image reference is updated |
| `output-directory` | No | `.` | SVG output directory |
| `output-prefix` | No | `contribution-focus` | Generated filename prefix |

### Outputs

| Name | Description |
| --- | --- |
| `image` | Path to the generated versioned SVG |
| `changed` | Whether the SVG, README reference, or old generated files changed |

## Versioning and Security

- Latest stable release: use the workflow above to resolve and check out the latest stable release through the Releases API.
- Full release tag: select and pin one from [Releases](https://github.com/KrelinnBios/github-profile-contribution-focus/releases) when upgrades should remain explicit.
- Full commit SHA: provides the strictest supply-chain reproducibility but requires manual update tracking.

The profile workflow uses `contents: write` only to commit the generated SVG and README. The Action does not write to other repositories.

## Development

The project uses only the Python standard library:

```bash
python -m unittest discover -s tests -v
python examples/generate_preview.py
```

## License

This project is released under the [MIT License](./LICENSE). Use, modification, distribution, and commercial use are permitted as long as the license and copyright notice are retained.

## Feedback and contributions

Use [GitHub Issues](https://github.com/KrelinnBios/github-profile-contribution-focus/issues) to report usage problems, ask about counting rules, suggest features, or propose other improvements.
