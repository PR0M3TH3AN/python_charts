#!/usr/bin/env python3
"""
lagged_oil_unrate_chart_styled.py
---------------------------------
Offline version: reads UNRATE & WTI series from ``data/fred.db``
(populated by ``scripts/refresh_data.py``), validates that both series
contain data for the requested period (overlap only), and plots them
with a configurable lag.
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


def save_figure(fig: plt.Figure, output: str | None, script_path: str) -> Path:
    """Save ``fig`` to ``output`` or a timestamped path under ``outputs/``."""
    out_path = (
        Path(output)
        if output is not None
        else Path("outputs")
        / f"{Path(script_path).stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path)
    print(f"Saved figure to {out_path}")
    return out_path


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
        unrate = pd.read_sql(
            "SELECT date, UNRATE AS value FROM UNRATE",
            conn,
            parse_dates=["date"],
            index_col="date",
        ).loc[start:end]
        oil = pd.read_sql(
            "SELECT date, DCOILWTICO AS value FROM DCOILWTICO",
            conn,
            parse_dates=["date"],
            index_col="date",
        ).loc[start:end]

    # Resample WTI to month-end average
    oil_monthly = oil.resample("M").mean()
    # Ensure UNRATE is at month-end, too
    unrate.index = unrate.index.to_period("M").to_timestamp("M")
    return unrate, oil_monthly


def validate_series(unrate: pd.DataFrame, oil: pd.DataFrame) -> None:
    """
    Sanity-check the fetched series before plotting.

    Both dataframes must contain a ``value`` column with no missing values
    and share a non-empty overlapping date range.
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

    # Replace strict range check with overlap check
    overlap_start = max(unrate.index.min(), oil.index.min())
    overlap_end = min(unrate.index.max(), oil.index.max())

    if overlap_start >= overlap_end:
        raise ValueError("Series have no overlapping date range")


# ──────────────────────────────────────────────────────────────────────────
# Plotting
# ──────────────────────────────────────────────────────────────────────────
def plot_lagged(
    unrate: pd.DataFrame,
    oil: pd.DataFrame,
    offset_months: int,
    _start_date: datetime,
    _end_date: datetime,
    extend_years: int,
) -> plt.Figure:
    """
    Render the dual-axis chart with fixed scales and log ticks on oil.
    Trims both series to their overlapping date range before shifting.

    Returns the created :class:`matplotlib.figure.Figure` so callers can
    decide how to display or save it.
    """
    # Find overlapping date range
    common_start = max(unrate.index.min(), oil.index.min())
    common_end = min(unrate.index.max(), oil.index.max())

    print(f"⚠️ Using overlapping range: {common_start.date()} to {common_end.date()}")
    print(
        f"  - UNRATE range: {unrate.index.min().date()} to {unrate.index.max().date()}"
    )
    print(f"  - OIL range: {oil.index.min().date()} to {oil.index.max().date()}")

    # Trim series to common range
    unrate_common = unrate.loc[common_start:common_end]
    oil_common = oil.loc[common_start:common_end]

    # Apply lag/lead
    oil_shifted = oil_common.shift(offset_months)

    fig, ax1 = plt.subplots(figsize=(14, 7))
    plt.title("Unemployment Rate and US Oil Price", fontsize=20, weight="bold")
    plt.suptitle(
        "Civilian Unemployment Rate and WTI Crude Oil Price",
        fontsize=14,
        y=0.93,
    )

    # Left axis – UNRATE
    ax1.plot(
        unrate_common.index,
        unrate_common["value"],
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

    # X-axis formatting using common range
    ax1.set_xlim(common_start, common_end + relativedelta(years=extend_years))
    ax1.xaxis.set_major_locator(mdates.YearLocator(base=5))
    ax1.xaxis.set_minor_locator(mdates.YearLocator(1))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    plt.setp(ax1.get_xticklabels(), rotation=0, fontsize=11)

    # Legends
    lines, labels = ax1.get_legend_handles_labels()
    l2, l2l = ax2.get_legend_handles_labels()
    ax1.legend(lines + l2, labels + l2l, loc="upper left", frameon=False, fontsize=12)

    # Footnote with actual ranges
    foot = (
        f"UNRATE: {unrate.index.min().strftime('%b %Y')}–{unrate.index.max().strftime('%b %Y')} | "
        f"OIL: {oil.index.min().strftime('%b %Y')}–{oil.index.max().strftime('%b %Y')}\n"
        "Source: Local FRED snapshot (offline)."
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
    return fig


# ──────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────
def main() -> plt.Figure:
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
    p.add_argument(
        "--output",
        type=str,
        default=None,
        help="optional path to save the figure (PNG or PDF)",
    )
    args = p.parse_args()

    start_dt = datetime.fromisoformat(args.start)
    end_dt = datetime.fromisoformat(args.end)

    unrate, oil = fetch_series(start_dt, end_dt, args.db)
    validate_series(unrate, oil)
    fig = plot_lagged(unrate, oil, args.offset, start_dt, end_dt, args.extend_years)
    save_figure(fig, args.output, __file__)
    fig.show()
    return fig


if __name__ == "__main__":
    main()
