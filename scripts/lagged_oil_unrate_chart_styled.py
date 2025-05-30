#!/usr/bin/env python3
"""
lagged_oil_unrate_chart_styled.py
---------------------------------
Offline version: reads UNRATE & WTI series from ``data/fred.db``
(populated by ``scripts/refresh_data.py``), validates that both series
contain data for the requested period, and plots them with a configurable
lag.

Usage
-----
  python scripts/lagged_oil_unrate_chart_styled.py \
      --offset 18 \
      --start 1973-01-01 \
      --end   2025-05-31 \
      --extend-years 3
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
import sqlite3


# ──────────────────────────────────────────────────────────────────────────
# Data helpers
# ──────────────────────────────────────────────────────────────────────────
def fetch_series(
    start: datetime,
    end: datetime,
    db_path: str | Path = Path("data/fred.db"),
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load UNRATE and DCOILWTICO from a local SQLite DB, then:

    * convert UNRATE to month-end timestamps
    * average WTI daily prices to month-end
    """
    db_path = Path(db_path)
    if not db_path.exists():
        raise FileNotFoundError(
            f"{db_path} not found.  Run scripts/refresh_data.py on a "
            "machine with internet, commit the new DB, then retry."
        )

    with sqlite3.connect(db_path) as conn:
        unrate = (
            pd.read_sql(
                "SELECT date, UNRATE AS value FROM UNRATE", conn,
                parse_dates=["date"], index_col="date"
            )
            .loc[start:end]
        )
        oil = (
            pd.read_sql(
                "SELECT date, DCOILWTICO AS value FROM DCOILWTICO", conn,
                parse_dates=["date"], index_col="date"
            )
            .loc[start:end]
        )

    # Resample WTI to month-end average
    oil_monthly = oil.resample("M").mean()
    # Ensure UNRATE is at month-end, too
    unrate.index = unrate.index.to_period("M").to_timestamp("M")
    return unrate, oil_monthly


def validate_series(unrate: pd.DataFrame, oil: pd.DataFrame) -> None:
    """Sanity-check the fetched series before plotting.

    Both dataframes must contain a ``value`` column with no missing values and
    share a non-empty ``DatetimeIndex`` covering the same start and end dates.

    Parameters
    ----------
    unrate, oil:
        DataFrames returned by :func:`fetch_series`.

    Raises
    ------
    ValueError
        If either dataframe is empty, missing the ``value`` column, contains
        nulls, or the date indexes do not span the same range.
    """

    if unrate.empty:
        raise ValueError("UNRATE dataframe is empty")
    if oil.empty:
        raise ValueError("DCOILWTICO dataframe is empty")

    for name, df in [("UNRATE", unrate), ("DCOILWTICO", oil)]:
        if "value" not in df.columns:
            raise ValueError(f"{name} missing 'value' column")
        if df["value"].isna().any():
            raise ValueError(f"{name} contains null values")

    if not isinstance(unrate.index, pd.DatetimeIndex) or not isinstance(
        oil.index, pd.DatetimeIndex
    ):
        raise ValueError("Indexes must be DatetimeIndex")

    if unrate.index.min() != oil.index.min() or unrate.index.max() != oil.index.max():
        raise ValueError("Series indexes do not span the same date range")


# ──────────────────────────────────────────────────────────────────────────
# Plotting
# ──────────────────────────────────────────────────────────────────────────
def plot_lagged(
    unrate: pd.DataFrame,
    oil: pd.DataFrame,
    offset_months: int,
    start_date: datetime,
    end_date: datetime,
    extend_years: int,
) -> None:
    """Render the dual-axis chart with fixed scales and log ticks on oil."""
    oil_shifted = oil.shift(offset_months)

    fig, ax1 = plt.subplots(figsize=(14, 7))
    plt.title("Unemployment Rate and US Oil Price", fontsize=20, weight="bold")
    plt.suptitle(
        "Civilian Unemployment Rate and WTI Crude Oil Price",
        fontsize=14,
        y=0.93,
    )

    # Left axis – UNRATE
    ax1.plot(
        unrate.index,
        unrate["value"],
        label="UNRATE (LHS)",
        linewidth=2.5,
        color="#1f77b4",
    )
    ax1.set_ylabel("Unemployment rate (%)", fontsize=12)
    ax1.set_ylim(3, 15)
    ax1.yaxis.set_major_locator(mticker.MultipleLocator(2))
    ax1.yaxis.set_major_formatter("{x:.0f}%")
    ax1.grid(axis="y", linestyle="--", alpha=0.4)

    # Right axis – shifted oil (log scale)
    ax2 = ax1.twinx()
    ax2.plot(
        oil_shifted.index,
        oil_shifted["value"],
        label="USOIL (RHS)",
        linewidth=2,
        linestyle="-",
        alpha=0.8,
        color="#FF9900",
    )
    ax2.set_ylabel("Oil price (USD)", fontsize=12)

    # Build doubling ticks from $3 upward
    min_tick = 3
    max_val = oil_shifted["value"].max() * 1.1
    ticks = []
    i = 0
    while min_tick * 2**i < max_val:
        ticks.append(min_tick * 2**i)
        i += 1
    ticks.append(min_tick * 2**i)

    ax2.set_yscale("log")
    ax2.set_ylim(min_tick, ticks[-1])
    ax2.set_yticks(ticks)
    ax2.yaxis.set_major_formatter("${x:.0f}")

    # X-axis formatting
    ax1.set_xlim(start_date, end_date + relativedelta(years=extend_years))
    ax1.xaxis.set_major_locator(mdates.YearLocator(base=5))
    ax1.xaxis.set_minor_locator(mdates.YearLocator(1))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    plt.setp(ax1.get_xticklabels(), rotation=0, fontsize=11)

    # Legends
    lines, labels = ax1.get_legend_handles_labels()
    l2, l2l = ax2.get_legend_handles_labels()
    ax1.legend(lines + l2, labels + l2l, loc="upper left", frameon=False, fontsize=12)

    # Footnote
    foot = (
        f"Dates: {start_date.strftime('%Y')} through "
        f"{unrate.index[-1].strftime('%d %b %Y')}\."
        "\nSource: Local FRED snapshot (offline)."
    )
    plt.annotate(
        foot,
        (0, 0),
        (0, -40),
        xycoords="axes fraction",
        textcoords="offset points",
        va="top",
        fontsize=10,
        color="gray",
    )

    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()


# ──────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────
def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument(
        "-o",
        "--offset",
        type=int,
        default=18,
        help="lag in months (positive=lag, negative=lead)",
    )
    p.add_argument(
        "--start",
        type=str,
        default="1973-01-01",
        help="series start date (YYYY-MM-DD)",
    )
    p.add_argument(
        "--end",
        type=str,
        default=datetime.today().strftime("%Y-%m-%d"),
        help="series end date (YYYY-MM-DD)",
    )
    p.add_argument(
        "--extend-years",
        type=int,
        default=3,
        help="how many years beyond end_date to show on the x-axis",
    )
    p.add_argument(
        "--db",
        type=str,
        default="data/fred.db",
        help="path to local FRED SQLite file",
    )
    args = p.parse_args()

    start_dt = datetime.fromisoformat(args.start)
    end_dt = datetime.fromisoformat(args.end)

    unrate, oil = fetch_series(start_dt, end_dt, args.db)
    validate_series(unrate, oil)
    plot_lagged(unrate, oil, args.offset, start_dt, end_dt, args.extend_years)


if __name__ == "__main__":
    main()
