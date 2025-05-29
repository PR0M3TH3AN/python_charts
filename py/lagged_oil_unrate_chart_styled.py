#!/usr/bin/env python3
"""
lagged_oil_unrate_chart_styled.py
---------------------------------
Fetch and plot UNRATE vs. WTI oil price with a configurable lag,
date range, and polished dual-axis styling.

Usage:
    python lagged_oil_unrate_chart_styled.py \
        --offset 18 \
        --start 1973-01-01 \
        --end 2025-05-31 \
        --extend-years 3

Dependencies:
    pip install pandas pandas_datareader matplotlib python-dateutil
"""
import argparse
from datetime import datetime
from dateutil.relativedelta import relativedelta

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import pandas_datareader.data as web


def fetch_series(start, end):
    # FRED series
    unrate = web.DataReader("UNRATE", "fred", start, end)
    oil   = web.DataReader("DCOILWTICO", "fred", start, end)

    # Resample WTI to month-end average
    oil_monthly = oil.resample("M").mean()
    # Ensure UNRATE is at month-end timestamps, too
    unrate.index = unrate.index.to_period("M").to_timestamp("M")
    return unrate, oil_monthly


def plot_lagged(
    unrate: pd.DataFrame,
    oil: pd.DataFrame,
    offset_months: int,
    start_date: datetime,
    end_date: datetime,
    extend_years: int
):
    # Shift oil by offset: positive = lag; negative = lead
    oil_shifted = oil.shift(offset_months)

    # Build figure
    fig, ax1 = plt.subplots(figsize=(14, 7))
    plt.title("Unemployment Rate and US Oil Price", fontsize=20, weight="bold")
    plt.suptitle(
        "Civilian Unemployment Rate and WTI Crude Oil Price",
        fontsize=14,
        y=0.93
    )

    # Plot UNRATE on left axis
    ax1.plot(unrate.index, unrate["UNRATE"], 
             label="UNRATE (LHS)", linewidth=2.5, color="#1f77b4")
    ax1.set_ylabel("Unemployment rate (%)", fontsize=12)
    ax1.set_ylim(0, unrate["UNRATE"].max() * 1.1)
    ax1.yaxis.set_major_formatter("{x:.0f}%")
    ax1.grid(axis="y", linestyle="--", alpha=0.4)

    # Plot shifted oil on right axis
    ax2 = ax1.twinx()
    ax2.plot(oil_shifted.index, oil_shifted["DCOILWTICO"],
             label="USOIL (RHS)", linewidth=2, linestyle="-", alpha=0.8, color="#FF9900")
    ax2.set_ylabel("Oil price (USD)", fontsize=12)
    ax2.set_ylim(0, oil_shifted["DCOILWTICO"].max() * 1.1)
    ax2.yaxis.set_major_formatter("${x:,.0f}")

    # X-axis formatting
    ax1.set_xlim(start_date, end_date + relativedelta(years=extend_years))
    ax1.xaxis.set_major_locator(mdates.YearLocator(base=5))
    ax1.xaxis.set_minor_locator(mdates.YearLocator(1))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    plt.setp(ax1.get_xticklabels(), rotation=0, fontsize=11)

    # Combine legends
    lines, labels = ax1.get_legend_handles_labels()
    l2, l2l = ax2.get_legend_handles_labels()
    ax1.legend(lines + l2, labels + l2l, loc="upper left", frameon=False, fontsize=12)

    # Footnotes
    foot = (
        f"Dates: {start_date.strftime('%Y')} through {unrate.index[-1].strftime('%d %b %Y')}.\n"
        "Source: FRED, pandas_datareader."
    )
    plt.annotate(
        foot,
        (0,0), (0, -40), 
        xycoords="axes fraction", textcoords="offset points",
        va="top", fontsize=10, color="gray"
    )

    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("-o", "--offset", type=int, default=18,
                   help="lag in months (positive=lag, negative=lead)")
    p.add_argument("--start", type=str, default="1973-01-01",
                   help="series start date (YYYY-MM-DD)")
    p.add_argument("--end", type=str, default=datetime.today().strftime("%Y-%m-%d"),
                   help="series end date (YYYY-MM-DD)")
    p.add_argument("--extend-years", type=int, default=3,
                   help="how many years beyond end_date to show on the x-axis")
    args = p.parse_args()

    start_dt = datetime.fromisoformat(args.start)
    end_dt   = datetime.fromisoformat(args.end)

    unrate, oil = fetch_series(start_dt, end_dt)
    plot_lagged(unrate, oil, args.offset, start_dt, end_dt, args.extend_years)
