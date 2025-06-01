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

from datetime import date, timedelta
import argparse
import pathlib
import sqlite3
import logging

logger = logging.getLogger(__name__)

# pandas_datareader < 0.11 requires distutils, which was removed in Python 3.12
try:  # pragma: no cover - prefer stdlib when available
    from distutils.version import LooseVersion  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - Python >=3.12
    from packaging.version import Version
    import types, sys

    class LooseVersion:
        def __init__(self, v: str | int) -> None:
            self.vstring = str(v)
            self.version = Version(self.vstring)

        def __repr__(self) -> str:  # pragma: no cover - debug helper
            return f"LooseVersion('{self.vstring}')"

        def __lt__(self, other: "LooseVersion") -> bool:
            return self.version < other.version

        def __le__(self, other: "LooseVersion") -> bool:
            return self.version <= other.version

        def __eq__(self, other: object) -> bool:
            if not isinstance(other, LooseVersion):
                return NotImplemented
            return self.version == other.version

        def __ne__(self, other: object) -> bool:  # pragma: no cover - unused
            if not isinstance(other, LooseVersion):
                return NotImplemented
            return self.version != other.version

        def __gt__(self, other: "LooseVersion") -> bool:
            return self.version > other.version

        def __ge__(self, other: "LooseVersion") -> bool:
            return self.version >= other.version

    version_module = types.ModuleType("version")
    version_module.LooseVersion = LooseVersion
    distutils_module = types.ModuleType("distutils")
    distutils_module.version = version_module
    sys.modules.setdefault("distutils", distutils_module)
    sys.modules.setdefault("distutils.version", version_module)

from pandas_datareader.data import DataReader
import pandas as pd

from scripts.constants import DB_PATH_DEFAULT, UNRATE, DCOILWTICO

HERE = pathlib.Path(__file__).resolve().parent
DATA_PATH = DB_PATH_DEFAULT.parent
DB_FILE = DB_PATH_DEFAULT

DEFAULT_START = "1948-01-01"  # earliest UNRATE observation
DEFAULT_END = date.today().isoformat()
DEFAULT_SERIES = (UNRATE, DCOILWTICO, "CBBTCUSD", "GLOBAL_M2")


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
            start = pd.to_datetime(args.start)
            end = pd.to_datetime(args.end)

            last = None
            table_exists = bool(
                conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                    (s,),
                ).fetchone()
            )
            if table_exists:
                last_row = conn.execute(f"SELECT MAX(date) FROM {s}").fetchone()
                if last_row and last_row[0] is not None:
                    last = pd.to_datetime(last_row[0])

            new_start = start
            if last is not None:
                new_start = max(start, last + timedelta(days=1))

            if new_start > end:
                logger.info("%s up to date; last date %s", s, last.date() if last else "n/a")
                continue

            logger.info("\u21af downloading %s …", s)
            df = DataReader(s, "fred", new_start.date().isoformat(), end.date().isoformat())
            if_exists = "append" if table_exists else "replace"
            df.to_sql(s, conn, if_exists=if_exists, index_label="date")
            logger.info("\u2713 wrote %s: %s rows", s, len(df))
    logger.info(
        "\nDone.  SQLite DB at %s (%s KB)",
        DB_FILE,
        DB_FILE.stat().st_size / 1024,
    )


if __name__ == "__main__":
    main()
