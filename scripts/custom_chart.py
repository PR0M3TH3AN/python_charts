#!/usr/bin/env python3
"""custom_chart.py
------------------
Plot arbitrary FRED series stored in ``data/fred.db``.

Example:
    python scripts/custom_chart.py --series UNRATE DCOILWTICO --start 2000-01-01 --end 2020-12-31
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Iterable

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from common import fetch_series_db, save_figure

def fetch_series_multi(
    series: Iterable[str],
    start: datetime,
    end: datetime,
    db_path: str | Path = Path("data/fred.db"),
) -> pd.DataFrame:
    """Load one or more FRED series from a local SQLite DB."""
    return fetch_series_db(series, start, end, db_path)


def plot_series(df: pd.DataFrame) -> plt.Figure:
    """Plot each column of ``df`` on a shared axis."""
    fig, ax = plt.subplots(figsize=(10, 5))
    for col in df.columns:
        ax.plot(df.index, df[col], label=col)

    ax.set_xlabel("Date")
    ax.set_ylabel("Value")
    ax.legend(frameon=False)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.xaxis.set_major_locator(mdates.YearLocator(base=5))
    ax.xaxis.set_minor_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    fig.autofmt_xdate()
    fig.tight_layout()
    return fig


def main(argv: list[str] | None = None) -> plt.Figure:
    p = argparse.ArgumentParser(description="Plot FRED series from a local DB")
    p.add_argument("--series", nargs="+", required=True, help="FRED series names")
    p.add_argument(
        "--start", type=str, default="1970-01-01", help="start date YYYY-MM-DD"
    )
    p.add_argument(
        "--end",
        type=str,
        default=datetime.today().strftime("%Y-%m-%d"),
        help="end date YYYY-MM-DD",
    )
    p.add_argument("--db", type=str, default="data/fred.db", help="path to SQLite DB")
    p.add_argument(
        "--output",
        type=str,
        default=None,
        help="optional path to save the figure (PNG or PDF)",
    )
    args = p.parse_args(argv)

    start_dt = datetime.fromisoformat(args.start)
    end_dt = datetime.fromisoformat(args.end)

    data = fetch_series_multi(args.series, start_dt, end_dt, args.db)
    fig = plot_series(data)

    save_figure(fig, args.output, __file__)
    if argv is None:
        fig.show()
    return fig


if __name__ == "__main__":
    main()
