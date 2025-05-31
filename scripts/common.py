from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import pandas as pd
import sqlite3


def save_figure(fig: plt.Figure, output: str | None, script_path: str) -> Path:
    """Save ``fig`` to ``output`` or ``outputs/`` with timestamp."""
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


def fetch_series_db(
    series: Iterable[str],
    start: datetime,
    end: datetime,
    db_path: str | Path = Path("data/fred.db"),
) -> pd.DataFrame:
    """Load one or more FRED series from a local SQLite DB."""
    db_path = Path(db_path)
    if not db_path.exists():
        raise FileNotFoundError(
            f"{db_path} not found. Run scripts/refresh_data.py on a machine with internet, commit the DB, then retry."
        )

    frames: list[pd.DataFrame] = []
    with sqlite3.connect(db_path) as conn:
        for name in series:
            df = pd.read_sql(
                f"SELECT date, {name} FROM {name}",
                conn,
                parse_dates=["date"],
                index_col="date",
            ).loc[start:end]
            df.rename(columns={name: name}, inplace=True)
            frames.append(df)

    if not frames:
        raise ValueError("No series loaded")

    return pd.concat(frames, axis=1).sort_index()


def validate_dataframe(df: pd.DataFrame, name: str) -> None:
    """Ensure dataframe has a ``value`` column with data and DatetimeIndex."""
    if df.empty:
        raise ValueError(f"{name} dataframe is empty")
    if "value" not in df.columns:
        raise ValueError(f"{name} missing 'value' column")
    if df["value"].isna().any():
        raise ValueError(f"{name} contains null values")
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("Indexes must be DatetimeIndex")


def validate_overlap(df1: pd.DataFrame, df2: pd.DataFrame) -> None:
    """Verify that two series share a non-empty overlapping date range."""
    start = max(df1.index.min(), df2.index.min())
    end = min(df1.index.max(), df2.index.max())
    if start >= end:
        raise ValueError("Series have no overlapping date range")
