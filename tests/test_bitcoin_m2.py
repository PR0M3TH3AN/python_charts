import matplotlib

matplotlib.use("Agg")

import os
import sys
import pandas as pd

sys.path.append(os.path.abspath("."))

from scripts.bitcoin_m2_chart import plot_bitcoin_m2, main as btc_m2_main


def sample_data():
    dates = pd.date_range("2021-01-01", periods=5, freq="D")
    btc = pd.DataFrame({"value": [10, 11, 12, 13, 14]}, index=dates)
    m2 = pd.DataFrame({"value": [1, 2, 3, 4, 5]}, index=dates)
    return btc, m2


def test_plot_bitcoin_m2_returns_figure():
    btc, m2 = sample_data()
    fig = plot_bitcoin_m2(btc, m2, 94, 1)
    assert len(fig.axes) == 2
    assert any(ax.get_lines() for ax in fig.axes)


def test_btc_m2_main(monkeypatch):
    btc, m2 = sample_data()

    def fake_fetch(*_args, **_kwargs):
        return btc, m2

    monkeypatch.setattr("scripts.bitcoin_m2_chart.fetch_series", fake_fetch)
    fig = btc_m2_main(["--btc-series", "BTC", "--m2-series", "M2"])
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
        ]
    )
    assert out_file.exists()
