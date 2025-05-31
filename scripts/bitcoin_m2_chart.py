#!/usr/bin/env python3
"""bitcoin_m2_chart.py
----------------------
Plot Bitcoin price versus global M2 money supply stored in `data/fred.db`.

The script reads two FRED series from the local SQLite database and
plots them on dual axes. The M2 series can be shifted relative to the
Bitcoin series by a configurable number of days.
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Tuple

from scripts.constants import DB_PATH_DEFAULT

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from dateutil.relativedelta import relativedelta

# IMPORTANT: use the package‐qualified import
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
) -> plt.Figure:
    """Plot Bitcoin price and shifted M2 on dual axes."""
    # Determine overlapping range
    common_start = max(btc.index.min(), m2.index.min())
    common_end = min(btc.index.max(), m2.index.max())

    btc_common = btc.loc[common_start:common_end]
    m2_common = m2.loc[common_start:common_end]

    m2_shifted = m2_common.shift(offset_days)

    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax1.plot(
        btc_common.index, btc_common["value"], label="Bitcoin (LHS)", color="#1f77b4"
    )
    ax1.set_ylabel("Price (USD)")
    ax1.grid(axis="y", linestyle="--", alpha=0.3)

    ax2 = ax1.twinx()
    ax2.plot(
        m2_shifted.index, m2_shifted["value"], label="Global M2 (RHS)", color="#ff7f0e"
    )
    ax2.set_ylabel("Global M2")

    ax1.set_xlim(common_start, common_end + relativedelta(years=extend_years))
    ax1.xaxis.set_major_locator(mdates.YearLocator(base=5))
    ax1.xaxis.set_minor_locator(mdates.YearLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", frameon=False)

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
        default=94,
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
    args = p.parse_args(argv)

    start_dt = datetime.fromisoformat(args.start)
    end_dt = datetime.fromisoformat(args.end)

    btc, m2 = fetch_series(start_dt, end_dt, args.btc_series, args.m2_series, args.db)
    validate_series(btc, m2, args.btc_series, args.m2_series)
    fig = plot_bitcoin_m2(btc, m2, args.offset, args.extend_years)

    save_figure(fig, args.output, __file__)
    if argv is None:
        fig.show()
    return fig


if __name__ == "__main__":
    main()
