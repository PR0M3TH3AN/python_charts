#!/usr/bin/env python3
"""bitcoin_m2_chart.py
----------------------
Plot Bitcoin price (log scale) versus global M2 money supply (as a 100-point index)
stored in `data/fred.db`. Bitcoin is orange; M2 is green; white background; monthly x-ticks.
"""

from __future__ import annotations
import argparse
from datetime import datetime
from pathlib import Path
from typing import Tuple
import sys

from scripts.constants import DB_PATH_DEFAULT

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from dateutil.relativedelta import relativedelta

# IMPORTANT: use the package-qualified import
from scripts.common import (
    fetch_series_db,
    save_figure,
    validate_dataframe,
    validate_overlap,
)


def fetch_series(
    start: datetime,
    end: datetime,
    btc_series: str,
    m2_series: str,
    db_path: str | Path = DB_PATH_DEFAULT,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load Bitcoin and M2 series from a local SQLite DB."""
    df = fetch_series_db([btc_series, m2_series], start, end, db_path)
    btc = df[[btc_series]].rename(columns={btc_series: "value"})
    m2 = df[[m2_series]].rename(columns={m2_series: "value"})
    return btc, m2


def validate_series(
    btc: pd.DataFrame, m2: pd.DataFrame, btc_name: str, m2_name: str
) -> None:
    """Run basic sanity checks on the two series."""
    validate_dataframe(btc, btc_name)
    validate_dataframe(m2, m2_name)
    validate_overlap(btc, m2)


def plot_bitcoin_m2(
    btc: pd.DataFrame,
    m2: pd.DataFrame,
    offset_days: int,
    extend_years: int,
    *,
    width: float = 12,
    height: float = 6,
    dpi: int | None = None,
) -> plt.Figure:
    """
    Plot Bitcoin price (log scale) and a rebased (100-point) M2 index on dual axes:
      • Bitcoin is orange, on a log-scaled left y-axis
      • Global M2 is green, on a linear right y-axis
      • White background, monthly x-ticks, with an “empty buffer” past the last date.
    """
    # 1) Determine overlapping date range
    common_start = max(btc.index.min(), m2.index.min())
    common_end = min(btc.index.max(), m2.index.max())

    btc_common = btc.loc[common_start:common_end].dropna(subset=["value"])
    m2_common = m2.loc[common_start:common_end].dropna(subset=["value"])

    # 2) Shift M2 by `offset_days`
    m2_shifted = m2_common.shift(offset_days)

    # 3) Rebase M2 to a 100-point index
    #    (so that at the first available date, M2_index = 100)
    m2_indexed = (m2_shifted["value"] / m2_shifted["value"].iloc[0]) * 100

    # 4) Create figure + axes
    fig, ax1 = plt.subplots(figsize=(width, height), dpi=dpi)
    # (White background is default, so no style override is needed.)

    # 5) Plot Bitcoin (orange) ON A LOGARITHMIC Y-AXIS
    ax1.plot(
        btc_common.index,
        btc_common["value"],
        label="Bitcoin (USD, log-scale)",
        color="#f7931a",  # Bitcoin-orange
        linewidth=2.0,
    )
    ax1.set_yscale("log")                     # ← LOG SCALE
    ax1.set_ylabel("Bitcoin Price (USD, log)", color="#333333")
    ax1.tick_params(axis="y", colors="#333333")
    ax1.grid(axis="y", linestyle="--", alpha=0.3)

    # 6) Plot M2 index (green) on a LINEAR right‐hand axis
    ax2 = ax1.twinx()
    ax2.plot(
        m2_indexed.index,
        m2_indexed,
        label="Global M2 Index (base 100)",
        color="#00aa00",  # dark-green for contrast
        linewidth=2.0,
    )
    ax2.set_ylabel("Global M2 Index (linear)", color="#333333")
    ax2.tick_params(axis="y", colors="#333333")
    # (No grid on ax2 to keep it clean.)

    # 7) Extend x‐axis to give “future blank space”
    x_end_extended = common_end + relativedelta(years=extend_years)
    ax1.set_xlim(common_start, x_end_extended)

    # 8) Monthly x-ticks (e.g., “Aug, Sep, Oct…”)
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax1.xaxis.set_minor_locator(mdates.MonthLocator(bymonthday=15))
    plt.setp(ax1.get_xticklabels(), rotation=0, ha="center")

    # 9) Combine legends from both axes
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(
        lines1 + lines2,
        labels1 + labels2,
        loc="upper left",
        frameon=False,
        fontsize=10,
    )

    fig.tight_layout()
    return fig


def main(argv: list[str] | None = None) -> plt.Figure:
    p = argparse.ArgumentParser(description="Plot Bitcoin vs Global M2")
    p.add_argument(
        "--btc-series",
        type=str,
        default="CBBTCUSD",
        help="FRED series name for Bitcoin price",
    )
    p.add_argument(
        "--m2-series",
        type=str,
        default="GLOBAL_M2",
        help="FRED series name for global M2",
    )
    p.add_argument(
        "--start", type=str, default="2010-01-01", help="start date YYYY-MM-DD"
    )
    p.add_argument(
        "--end",
        type=str,
        default=datetime.today().strftime("%Y-%m-%d"),
        help="end date YYYY-MM-DD",
    )
    p.add_argument(
        "--offset",
        type=int,
        default=94,  # M2 leads by 94 days
        help="shift M2 by this many days (positive = M2 leads)",
    )
    p.add_argument(
        "--extend-years", type=int, default=1, help="years beyond end date to show"
    )
    p.add_argument(
        "--db",
        type=str,
        default=str(DB_PATH_DEFAULT),
        help="path to local SQLite DB",
    )
    p.add_argument(
        "--output", type=str, default=None, help="optional path to save the figure"
    )
    p.add_argument("--width", type=float, default=12.0, help="figure width in inches")
    p.add_argument("--height", type=float, default=6.0, help="figure height in inches")
    p.add_argument("--dpi", type=int, default=None, help="figure DPI")
    p.add_argument("--no-show", action="store_true", help="do not display the figure")
    args = p.parse_args(argv)

    try:
        start_dt = datetime.fromisoformat(args.start)
    except ValueError:
        print(f"Invalid --start date: {args.start}", file=sys.stderr)
        raise SystemExit(1)

    try:
        end_dt = datetime.fromisoformat(args.end)
    except ValueError:
        print(f"Invalid --end date: {args.end}", file=sys.stderr)
        raise SystemExit(1)

    btc, m2 = fetch_series(start_dt, end_dt, args.btc_series, args.m2_series, args.db)

    # Drop rows with null “value”
    btc = btc.dropna(subset=["value"])
    m2 = m2.dropna(subset=["value"])

    validate_series(btc, m2, args.btc_series, args.m2_series)
    fig = plot_bitcoin_m2(
        btc,
        m2,
        offset_days=args.offset,
        extend_years=args.extend_years,
        width=args.width,
        height=args.height,
        dpi=args.dpi,
    )

    save_figure(fig, args.output, __file__)
    if argv is None and not args.no_show:
        fig.show()
    return fig


if __name__ == "__main__":
    main()
