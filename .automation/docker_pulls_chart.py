#!/usr/bin/env python3
"""
Generate docs/assets/images/docker-pulls-monthly.svg.

The chart is a line of the monthly totals of new Docker pulls across all
MegaLinter images (main image, flavors and standalone megalinter-only-*
images) on all registries (Docker Hub + ghcr.io) and all historical image
names, from the creation of the repository (October 2020) until today.

Historical points are frozen in
.automation/generated/docker-pulls-monthly.json: they were computed once from
the tracked stats plus a Web Archive reconstruction of the periods where
stats collection was interrupted, and never need recalculation. This script
only appends newly completed months, computed from flavors-stats.json (kept
up to date by the auto-update workflow), stores them in the same file, and
renders the SVG. The displayed line never decreases: a new month lower than
the previous point is clamped to it.

Pure stdlib (SVG is written by hand): no extra dependency and no network call
is needed in the auto-update workflow. Called by build.py right after
update_docker_pulls_counter() so the image is refreshed with the freshly
collected stats.

Usage:
    python .automation/docker_pulls_chart.py
"""

import json
import logging
import os

REPO_HOME = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + ".."
DOCKER_STATS_FILE = REPO_HOME + "/.automation/generated/flavors-stats.json"
MONTHLY_POINTS_FILE = REPO_HOME + "/.automation/generated/docker-pulls-monthly.json"
OUTPUT_SVG_FILE = REPO_HOME + "/docs/assets/images/docker-pulls-monthly.svg"

# Colors: dataviz-validated palette on light surface
COLOR_SURFACE = "#fcfcfb"
COLOR_INK = "#0b0b0b"
COLOR_INK_2 = "#52514e"
COLOR_MUTED = "#898781"
COLOR_GRID = "#e1e0d9"
COLOR_BASELINE = "#c3c2b7"
COLOR_SERIES = "#2a78d6"

FONT = "font-family=\"system-ui,-apple-system,'Segoe UI',sans-serif\""

# Ratio under which a snapshot is considered a failed fetch (registry API
# returned 0 or a partial sum) and dropped: cumulative counts never shrink
GLITCH_RATIO = 0.6


def month_add(month: str, delta: int) -> str:
    year, mon = int(month[:4]), int(month[5:7])
    mon += delta
    while mon > 12:
        mon, year = mon - 12, year + 1
    while mon < 1:
        mon, year = mon + 12, year - 1
    return f"{year:04d}-{mon:02d}"


def human_format(num: float) -> str:
    if num >= 1_000_000:
        value = num / 1_000_000
        return f"{value:.2f}M" if value < 10 else f"{value:.1f}M"
    if num >= 1_000:
        return f"{round(num / 1_000)}k"
    return str(round(num))


def load_tracked_stats() -> tuple[dict, set, int, str]:
    with open(DOCKER_STATS_FILE, "r", encoding="utf-8") as f:
        docker_stats = json.load(f)

    # Per image: last cleaned cumulative count of each tracked month
    last_snapshot_date = ""
    per_image_month: dict[str, dict[str, int]] = {}
    for image_key, series in docker_stats.items():
        month_values: dict[str, int] = {}
        running_max = 0
        for iso_date, count in series:
            if count < GLITCH_RATIO * running_max:
                continue
            running_max = max(running_max, count)
            month_values[iso_date[:7]] = count
            last_snapshot_date = max(last_snapshot_date, iso_date[:10])
        per_image_month[image_key] = month_values

    observed_months = {month for values in per_image_month.values() for month in values}
    total_pulls = sum(
        values[max(values)] for values in per_image_month.values() if values
    )
    return per_image_month, observed_months, total_pulls, last_snapshot_date


def append_new_months(points: list) -> bool:
    per_image_month, observed_months, _, last_snapshot_date = load_tracked_stats()
    current_month = last_snapshot_date[:7]  # still being collected: skip
    updated = False
    month = month_add(points[-1][0], 1)
    while month in observed_months and month < current_month:
        previous_month = month_add(month, -1)
        if previous_month not in observed_months:
            logging.warning(f"No stats for {previous_month}: cannot append {month}")
            break
        delta = 0
        for month_values in per_image_month.values():
            if month in month_values and previous_month in month_values:
                delta += month_values[month] - month_values[previous_month]
        points.append([month, max(delta, points[-1][1])])
        updated = True
        month = month_add(month, 1)
    return updated


def nice_ceiling(value: float) -> float:
    magnitude = 10 ** (len(str(int(value))) - 1)
    for factor in [1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10]:
        if factor * magnitude >= value:
            return factor * magnitude
    return 10 * magnitude


