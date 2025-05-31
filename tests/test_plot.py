import matplotlib

matplotlib.use("Agg")

import os
import sys
import pandas as pd

sys.path.append(os.path.abspath("."))

from scripts.lagged_oil_unrate_chart_styled import plot_lagged, main as lagged_main
from scripts.custom_chart import plot_series, main as custom_main


def test_plot_lagged_returns_figure():
    dates = pd.date_range("2000-01-01", periods=5, freq="M")
    unrate = pd.DataFrame({"value": [5, 6, 7, 5, 4]}, index=dates)
    oil = pd.DataFrame({"value": [20, 25, 30, 35, 40]}, index=dates)

    fig = plot_lagged(unrate, oil, 1, dates[0], dates[-1], 0)

    assert len(fig.axes) == 2
    assert any(ax.get_lines() for ax in fig.axes)


def test_plot_series_and_main():
    dates = pd.date_range("2020-01-01", periods=3, freq="D")
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]}, index=dates)
    fig = plot_series(df)
    assert len(fig.axes) == 1
    assert any(fig.axes[0].get_lines())

    fig2 = custom_main(
        [
            "--series",
            "UNRATE",
            "DCOILWTICO",
            "--start",
            "2020-01-01",
            "--end",
            "2020-03-01",
            "--db",
            "data/fred.db",
        ]
    )
    assert len(fig2.axes) == 1
    assert any(fig2.axes[0].get_lines())


def test_custom_main_saves_output(tmp_path):
    out_file = tmp_path / "chart.png"
    custom_main(
        [
            "--series",
            "UNRATE",
            "--start",
            "2020-01-01",
            "--end",
            "2020-03-01",
            "--db",
            "data/fred.db",
            "--output",
            str(out_file),
        ]
    )
    assert out_file.exists()


def test_lagged_main_options(monkeypatch):
    dates = pd.date_range("2021-01-01", periods=3, freq="M")
    unrate = pd.DataFrame({"value": [1, 2, 3]}, index=dates)
    oil = pd.DataFrame({"value": [4, 5, 6]}, index=dates)

    monkeypatch.setattr(
        "scripts.lagged_oil_unrate_chart_styled.fetch_series", lambda *_: (unrate, oil)
    )

    fig = lagged_main(
        ["--offset", "1", "--width", "8", "--height", "4", "--dpi", "150", "--no-show"]
    )
    assert len(fig.axes) == 2
