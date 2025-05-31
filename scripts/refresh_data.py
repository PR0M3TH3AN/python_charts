#!/usr/bin/env python3
"""refresh_data.py
-----------------
Download one or more FRED series into ``data/fred.db``.

Run this script on a machine with internet access and commit the updated
database afterwards.

Example:
    python scripts/refresh_data.py --series UNRATE CPIAUCSL --start 1960-01-01
"""

from __future__ import annotations

from datetime import date
import argparse
import pathlib
import sqlite3

from pandas_datareader.data import DataReader
import pandas as pd

from scripts.constants import DB_PATH_DEFAULT, UNRATE, DCOILWTICO

HERE = pathlib.Path(__file__).resolve().parent
DATA_PATH = DB_PATH_DEFAULT.parent
DB_FILE = DB_PATH_DEFAULT

DEFAULT_START = "1948-01-01"  # earliest UNRATE observation
DEFAULT_END = date.today().isoformat()
DEFAULT_SERIES = (UNRATE, DCOILWTICO)


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description="Download FRED series to SQLite")
    p.add_argument(
        "--series",
        nargs="+",
        default=list(DEFAULT_SERIES),
        help="FRED series names",
    )
    p.add_argument("--start", type=str, default=DEFAULT_START, help="start date")
    p.add_argument("--end", type=str, default=DEFAULT_END, help="end date")
    args = p.parse_args(argv)

    DATA_PATH.mkdir(exist_ok=True)
    with sqlite3.connect(DB_FILE) as conn:
        for s in args.series:
            print(f"↯ downloading {s} …")
            df = DataReader(s, "fred", args.start, args.end)
            df.to_sql(s, conn, if_exists="replace", index_label="date")
            print(f"✓ wrote {s}: {len(df):,} rows")
    print(f"\nDone.  SQLite DB at {DB_FILE} ({DB_FILE.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
