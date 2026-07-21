#!/usr/bin/env python3
"""Generate a versioned SVG contribution focus chart for a GitHub profile."""

import argparse
from datetime import datetime, timezone
from pathlib import Path

from contribution_focus.aggregate import build_rows
from contribution_focus.chart import build_svg
from contribution_focus.config import load_config
from contribution_focus.dates import month_windows
from contribution_focus.github import fetch_activity, repository_context
from contribution_focus.output import set_action_outputs, write_outputs


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="contribution-focus.config.json")
    parser.add_argument("--readme", default="README.md")
    parser.add_argument("--output-directory", default=".")
    parser.add_argument("--output-prefix", default="contribution-focus")
    return parser.parse_args()


def main():
    args = parse_args()
    config = load_config(Path(args.config))
    owner = repository_context(config)
    months = month_windows(datetime.now(timezone.utc))
    activity = fetch_activity(owner, months, config)
    rows = build_rows(activity.repositories, activity.unattributed)
    svg = build_svg(rows, months, activity.repository_count, config)
    image, changed = write_outputs(
        svg,
        Path(args.readme),
        Path(args.output_directory),
        args.output_prefix,
    )
    set_action_outputs(image, changed)
    state = "changed" if changed else "unchanged"
    print(f"Generated {image.as_posix()} ({state}).")


if __name__ == "__main__":
    main()
