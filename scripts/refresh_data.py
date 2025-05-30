#!/usr/bin/env python3
"""
refresh_data.py
---------------
Download UNRATE and DCOILWTICO from FRED and store them in SQLite
(data/fred.db).  Run on a connected machine; commit the DB afterwards.
"""

from datetime import date
import pathlib
import sqlite3

import pandas as pd
from pandas_datareader.data import DataReader

HERE = pathlib.Path(__file__).resolve().parent
DATA_PATH = HERE.parent / "data"
DB_FILE = DATA_PATH / "fred.db"

START = "1948-01-01"          # earliest UNRATE observation
END = date.today().isoformat()
SERIES = ("UNRATE", "DCOILWTICO")


def main() -> None:
    DATA_PATH.mkdir(exist_ok=True)
    with sqlite3.connect(DB_FILE) as conn:
        for s in SERIES:
            print(f"↯ downloading {s} …")
            df = DataReader(s, "fred", START, END)
            df.to_sql(s, conn, if_exists="replace", index_label="date")
            print(f"✓ wrote {s}: {len(df):,} rows")
    print(f"\nDone.  SQLite DB at {DB_FILE} ({DB_FILE.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
