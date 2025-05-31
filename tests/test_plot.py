import matplotlib

matplotlib.use("Agg")

import os
import sys
import pandas as pd

sys.path.append(os.path.abspath("."))

from scripts.lagged_oil_unrate_chart_styled import plot_lagged


def test_plot_lagged_returns_figure():
    dates = pd.date_range("2000-01-01", periods=5, freq="M")
    unrate = pd.DataFrame({"value": [5, 6, 7, 5, 4]}, index=dates)
    oil = pd.DataFrame({"value": [20, 25, 30, 35, 40]}, index=dates)

    fig = plot_lagged(unrate, oil, 1, dates[0], dates[-1], 0)

    assert len(fig.axes) == 2
    assert any(ax.get_lines() for ax in fig.axes)
