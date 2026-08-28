import re
from pathlib import Path

import matplotlib.pyplot as plt

from fdi.numbers import parse_scaled_number

YEAR_PATTERN = re.compile(r"(19|20)\d{2}")


def parse_fiscal_year(fiscal_period: str) -> int | None:
    """Extract the fiscal year a fact's period string refers to, e.g. 'Year Ended December 31, 2025' -> 2025."""
    years = [int(match.group()) for match in YEAR_PATTERN.finditer(fiscal_period)]
    return max(years) if years else None


def build_metric_series(facts: list[dict], metric_name: str) -> dict[int, float]:
    """Collect (year -> value) for every fact whose metric name exactly matches (case-insensitive)."""
    series: dict[int, float] = {}
    for fact in facts:
        if fact["metric"].strip().lower() != metric_name.strip().lower():
            continue
        year = parse_fiscal_year(fact["fiscal_period"])
        value = parse_scaled_number(fact["value"])
        if year is not None and value is not None:
            series[year] = value
    return series


def plot_metric_trend(metric_name: str, series: dict[int, float], output_path: Path) -> None:
    """Render a bar chart of a metric's year-over-year values and save it as a PNG."""
    years = sorted(series)
    values = [series[year] for year in years]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar([str(year) for year in years], values, color="#2563eb")
    ax.set_title(metric_name)
    ax.set_ylabel("USD")
    fig.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
