"""Render the repository-by-month contribution focus SVG."""

import html
import math
from collections import Counter

from .aggregate import FocusRow
from .colors import color_for
from .dates import MonthWindow

FONT_STACK = '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'


def intensity_level(value: int, maximum: int) -> int:
    """Map a non-negative count to one of four visible intensity levels."""

    if value <= 0 or maximum <= 0:
        return 0
    return min(4, max(1, math.ceil(math.sqrt(value / maximum) * 4)))


def _short_name(repository: str) -> str:
    return repository.rsplit("/", 1)[-1]


def _truncate(value: str, limit: int = 21) -> str:
    if len(value) <= limit:
        return value
    return f"{value[: limit - 1]}…"


def _display_labels(rows: list[FocusRow]) -> dict[str, str]:
    short_names = Counter(_short_name(row.name).casefold() for row in rows)
    labels = {}
    for row in rows:
        short_name = _short_name(row.name)
        label = (
            row.name
            if not row.is_other and short_names[short_name.casefold()] > 1
            else short_name
        )
        labels[row.name] = _truncate(label)
    return labels


def build_svg(
    rows: list[FocusRow],
    months: list[MonthWindow],
    repository_count: int,
    config: dict,
) -> str:
    if not months:
        raise ValueError("the contribution focus chart requires at least one month")
    if any(len(row.monthly) != len(months) for row in rows):
        raise ValueError("each repository row must match the month count")

    theme = config["theme"]
    colors = config["colors"]
    total_contributions = sum(row.total for row in rows)
    labels = _display_labels(rows)

    padding_x = 24
    label_width = 178
    cell_size = 18
    cell_gap = 6
    row_height = 32
    header_y = 58
    grid_y = 72
    grid_x = padding_x + label_width
    grid_width = len(months) * cell_size + (len(months) - 1) * cell_gap
    total_value_x = grid_x + grid_width + 58
    width = total_value_x + padding_x
    height = grid_y + max(1, len(rows)) * row_height + 16

    repository_word = "repository" if repository_count == 1 else "repositories"
    subtitle = (
        f"{total_contributions} contributions across "
        f"{repository_count} {repository_word}"
        if total_contributions
        else "No visible contributions in the past year"
    )

    positive_values = [value for row in rows for value in row.monthly if value > 0]
    maximum = max(positive_values, default=0)

    month_elements = []
    for index, month in enumerate(months):
        x = grid_x + index * (cell_size + cell_gap) + cell_size / 2
        css_class = "month current-month" if month.current else "month"
        month_elements.append(
            f'    <text class="{css_class}" x="{x:.1f}" y="{header_y}" '
            f'text-anchor="middle">{month.label}</text>'
        )
        if month.current:
            month_elements.append(
                f'    <rect class="current-marker" x="{x - 7:.1f}" '
                f'y="{header_y + 6}" width="14" height="2" rx="1" />'
            )

    row_elements = []
    descriptions = []
    for row_index, row in enumerate(rows):
        y = grid_y + row_index * row_height
        label = labels[row.name]
        color = color_for(row.name, colors)
        row_elements.append(
            f'    <text class="repo-label" x="{padding_x}" y="{y + 14}">'
            f'{html.escape(label)}</text>'
        )
        for month_index, value in enumerate(row.monthly):
            x = grid_x + month_index * (cell_size + cell_gap)
            level = intensity_level(value, maximum)
            css_class = "cell-empty" if level == 0 else f"cell level-{level}"
            fill = "" if level == 0 else f' fill="{color}"'
            tooltip = html.escape(
                f"{label} · {months[month_index].key}: {value} contributions"
            )
            row_elements.append(
                f'    <rect class="{css_class}" x="{x}" y="{y}" '
                f'width="{cell_size}" height="{cell_size}" rx="3"{fill}>'
                f"<title>{tooltip}</title></rect>"
            )
        row_elements.append(
            f'    <text class="total" x="{total_value_x}" y="{y + 14}" '
            f'text-anchor="end">{row.total}</text>'
        )
        descriptions.append(f"{label} {row.total}")

    description = html.escape(
        f"Contribution focus from {months[0].start:%Y-%m-%d} "
        f"through {months[-1].end:%Y-%m-%d}. "
        + (", ".join(descriptions) if descriptions else subtitle)
        + "."
    )

    grid_content = ""
    if rows:
        grid_content = f'''
  <g aria-hidden="true">
{chr(10).join(month_elements)}
    <text class="month" x="{total_value_x}" y="{header_y}" text-anchor="end">Total</text>
{chr(10).join(row_elements)}
  </g>'''

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">Contribution Focus · Last Year</title>
  <desc id="desc">{description}</desc>
  <style>
    .subtitle {{ fill: {theme["light_muted"]}; font: 400 14px {FONT_STACK}; }}
    .repo-label {{ fill: {theme["light_text"]}; font: 500 14px {FONT_STACK}; }}
    .month, .total {{ fill: {theme["light_muted"]}; font: 500 12px {FONT_STACK}; }}
    .current-month {{ fill: {theme["light_text"]}; font-weight: 700; }}
    .current-marker {{ fill: {theme["light_text"]}; opacity: 0.55; }}
    .cell-empty {{ fill: {theme["light_empty"]}; opacity: 0.34; }}
    .level-1 {{ fill-opacity: 0.28; }}
    .level-2 {{ fill-opacity: 0.50; }}
    .level-3 {{ fill-opacity: 0.74; }}
    .level-4 {{ fill-opacity: 1; }}
    @media (prefers-color-scheme: dark) {{
      .repo-label, .current-month {{ fill: {theme["dark_text"]}; }}
      .subtitle, .month, .total {{ fill: {theme["dark_muted"]}; }}
      .current-marker {{ fill: {theme["dark_text"]}; }}
      .cell-empty {{ fill: {theme["dark_empty"]}; opacity: 0.72; }}
    }}
  </style>

  <text class="subtitle" x="{padding_x}" y="28">{html.escape(subtitle)}</text>{grid_content}
</svg>'''
