# Python Charts [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

This initial chart is a self‐contained toolkit that:

* Fetches U.S. unemployment rate (UNRATE) and WTI crude oil price (DCOILWTICO) from FRED :contentReference[oaicite:1]{index=1}  
* Stores the series in a local SQLite database (`data/fred.db`) :contentReference[oaicite:2]{index=2}  
* Produces a dual‐axis plot of unemployment vs. lagged oil price, with customizable lag, date range, and styling :contentReference[oaicite:3]{index=3}  

## Table of Contents
- [Quickstart](#quickstart)
- [Repository Structure](#repository-structure)
- [Usage](#usage)
- [Custom Charts](#custom-charts)
- [Details](#details)
- [Dependencies](#dependencies)
- [Troubleshooting](#troubleshooting)
- [License](#license)


---

## 🚀 Quickstart

```bash
# Clone the repo
git clone https://github.com/your-org/python_charts.git
cd python_charts

# Create and activate your virtual environment
python3 -m venv venv
source venv/bin/activate
# Plot the lagged UNRATE vs. Oil chart
./startup.sh lagged_oil_unrate --offset 12 --end 2025-05-31 --extend-years 5
```

This will:

1. Upgrade `pip` & `setuptools` globally
2. Install required packages from `requirements.txt` automatically
3. Download UNRATE & DCOILWTICO into `data/fred.db` if missing (\[Stack Overflow]\[3], \[martinheinz.dev]\[4])
4. Generate the chart with a 12‐month oil lead, extending the x‐axis by 5 years (\[martinheinz.dev]\[4], \[Real Python]\[1])

---

## 📁 Repository Structure

```
python_charts/
├── data/
│   └── fred.db                            # Local FRED snapshot (SQLite)
├── scripts/
│   ├── __init__.py                        # Marks this folder as a Python package
│   ├── common.py                          # Data‐loading, validation, and save_figure utils
│   ├── refresh_data.py                    # Downloads and stores FRED series
│   ├── lagged_oil_unrate_chart_styled.py  # Offline plot of UNRATE vs. WTI oil with lag
│   ├── bitcoin_m2_chart.py                # Plot Bitcoin vs. Global M2 overlay
│   └── custom_chart.py                    # Generic plotting for arbitrary FRED series
├── outputs/                               # Generated chart files (PNGs)
├── Makefile                               # High‐level targets (install, data, plot, etc.)
├── startup.sh                             # Installs dependencies, ensures data, runs commands
├── requirements.txt                       # Python dependencies
└── README.md                              # This file
```

> **Note:** An empty `scripts/__init__.py` file has been added so that Python treats `scripts/` as a package. Because of this, each script can import `common.py` via:
>
> ```python
> from scripts.common import fetch_series_db, save_figure, validate_dataframe, validate_overlap
> ```
>
> rather than `from common import …`. (\[Real Python]\[1], \[Software Engineering Stack Exchange]\[2])

---

## ⚙️ Usage

### 1. Refresh FRED Data

To refresh (or initially populate) the SQLite database with FRED series, run:

```bash
# Either let startup.sh dispatch via alias:
./startup.sh refresh_data --series UNRATE CPIAUCSL --start 1960-01-01 --output outputs/chart.png

# Or invoke it directly as a module (dependencies must already be installed):
python -m scripts.refresh_data --series UNRATE CPIAUCSL --start 1960-01-01 --output outputs/chart.png
```

This command:

* Connects to FRED via `pandas_datareader`
* Downloads the specified series (e.g., `UNRATE` and `CPIAUCSL`) from the start date through today
* Writes each series to its own table in `data/fred.db`
* Saves a PNG of any default plot (if `--output` is provided) to `outputs/` (\[Stack Overflow]\[3], \[GitHub]\[5])

#### `refresh_data.py` options

| Option     | Description                                              |
| ---------- | -------------------------------------------------------- |
| `--series` | One or more FRED series names (e.g., UNRATE, DCOILWTICO) |
| `--start`  | Start date in `YYYY-MM-DD` format                        |
| `--end`    | End date in `YYYY-MM-DD` format (defaults to today)      |

##### Example:

```bash
# Populate fred.db with four series (UNRATE, WTI, Bitcoin, and Global M2)
./startup.sh refresh_data --series UNRATE DCOILWTICO CBBTCUSD GLOBAL_M2 --start 1973-01-01
```

---

### 2. Generate the Default UNRATE vs. Oil Chart

Once data is present, generate the dual‐axis plot of UNRATE vs. lagged WTI oil price:

```bash
# Default: 18‐month lag, default date range (1973‐01‐01 to today), and 3‐year extension
./startup.sh lagged_oil_unrate --offset 18
```

What happens under the hood:

1. `startup.sh` sees `--offset 18` and forwards it to the default module `scripts.lagged_oil_unrate_chart_styled` as:

   ```bash
   python -m scripts.lagged_oil_unrate_chart_styled --offset 18
   ```
2. The script imports `UNRATE` and `DCOILWTICO` from `fred.db` via:

   ```python
   from scripts.common import fetch_series_db, save_figure, validate_dataframe, validate_overlap
   ```

   (\[Real Python]\[1], \[Software Engineering Stack Exchange]\[2])
3. Converts both series to month‐end indices, resamples oil to a monthly average, and aligns their date ranges.
4. Validates that neither series is empty, contains `NaN`, or has no overlap (raising a `ValueError` if any issue).
5. Applies the specified lag (e.g., 18 months), then plots UNRATE on the left y‐axis and log‐scaled WTI on the right y‐axis.
6. Saves the figure to `outputs/lagged_oil_unrate_chart_styled_<timestamp>.png` (unless `--output` is specified). (\[martinheinz.dev]\[4], \[Real Python]\[1])

#### Customizing the UNRATE vs. Oil Chart

```bash
# 6‐month lag, start in 1980, end in 2025‐05‐31, extend by 2 years
./startup.sh lagged_oil_unrate --offset 6 --start 1980-01-01 --end 2025-05-31 --extend-years 2
```

| Option           | Description                                                              |
| ---------------- | ------------------------------------------------------------------------ |
| `--offset`       | Lag in months (positive means oil is shifted forward relative to UNRATE) |
| `--start`        | Start date for both series (`YYYY-MM-DD`)                                |
| `--end`          | End date for both series (`YYYY-MM-DD`)                                  |
| `--extend-years` | Number of years to extend the x‐axis beyond the end date                 |
| `--output`       | Save the figure to this path (PNG or PDF)                                |

> **Note:** If you do not specify `--output`, `save_figure(...)` creates a timestamped PNG in `outputs/` by default:
> `outputs/lagged_oil_unrate_chart_styled_20250531_121045.png` (\[Python Packaging]\[6], \[Real Python]\[1])

---

## Custom Charts

You can plot any combination of FRED series stored in `data/fred.db` using `scripts/custom_chart.py`. Each column in the DataFrame is plotted on a shared axis.

```bash
# Either let startup.sh dispatch via alias:
./startup.sh custom_chart --series UNRATE DCOILWTICO --start 2000-01-01 --end 2020-12-31

# Or invoke it directly as a module (dependencies must already be installed):
python -m scripts.custom_chart --series UNRATE DCOILWTICO --start 2000-01-01 --end 2020-12-31
```

* Internally, `custom_chart.py` invokes:

  ```python
  from scripts.common import fetch_series_db, save_figure
  ```

  to load the requested series and save the figure.
* The same invocation is available via Make:

  ````bash
  make plot-custom ARGS="--series UNRATE DCOILWTICO --start 2000-01-01 --end 2020-12-31"
  ``` :contentReference[oaicite:12]{index=12}  
  ````

---

### Bitcoin vs. Global M2

Before running `bitcoin_m2_chart.py`, make sure the Bitcoin price
(`CBBTCUSD`) and global M2 (`GLOBAL_M2`) series exist in `data/fred.db`. If the database is missing these tables, fetch them with `refresh_data.py`:

```bash
# Either let startup.sh dispatch via alias:
./startup.sh refresh_data --series CBBTCUSD GLOBAL_M2 --start 2010-01-01

# Or invoke it directly as a module (dependencies must already be installed):
python -m scripts.refresh_data --series CBBTCUSD GLOBAL_M2 --start 2010-01-01
```

Once the data is present, generate the Bitcoin‐Global M2 overlay chart:

```bash
# Either let startup.sh dispatch via alias:
./startup.sh bitcoin_m2 --btc-series CBBTCUSD --m2-series GLOBAL_M2 --output outputs/chart.png

# Or invoke it directly as a module (dependencies must already be installed):
python -m scripts.bitcoin_m2_chart --btc-series CBBTCUSD --m2-series GLOBAL_M2 --output outputs/chart.png
```

* This script:

  1. Imports both series from `fred.db` with:

     ```python
     from scripts.common import fetch_series_db, save_figure
     ```

     (\[Real Python]\[1], \[Software Engineering Stack Exchange]\[2])
  2. Renames each column to `"value"` for consistency.
  3. Finds the overlapping date range, shifts M2 by `--offset` (default = 94 days), and overlays the two series on dual axes.
  4. Saves the figure—e.g., `outputs/bitcoin_m2_chart_20250531_090608.png` (\[martinheinz.dev]\[4], \[Real Python]\[1])

> **CLI Options for `bitcoin_m2_chart.py`:**
>
> | Option           | Default      | Description                                      |
> | ---------------- | ------------ | ------------------------------------------------ |
> | `--btc-series`   | `CBBTCUSD`   | FRED series code for Bitcoin price               |
> | `--m2-series`    | `GLOBAL_M2`  | FRED series code for global M2 money supply      |
> | `--start`        | `2010-01-01` | Start date for fetching both series              |
> | `--end`          | Today        | End date for fetching both series                |
> | `--offset`       | `94`         | Shift M2 by this many days (positive → M2 leads) |
> | `--extend-years` | `1`          | Years beyond `end` to extend the x‐axis          |
> | `--output`       | None         | Optional path to save the figure (PNG/PDF)       |

---

## 📝 Details

* **Data storage**:

  * `data/fred.db` (SQLite) contains one table per FRED series—each table has columns `date` (as the index) and `<SERIES_NAME>` for the value (\[Stack Overflow]\[3], \[martinheinz.dev]\[4]).

* **Plot styling**:

  * **Lagged oil vs. UNRATE chart**:

    * Left y‐axis: Unemployment rate (%) from 3% to 15%, with tick marks every 2%
    * Right y‐axis: WTI oil price (USD) on a log scale; ticks double starting at \$3 (i.e., 3, 6, 12, 24, etc.) (\[martinheinz.dev]\[4], \[Real Python]\[1])
    * X‐axis: Major tick every 5 years, minor tick every year; format ticks as `%Y` (e.g., 1980, 1985, 1990) (\[Real Python]\[1], \[martinheinz.dev]\[4])

  * **Bitcoin vs. Global M2 chart**:

    * Left y‐axis: Bitcoin price (USD) as a linear scale
    * Right y‐axis: Global M2 (billions of USD) as a linear scale
    * X‐axis: Same date formatting as above (major = every 5 years, minor = yearly) (\[Real Python]\[1], \[martinheinz.dev]\[4])

* **Utility functions in `common.py`**:

  * `fetch_series_db(series_list, start, end, db_path)`

    * Opens `data/fred.db`, reads each series table, slices by date range, and concatenates into a single DataFrame, sorted by date. Raises `FileNotFoundError` if `fred.db` is missing. (\[Stack Overflow]\[3], \[martinheinz.dev]\[4])
  * `validate_dataframe(df, name)`

    * Confirms the DataFrame is nonempty, has a `"value"` column, contains no nulls, and uses a `DatetimeIndex`. Raises `ValueError` otherwise. (\[devgem.io]\[7], \[Real Python]\[1])
  * `validate_overlap(df1, df2)`

    * Checks for a nonempty overlap in dates between two series; raises `ValueError` if there is no intersection. (\[devgem.io]\[7], \[Real Python]\[1])
  * `save_figure(fig, output, script_path)`

    * Saves the Matplotlib `Figure` to either the given `output` path or `outputs/<script>_<timestamp>.png`. (\[Python Packaging]\[6], \[Real Python]\[1])

---

## 📦 Dependencies

All Python dependencies are listed in `requirements.txt` and are installed by `./startup.sh`:

```text
pandas>=1.5.0
pandas_datareader>=0.10.0
matplotlib>=3.5.0
lxml>=4.6.0
python-dateutil>=2.8.1
```

> **Tip:** If you run into `ModuleNotFoundError: distutils`, resolve it by upgrading `setuptools`:
>
> ````bash
> pip install --upgrade setuptools
> ``` :contentReference[oaicite:23]{index=23}  
> ````

---

## 🛡️ Troubleshooting

* **ModuleNotFoundError: `scripts.common` not found**

  * Ensure you have added `scripts/__init__.py` and that all `from common import …` lines have been updated to `from scripts.common import …`. Then rerun:

    ```bash
    # Run the default lagged-oil chart via startup.sh
    ./startup.sh lagged_oil_unrate --offset 18
    ```

    or, if you prefer the module form:

    ```bash
    python -m scripts.lagged_oil_unrate_chart_styled --offset 18
    ```

* **`ValueError: UNRATE contains null values`**

  * This indicates that the UNRATE DataFrame has missing (NaN) entries. Possible fixes:

    1. Drop nulls within SQL—e.g., run `refresh_data.py --end` using the last fully published month rather than “today” (\[devgem.io]\[7], \[pyOpenSci]\[8])
    2. Forward‐fill or backward‐fill missing UNRATE values in `common.py` before validation (if appropriate) (\[pyOpenSci]\[8], \[Real Python]\[1])
    3. Comment out the strict null check in `validate_dataframe(...)` (not recommended for publication‐quality charts) (\[devgem.io]\[7], \[Real Python]\[1])

* **Database not found**

  * If `data/fred.db` does not exist (e.g., fresh clone), run:

    ````bash
    # Using startup.sh to run via alias
    ./startup.sh refresh_data --series UNRATE DCOILWTICO

    # Or run it as a module directly
    python -m scripts.refresh_data --series UNRATE DCOILWTICO
    ``` :contentReference[oaicite:28]{index=28}  

    ````

* **Permission errors**

  * Ensure you have write access to the project directory, especially for `data/` and `outputs/`. (\[Real Python]\[1], \[Roy's Blog]\[9])

---

## 📄 License

Released under the MIT License. See [LICENSE](LICENSE) for details. (\[Roy's Blog]\[9], \[Real Python]\[1])
