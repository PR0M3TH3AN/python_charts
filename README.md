# Lagged Oil–Unemployment Chart

A self-contained toolkit that:

* Fetches U.S. unemployment rate (UNRATE) and WTI crude oil price (DCOILWTICO) from FRED
* Stores the series in a local SQLite database (`data/fred.db`)
* Produces a dual-axis plot of unemployment vs. lagged oil price, with customizable lag, date range, and styling

![Example chart](scripts/lagged_oil_unrate_chart_styled.py)

---

## 🚀 Quickstart

```bash
# Clone the repo
git clone https://github.com/your-org/python_charts.git
cd python_charts

# One-command: install deps, download data, and plot
./startup.sh python scripts/lagged_oil_unrate_chart_styled.py \
    --offset 12 --end 2025-05-31 --extend-years 5
```

This will:

1. Create (or reuse) a Python 3 virtual environment (`venv/`)
2. Upgrade `pip` & `setuptools` (providing `distutils` support)
3. Install required packages (offline wheelhouse first, PyPI fallback)
4. Download UNRATE & DCOILWTICO into `data/fred.db` if missing
5. Generate the chart with a 12-month oil lead, extending the x-axis by 5 years

---

## 📁 Repository Structure

```
python_charts/
├── data/
│   └── fred.db                 # Local FRED snapshot (SQLite)
├── scripts/
│   ├── refresh_data.py         # Download and store FRED series
│   ├── lagged_oil_unrate_chart_styled.py  # Plotting script
│   └── pyproject.toml          # Packaging metadata
├── startup.sh                  # Bootstraps venv, deps, data, and runs commands
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## 🛠️ Installation & Setup

1. **Ensure** you have Python 3.8+ installed on your system.
2. **Clone** and navigate into the project:

   ```bash
   git clone https://github.com/your-org/python_charts.git
   cd python_charts
   ```
3. **Make** the startup script executable:

   ```bash
   chmod +x startup.sh
   ```

> On first run, `startup.sh` will build the environment, install dependencies, and pull data.

---

## ⚙️ Usage

### Refresh FRED data

```bash
./startup.sh python scripts/refresh_data.py
```

Downloads the full UNRATE and WTI series (from 1948 to today) into `data/fred.db`.

### Generate the chart

```bash
# Default 18-month lag
./startup.sh

# Custom lag, range, and extension
./startup.sh python scripts/lagged_oil_unrate_chart_styled.py \
    --offset 6 --start 1980-01-01 --end 2025-05-31 --extend-years 2
```

| Option           | Description                                               |
| ---------------- | --------------------------------------------------------- |
| `--offset`       | Lag in months (positive = oil leads; negative = oil lags) |
| `--start`        | Start date (YYYY-MM-DD)                                   |
| `--end`          | End date (YYYY-MM-DD)                                     |
| `--extend-years` | Years to extend the x-axis beyond the end date            |

---

## 📝 Details

* **Data storage**: `data/fred.db` (SQLite) holds two tables: `UNRATE` and `DCOILWTICO`.
* **Plot styling**:

  * Left y-axis: unemployment rate (%) from 3 to 15%, ticks every 2%.
  * Right y-axis: log scale oil price (USD), doubling ticks from \$3 upward.
  * X-axis: years, major tick every 5 years, minor tick every year.

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

`startup.sh` also upgrades `pip` & `setuptools` to ensure `distutils` is available.

---

## 🛡️ Troubleshooting

* **ModuleNotFoundError: distutils**: resolved automatically by upgrading `setuptools` in `startup.sh`.
* **Database not found**: run `./startup.sh python scripts/refresh_data.py` to populate `data/fred.db`.
* **Virtual-env issues**: delete `venv/` and re-run `startup.sh`.

---

## 📄 License

This project is released under the MIT License. See [LICENSE](LICENSE) for details.
