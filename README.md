# Python Charts

This initial chart is a self-contained toolkit that:

* Fetches U.S. unemployment rate (UNRATE) and WTI crude oil price (DCOILWTICO) from FRED  
* Stores the series in a local SQLite database (`data/fred.db`)  
* Produces a dual-axis plot of unemployment vs. lagged oil price, with customizable lag, date range, and styling  

---

## 🚀 Quickstart

```bash
# Clone the repo
git clone https://github.com/your-org/python_charts.git
cd python_charts

# One-command: install deps, download data, and plot
./startup.sh --offset 12 --end 2025-05-31 --extend-years 5
````

This will:

1. Upgrade `pip` & `setuptools` globally
2. Install required packages from `requirements.txt` via

   ```bash
   pip install --upgrade -r requirements.txt
   ```
3. Download UNRATE & DCOILWTICO into `data/fred.db` if missing
4. Generate the chart with a 12-month oil lead, extending the x-axis by 5 years

---

## 📁 Repository Structure

```
python_charts/
├── data/
│   └── fred.db                            # Local FRED snapshot (SQLite)
├── scripts/
│   ├── refresh_data.py                    # Download and store FRED series
│   ├── lagged_oil_unrate_chart_styled.py  # Plotting script
│   └── pyproject.toml                     # Packaging metadata
├── Makefile                               # High-level targets (install, plot, etc.)
├── startup.sh                             # Installs deps globally, fetches data, runs commands
├── requirements.txt                       # Python dependencies
└── README.md                              # This file
```

---

## ⚙️ Usage

### Refresh FRED data

```bash
./startup.sh python scripts/refresh_data.py --series UNRATE CPIAUCSL --start 1960-01-01 --output outputs/chart.png
```

Downloads UNRATE and WTI series (from 1948 to today) into `data/fred.db`.

#### `refresh_data.py` options

| Option     | Description                         |
| ---------- | ----------------------------------- |
| `--series` | One or more FRED series names       |
| `--start`  | Start date in `YYYY-MM-DD` format   |
| `--end`    | End date in `YYYY-MM-DD` format     |

To add new data and plot it later:

1. Download series:

   ```bash
   ./startup.sh python scripts/refresh_data.py --series <names>
   ```

2. Generate a chart with those series:

   ```bash
   ./startup.sh python scripts/custom_chart.py --series <names>
   ```

### Generate the chart

```bash
# Default 18-month lag
./startup.sh

# Custom lag, date range, and extension
./startup.sh --offset 6 --start 1980-01-01 --end 2025-05-31 --extend-years 2
```

The plotting script validates that both series contain data for the
requested period before rendering the chart.

If no `--output` path is provided, each script automatically saves the figure to
`outputs/<script>_<timestamp>.png`, where `<script>` is the script's base name
and `<timestamp>` is the current date and time in `YYYYMMDD_HHMMSS` format.

| Option           | Description                                     |
| ---------------- | ----------------------------------------------- |
| `--offset`       | Lag in months (pos = oil leads; neg = oil lags) |
| `--start`        | Start date (YYYY-MM-DD)                         |
| `--end`          | End date (YYYY-MM-DD)                           |
| `--extend-years` | Years to extend the x-axis beyond the end date  |
| `--output`       | Save the figure to this path before showing it  |

## Custom Charts

Plot any combination of FRED series stored in `data/fred.db` using
`scripts/custom_chart.py`.

```bash
# Example: unemployment and oil
./startup.sh python scripts/custom_chart.py \
    --series UNRATE DCOILWTICO --start 2000-01-01 --end 2020-12-31
```

The same invocation is available via Make:

```bash
make plot-custom ARGS="--series UNRATE DCOILWTICO --start 2000-01-01 --end 2020-12-31"
```
### Bitcoin vs. Global M2

After downloading the required series into `data/fred.db`, generate the Bitcoin overlay chart:

```bash
./startup.sh python scripts/bitcoin_m2_chart.py --btc-series CBBTCUSD --m2-series GLOBAL_M2 --output outputs/chart.png
```


---

## 📝 Details

* **Data storage**: `data/fred.db` (SQLite) contains one table per series (e.g., `UNRATE`, `DCOILWTICO`).
* **Plot styling**:

  * Left y-axis: unemployment rate (%) from 3 to 15%, ticks every 2%.
  * Right y-axis: log scale oil price (USD), doubling ticks from \$3 upward.
  * X-axis: major tick every 5 years, minor tick every year.

---

## 📦 Dependencies

Listed in `requirements.txt`:

```text
pandas>=1.5.0
pandas_datareader>=0.10.0
matplotlib>=3.5.0
lxml>=4.6.0
python-dateutil>=2.8.1
```

---

## 🛡️ Troubleshooting

* **ModuleNotFoundError: distutils**: resolved by `pip install --upgrade setuptools`.
* **Database not found**: run `./startup.sh python scripts/refresh_data.py`.
* **Permission errors**: ensure write access to the project directory.

---

## 📄 License

Released under the MIT License. See [LICENSE](LICENSE) for details.

