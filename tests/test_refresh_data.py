import os
import sys
import sqlite3
from pathlib import Path

import pandas as pd

sys.path.append(os.path.abspath("."))

import scripts.refresh_data as refresh_data


def test_refresh_data_writes_series(tmp_path, monkeypatch):
    calls = []

    def fake_reader(name, src, start, end):
        calls.append(name)
        dates = pd.date_range(start, periods=1)
        return pd.DataFrame({name: [1]}, index=dates)

    monkeypatch.setattr(refresh_data, "DataReader", fake_reader)
    monkeypatch.setattr(refresh_data, "DATA_PATH", tmp_path)
    db_file = tmp_path / "fred.db"
    monkeypatch.setattr(refresh_data, "DB_FILE", db_file)

    refresh_data.main(
        [
            "--series",
            "A",
            "B",
            "--start",
            "2000-01-01",
            "--end",
            "2000-01-02",
        ]
    )

    assert set(calls) == {"A", "B"}
    with sqlite3.connect(db_file) as conn:
        tables = {
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
    assert {"A", "B"} <= tables
