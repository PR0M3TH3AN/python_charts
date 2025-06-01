#!/usr/bin/env python3
"""bitcoin_m2_chart.py
----------------------
Plot Bitcoin price (log scale) versus global M2 money supply (rebased to 100),
with M2 shifted forward by 90 days so that both series share the same x-axis.
Use the full range provided by ``--start``/``--end``. White background, two y-axes
on the right, monthly x-ticks, and friendly error message if ``GLOBAL_M2`` is
missing.
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
    """Basic sanity checks on the two series."""
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
    Plot Bitcoin (log scale) and Global M2 (rebased to 100) on a shared x-axis,
    with M2 shifted forward by ``offset_days`` (90 days). Data is shown for the
    entire range provided by ``--start``/``--end``. White background, two
    y-axes on the right, monthly x-ticks.
    """

    # ──────────────────────────────────────────────────────────────────────────
    # 1) DROP ANY ROWS WITH NULL "value" BEFORE SHIFTING/REBASE:
    # ──────────────────────────────────────────────────────────────────────────
    btc_clean = btc.dropna(subset=["value"])
    m2_clean = m2.dropna(subset=["value"])

    # ──────────────────────────────────────────────────────────────────────────
    # 2) SHIFT M2's INDEX FORWARD by offset_days (90)
    # ──────────────────────────────────────────────────────────────────────────
    m2_shifted = m2_clean.copy()
    m2_shifted.index = m2_shifted.index + pd.Timedelta(days=offset_days)

    # ──────────────────────────────────────────────────────────────────────────
    # 3) USE FULL RANGE FROM --start (no hard-coded crop)
    # ──────────────────────────────────────────────────────────────────────────
    btc_cropped = btc_clean
    m2_cropped = m2_shifted

    # ──────────────────────────────────────────────────────────────────────────
    # 4) FIND OVERLAP WINDOW: plot only dates where BOTH series exist
    # ──────────────────────────────────────────────────────────────────────────
    overlap_start = max(btc_cropped.index.min(), m2_cropped.index.min())
    overlap_end = min(btc_cropped.index.max(), m2_cropped.index.max())

    if overlap_start >= overlap_end:
        raise ValueError(
            f"No overlapping range after shifting M2 by {offset_days} days."
        )

    btc_overlap = btc_cropped.loc[overlap_start:overlap_end]
    m2_overlap = m2_cropped.loc[overlap_start:overlap_end]

    # ──────────────────────────────────────────────────────────────────────────
    # 5) REBASE M2_OVERLAP to base‐100 index
    # ──────────────────────────────────────────────────────────────────────────
    first_m2_date = m2_overlap["value"].dropna().index.min()
    if first_m2_date is None:
        m2_indexed = pd.Series([], dtype=float)
    else:
        first_m2_value = float(m2_overlap.loc[first_m2_date, "value"])
        m2_indexed = (m2_overlap["value"] / first_m2_value) * 100
        m2_indexed = m2_indexed.dropna()

    # ──────────────────────────────────────────────────────────────────────────
    # 6) SET UP FIGURE WITH WHITE BACKGROUND
    # ──────────────────────────────────────────────────────────────────────────
    fig, ax1 = plt.subplots(figsize=(width, height), dpi=dpi)
    fig.patch.set_facecolor("white")
    ax1.set_facecolor("white")

    # ─── Plot Bitcoin on "ax1" (log scale, orange) ─────────────────────────────
    ax1.plot(
        btc_overlap.index,
        btc_overlap["value"],
        label="Bitcoin (USD, log-scale)",
        color="#f7931a",
        linewidth=2.0,
    )
    ax1.set_yscale("log")
    ax1.set_ylabel("Bitcoin Price (USD, log)", color="#333333")
    ax1.tick_params(axis="y", colors="#333333")
    # Move BTC axis to the right side:
    ax1.yaxis.set_label_position("right")
    ax1.yaxis.tick_right()

    # ─── Plot a horizontal dotted line at the last BTC close ────────────────────
    last_btc_date = btc_overlap.index.max()
    last_btc_value = float(btc_overlap.loc[last_btc_date, "value"])
    ax1.axhline(
        last_btc_value,
        color="#f7931a",
        linestyle=":",
        linewidth=1.5,
        alpha=0.9,
    )

    # ──────────────────────────────────────────────────────────────────────────
    # 7) Plot M2 on twin axis "ax2" (linear scale, green) ───────────────────────
    # ──────────────────────────────────────────────────────────────────────────
    ax2 = ax1.twinx()
    if not m2_indexed.empty:
        ax2.plot(
            m2_indexed.index,
            m2_indexed.values,
            label="Global M2 Index (base 100)",
            color="#00aa00",
            linewidth=2.0,
        )
    ax2.set_ylabel("Global M2 Index (base 100)", color="#333333")
    ax2.tick_params(axis="y", colors="#333333")
    # Move M2 axis even further right (so BTC ticks are inner-right, M2 outer-right):
    ax2.spines["right"].set_position(("axes", 1.08))

    # ──────────────────────────────────────────────────────────────────────────
    # 8) SET Y-TICKS EXACTLY AS IN THE SCREENSHOT
    # ──────────────────────────────────────────────────────────────────────────
    # Bitcoin ticks (inner right):
    btc_ticks = [41100, 45500, 50500, 56500, 62500, 70500, 78000, 86000, 98000, 113000]
    ax1.set_yticks(btc_ticks)
    ax1.set_yticklabels([f"{int(tick):,}" for tick in btc_ticks], color="#333333")

    # Global M2 ticks (outer right):
    m2_ticks = [99.10] + list(range(100, 114))  # [99.10, 100, 101, …, 113]
    ax2.set_yticks(m2_ticks)
    ax2.set_yticklabels(
        [f"{tick:.2f}" if isinstance(tick, float) else f"{tick}" for tick in m2_ticks],
        color="#333333",
    )

    # ──────────────────────────────────────────────────────────────────────────
    # 9) DRAW HORIZONTAL GRID LINES (only on BTC axis)
    # ──────────────────────────────────────────────────────────────────────────
    ax1.grid(
        axis="y",
        linestyle="--",
        linewidth=0.7,
        color="#cccccc",
        alpha=0.4,
    )

    # ──────────────────────────────────────────────────────────────────────────
    # 10) SET X-LIMITS: from overlap_start → overlap_end + extend_years
    # ──────────────────────────────────────────────────────────────────────────
    x_end_extended = overlap_end + relativedelta(years=extend_years)
    ax1.set_xlim(overlap_start, x_end_extended)

    # ──────────────────────────────────────────────────────────────────────────
    # 11) MONTHLY X-TICKS:
    #     Major = first of each month (“Jul, Aug, Sep …”),
    #     Minor = mid-month (no label).
    # ──────────────────────────────────────────────────────────────────────────
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax1.xaxis.set_minor_locator(mdates.MonthLocator(bymonthday=15))
    for label in ax1.get_xticklabels():
        label.set_color("#333333")
        label.set_rotation(0)
        label.set_fontsize(10)

    # ──────────────────────────────────────────────────────────────────────────
    # 12) ANNOTATE “2025” UNDER THE JANUARY TICK
    # ──────────────────────────────────────────────────────────────────────────
    try:
        jan2025 = pd.to_datetime("2025-01-01")
        if jan2025 < overlap_start:
            jan2025 = pd.to_datetime(f"{overlap_start.year + 1}-01-01")
        xloc = mdates.date2num(jan2025)
        ax1.annotate(
            "2025",
            (xloc, 0),
            xycoords=("data", "axes fraction"),
            xytext=(0, -20),
            textcoords="offset points",
            ha="center",
            color="#333333",
            fontsize=11,
        )
    except Exception:
        pass

    # ──────────────────────────────────────────────────────────────────────────
    # 13) LEGEND (combine both axes) at top-left
    # ──────────────────────────────────────────────────────────────────────────
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(
        lines1 + lines2,
        labels1 + labels2,
        loc="upper left",
        frameon=False,
        fontsize=11,
    )

    # ──────────────────────────────────────────────────────────────────────────
    # 14) HEADER TEXT (symbol, price, M2 info) at top-left
    # ──────────────────────────────────────────────────────────────────────────
    header_y = 1.02
    # “Bitcoin / U.S. Dollar · 1D · COINBASE” in gray:
    ax1.text(
        0.0,
        header_y,
        "Bitcoin / U.S. Dollar · 1D · COINBASE",
        transform=ax1.transAxes,
        color="#333333",
        fontsize=12,
        weight="bold",
        va="bottom",
    )
    # BTC’s last close and daily change in orange:
    prev_btc = float(btc_overlap["value"].iloc[-2])
    change = last_btc_value - prev_btc
    pct_change = (change / prev_btc) * 100
    ax1.text(
        0.0,
        header_y - 0.035,
        f"{last_btc_value:,.2f}  {change:+.2f} ({pct_change:+.2f}%)",
        transform=ax1.transAxes,
        color="#f7931a",
        fontsize=11,
        va="bottom",
    )
    # M2 info (“Days Offset = 90” and last M2 index) in green:
    if not m2_indexed.empty:
        last_m2_val = m2_indexed.iloc[-1]
        ax1.text(
            0.0,
            header_y - 0.07,
            f"Global M2 Money Supply // Days Offset = {offset_days}   {last_m2_val:.2f}",
            transform=ax1.transAxes,
            color="#00aa00",
            fontsize=11,
            va="bottom",
        )

    fig.tight_layout(rect=[0, 0, 1, 0.95])
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
        "--start", type=str, default="2024-01-01", help="start date YYYY-MM-DD"
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
        default=90,  # shift M2 forward by 90 days (to match TradingView)
        help="shift M2 by this many days (positive = M2 leads BTC)",
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

    # ──────────────────────────────────────────────────────────────────────────
    # 15) FETCH SERIES
    # ──────────────────────────────────────────────────────────────────────────
    try:
        btc, m2 = fetch_series(
            start_dt, end_dt, args.btc_series, args.m2_series, args.db
        )
    except FileNotFoundError as fnf:
        print(fnf, file=sys.stderr)
        sys.exit(1)

    # ──────────────────────────────────────────────────────────────────────────
    # DROP ANY ROWS WITH NULL "value" BEFORE VALIDATION
    # ──────────────────────────────────────────────────────────────────────────
    # (GLOBAL_M2 often has one or two trailing NaNs for "unpublished" months.)
    btc = btc.dropna(subset=["value"])
    m2 = m2.dropna(subset=["value"])

    # If either series is empty, print a friendly message and exit:
    if btc.empty:
        print(
            f"No data found for {args.btc_series} between {args.start} and {args.end}.",
            file=sys.stderr,
        )
        sys.exit(1)

    if m2.empty:
        print(
            f"No data found for {args.m2_series} between {args.start} and {args.end}.",
            file=sys.stderr,
        )
        print(
            "Try running:\n"
            "  python -m scripts.refresh_data --series GLOBAL_M2 --start 2010-01-01",
            file=sys.stderr,
        )
        sys.exit(1)

    # ──────────────────────────────────────────────────────────────────────────
    # 16) VALIDATE (non-empty, no nulls, overlapping)
    # ──────────────────────────────────────────────────────────────────────────
    try:
        validate_series(btc, m2, args.btc_series, args.m2_series)
    except ValueError as e:
        print(f"Validation error: {e}", file=sys.stderr)
        sys.exit(1)

    # ──────────────────────────────────────────────────────────────────────────
    # 17) PLOT
    # ──────────────────────────────────────────────────────────────────────────
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
