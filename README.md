# Lagged Oil vs. Unemployment Charting

This repository provides two Python scripts to fetch the latest US Unemployment Rate (UNRATE) and WTI crude oil price (DCOILWTICO) from FRED, apply a configurable lag or lead to the oil series, and generate polished dual‑axis charts.

## Files

* **`lagged_oil_unrate_chart.py`**
  A lightweight script that:

  1. Downloads monthly UNRATE and averages daily WTI to monthly.
  2. Shifts the oil series by `N` months (default = 18).
  3. Plots both series on a dual‑axis Matplotlib chart.

* **`lagged_oil_unrate_chart_styled.py`**
  A more polished version that adds:

  * Title, subtitle, footnote with date range and source.
  * Clean dual‑axis styling with percentage and dollar‑format ticks.
  * Customizable date range and extended x‑axis (e.g., 1973–2028).
  * CLI flags for offset, start/end dates, and axis extension.

* **`requirements.txt`**
  Lists all Python dependencies for both scripts.

## Prerequisites

* Python 3.7 or later
* Internet connection (to fetch data from FRED)

## Setup

Clone or download this repository:

```bash
git clone https://your-repo-url.git
cd your-repo-folder
```

### Create a Virtual Environment & Install Dependencies

#### On Linux / macOS

```bash
# 1. Create a venv
python3 -m venv venv

# 2. Activate it
source venv/bin/activate

# 3. Upgrade pip and install requirements
pip install --upgrade pip
pip install -r requirements.txt
```

#### On Windows (PowerShell)

```powershell
# 1. Create a venv
python -m venv venv

# 2. Activate it
venv\Scripts\Activate.ps1

# 3. Upgrade pip and install requirements
python -m pip install --upgrade pip
pip install -r requirements.txt
```

> **Note:** If you get execution policy errors on Windows, you may need to run:
>
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

## Usage

Once the virtual environment is active and dependencies are installed, run either script from the project root.

### 1. Basic Lag Script

```bash
# Default: oil lags unemployment by 18 months (~1.5 years)
python lagged_oil_unrate_chart.py

# Other offsets (in months)
python lagged_oil_unrate_chart.py --offset 6    # 6‑month lag
python lagged_oil_unrate_chart.py --offset -12  # 12‑month lead
```

### 2. Styled & Configurable Chart

```bash
python lagged_oil_unrate_chart_styled.py \
    --offset 18 \
    --start 1973-01-01 \
    --end 2025-05-31 \
    --extend-years 3
```

| Flag               | Description                                                    |
| ------------------ | -------------------------------------------------------------- |
| `--offset N`       | Lag (positive) or lead (negative) in months (default = 18)     |
| `--start DATE`     | Series start date (`YYYY-MM-DD`, default = `1973-01-01`)       |
| `--end DATE`       | Series end date (`YYYY-MM-DD`, default = today)                |
| `--extend-years M` | How many years beyond `end` to extend the x‑axis (default = 3) |

## Customization

* **Normalization**: Insert a normalization step (e.g., percent change from a base date).
* **Export**: Modify the script to save figures with `plt.savefig('chart.png', dpi=300)`.
* **Statistics**: Add `ta.correl()` or use Pandas to compute rolling correlations.

## Troubleshooting

* **"ModuleNotFoundError"**: Ensure your venv is activated, then reinstall dependencies.
* **SSL/DataReader errors**: Upgrade `pandas_datareader` or switch to an alternate data source.

## License

This project is released under the MIT License.
