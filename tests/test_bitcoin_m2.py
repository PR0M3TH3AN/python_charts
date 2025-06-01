import matplotlib

matplotlib.use("Agg")

import os
import sys
import pandas as pd

sys.path.append(os.path.abspath("."))

from scripts.bitcoin_m2_chart import plot_bitcoin_m2, main as btc_m2_main


def sample_data():
    btc_dates = pd.date_range("2024-07-01", periods=10, freq="D")
    btc = pd.DataFrame({"value": range(10, 20)}, index=btc_dates)
    m2_dates = btc_dates
    m2 = pd.DataFrame({"value": range(1, 11)}, index=m2_dates)
    return btc, m2


def sample_data_with_nan():
    btc_dates = pd.date_range("2024-07-01", periods=10, freq="D")
    btc = pd.DataFrame({"value": range(10, 20)}, index=btc_dates)
    m2_dates = btc_dates
    m2_values = list(range(1, 10)) + [pd.NA]
    m2 = pd.DataFrame({"value": m2_values}, index=m2_dates)
    return btc, m2


def test_plot_bitcoin_m2_returns_figure():
    btc, m2 = sample_data()
    fig = plot_bitcoin_m2(btc, m2, 0, 1)
    assert len(fig.axes) == 2
    assert any(ax.get_lines() for ax in fig.axes)


def test_btc_m2_main(monkeypatch):
    btc, m2 = sample_data()

    def fake_fetch(*_args, **_kwargs):
        return btc, m2

    monkeypatch.setattr("scripts.bitcoin_m2_chart.fetch_series", fake_fetch)
    fig = btc_m2_main(
        [
            "--btc-series",
            "BTC",
            "--m2-series",
            "M2",
            "--offset",
            "0",
            "--width",
            "8",
            "--height",
            "4",
            "--dpi",
            "150",
            "--no-show",
        ]
    )
    assert len(fig.axes) == 2


def test_main_handles_trailing_nan(monkeypatch):
    btc, m2 = sample_data_with_nan()

    def fake_fetch(*_args, **_kwargs):
        return btc, m2

    monkeypatch.setattr("scripts.bitcoin_m2_chart.fetch_series", fake_fetch)
    fig = btc_m2_main(
        [
            "--btc-series",
            "BTC",
            "--m2-series",
            "M2",
            "--offset",
            "0",
            "--no-show",
        ]
    )
    assert len(fig.axes) == 2


def test_btc_m2_main_saves_output(tmp_path, monkeypatch):
    btc, m2 = sample_data()

    def fake_fetch(*_args, **_kwargs):
        return btc, m2

    monkeypatch.setattr("scripts.bitcoin_m2_chart.fetch_series", fake_fetch)
    out_file = tmp_path / "out.png"
    btc_m2_main(
        [
            "--btc-series",
            "BTC",
            "--m2-series",
            "M2",
            "--output",
            str(out_file),
            "--offset",
            "0",
            "--width",
            "8",
            "--height",
            "4",
            "--dpi",
            "150",
            "--no-show",
        ]
    )
    assert out_file.exists()