def svg_text(x: float, y: float, content: str, **attrs) -> str:
    attributes = " ".join(
        f'{key.replace("_", "-")}="{value}"' for key, value in attrs.items()
    )
    return f'<text x="{x:.1f}" y="{y:.1f}" {FONT} {attributes}>{content}</text>'


def svg_line(x1: float, y1: float, x2: float, y2: float, stroke: str) -> str:
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="{stroke}" stroke-width="1"/>'
    )


def build_svg(points: list, total_pulls: int) -> str:
    width = 1200
    margin_left, margin_right = 70, 80
    plot_w = width - margin_left - margin_right
    n = len(points)
    slot = plot_w / n

    plot_top, plot_h = 95, 330
    axis_y = plot_top + plot_h
    height = 470

    def x_center(index: int) -> float:
        return margin_left + slot * index + slot / 2

    y_max = nice_ceiling(max(value for _, value in points))

    def y_pos(value: float) -> float:
        return axis_y - (value / y_max) * plot_h

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img" '
        'aria-label="New MegaLinter Docker image pulls per month">',
        f'<rect width="{width}" height="{height}" fill="{COLOR_SURFACE}"/>',
        svg_text(
            margin_left,
            40,
            "MegaLinter Docker pulls per month",
            font_size=22,
            font_weight=650,
            fill=COLOR_INK,
        ),
        svg_text(
            margin_left,
            62,
            f"New pulls per month, all images (main + flavors + standalone), "
            f"all registries and historical image names - "
            f"{human_format(total_pulls)} pulls in total",
            font_size=13,
            fill=COLOR_INK_2,
        ),
    ]

    # Horizontal gridlines + y-axis tick labels
    for tick in range(5):
        value = tick * y_max / 4
        y = y_pos(value)
        color = COLOR_BASELINE if tick == 0 else COLOR_GRID
        parts.append(svg_line(margin_left, y, margin_left + plot_w, y, color))
        if tick > 0:
            parts.append(
                svg_text(
                    margin_left - 8,
                    y + 4,
                    human_format(value),
                    font_size=11,
                    fill=COLOR_MUTED,
                    text_anchor="end",
                )
            )

    # Area wash under the line (series hue at ~10% opacity)
    area_points = " ".join(
        f"L{x_center(i):.1f},{y_pos(points[i][1]):.1f}" for i in range(n)
    )
    parts.append(
        f'<path d="M{x_center(0):.1f},{axis_y:.1f} {area_points} '
        f'L{x_center(n - 1):.1f},{axis_y:.1f} Z" '
        f'fill="{COLOR_SERIES}" fill-opacity="0.10"/>'
    )

    # Continuous line
    line_points = " ".join(
        f"{x_center(i):.1f},{y_pos(points[i][1]):.1f}" for i in range(n)
    )
    parts.append(
        f'<polyline points="{line_points}" fill="none" '
        f'stroke="{COLOR_SERIES}" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round"/>'
    )

    # End marker (surface ring + dot) and latest value label
    end_x, end_y = x_center(n - 1), y_pos(points[n - 1][1])
    parts.append(
        f'<circle cx="{end_x:.1f}" cy="{end_y:.1f}" r="6" ' f'fill="{COLOR_SURFACE}"/>'
    )
    parts.append(
        f'<circle cx="{end_x:.1f}" cy="{end_y:.1f}" r="4" ' f'fill="{COLOR_SERIES}"/>'
    )
    parts.append(
        svg_text(
            end_x + 10,
            end_y + 4,
            f"+{human_format(points[n - 1][1])}",
            font_size=12,
            font_weight=650,
            fill=COLOR_INK,
        )
    )

    # X axis: one tick per year (January)
    for i, (month, _) in enumerate(points):
        if month.endswith("-01"):
            parts.append(
                svg_line(x_center(i), axis_y, x_center(i), axis_y + 4, COLOR_BASELINE)
            )
            parts.append(
                svg_text(
                    x_center(i),
                    axis_y + 18,
                    month[:4],
                    font_size=11,
                    fill=COLOR_MUTED,
                    text_anchor="middle",
                )
            )

    parts.append("</svg>")
    return "\n".join(parts)


def generate_docker_pulls_chart():
    with open(MONTHLY_POINTS_FILE, "r", encoding="utf-8") as f:
        points = json.load(f)

    if append_new_months(points):
        with open(MONTHLY_POINTS_FILE, "w", encoding="utf-8") as f:
            json.dump(points, f, indent=1)

    _, _, total_pulls, _ = load_tracked_stats()
    svg = build_svg(points, total_pulls)
    with open(OUTPUT_SVG_FILE, "w", encoding="utf-8") as f:
        f.write(svg)
    logging.info(
        f"Generated {OUTPUT_SVG_FILE} "
        f"({len(points)} months, {total_pulls:,} total pulls)"
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    generate_docker_pulls_chart()
