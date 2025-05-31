# AGENTS.md — Guidance for OpenAI Codex

## Execution Commands
- **Always** invoke Python scripts via the `startup.sh` wrapper, which installs dependencies globally and then runs your code under the system Python. In particular, don’t run a `.py` file directly if it uses imports like `from scripts.common …`. Instead, run it as a module or let `startup.sh` handle it. For example:

  ```bash
  # Preferred: let startup.sh dispatch to scripts.lagged_oil_unrate_chart_styled
  ./startup.sh --offset <months> --end <YYYY-MM-DD> --extend-years <N>

  # Or explicitly in module mode, so that 'scripts' is on PYTHONPATH:
  ./startup.sh python -m scripts.lagged_oil_unrate_chart_styled --offset <months> --end <YYYY-MM-DD> --extend-years <N>
````

* Running a script this way ensures that `import scripts.common` (and other `scripts.*` imports) resolve correctly.

* If you ever need to call a different script, still invoke it under `./startup.sh`, for example:

  ```bash
  # Custom-chart example:
  ./startup.sh python -m scripts.custom_chart --series UNRATE DCOILWTICO --start 2000-01-01 --end 2020-12-31
  ```

* **Never** call `refresh_data.py` from within a Task Command. This environment has **no internet access**, so attempts to fetch external data will fail. Data in `data/fred.db` must already be present. If you need to refresh data, run it only in an internet-connected shell:

  ```bash
  python scripts/refresh_data.py --series UNRATE DCOILWTICO --start 1973-01-01
  ```

## Policy for Handling UNRATE Null Values

When generating the UNRATE vs. Oil chart, the UNRATE series may include a `NaN` for the most recent month if that month’s data has not yet been published. To prevent the script from raising a `ValueError: UNRATE contains null values`, follow this policy:

1. **Clamp to Last Valid Index**

   * After loading `unrate` and `oil` with `fetch_series(...)`, immediately determine the last non-NaN date in the `unrate` DataFrame using:

     ```python
     last_date = unrate.last_valid_index()
     ```
   * Truncate both `unrate` and `oil` so that any trailing `NaN` row in `unrate` (and the corresponding index in `oil`) is removed:

     ```python
     unrate = unrate.loc[:last_date]
     oil    = oil.loc[:last_date]
     ```
   * Only after this truncation should you call `validate_series(unrate, oil)`. This ensures that neither DataFrame contains nulls and that they share a valid overlapping date range.

2. **Rationale**

   * Doing a forward-fill or dropping all NaNs could inadvertently hide missing data or distort recent observations. Clamping to the last officially published month preserves data purity.
   * By slicing both series at `last_valid_index()`, you ensure that the chart is plotted only with officially released data and no “estimate” for the current month.

3. **Implementation in `lagged_oil_unrate_chart_styled.py`**

   * Right after:

     ```python
     unrate, oil = fetch_series(start_dt, end_dt, args.db)
     ```

     insert:

     ```python
     last_date = unrate.last_valid_index()
     unrate = unrate.loc[:last_date]
     oil    = oil.loc[:last_date]
     ```
   * Then proceed to `validate_series(unrate, oil)` and the usual plotting logic.

## Project Overview

This repository, **python\_charts**, provides a framework for fetching economic time series from FRED, storing them locally, and producing custom matplotlib charts with configurable parameters. The core components are:

* **`startup.sh`**: Single‐entrypoint script to install dependencies globally, ensure local data is present, and run specified commands under system Python.
* **`Makefile`**: Convenient high‐level targets (`install`, `data`, `plot`, `plot‐custom`, `test`, `clean`) that funnel through `startup.sh` for reproducible builds.
* **`scripts/refresh_data.py`**: Downloads UNRATE and DCOILWTICO series into `data/fred.db`—**only run in an internet-connected environment**, not in Codex/CI.
* **`scripts/lagged_oil_unrate_chart_styled.py`**: Generates the lagged oil vs. unemployment chart with fixed axes styling and log scale.
* **`scripts/bitcoin_m2_chart.py`**: Produces a Bitcoin vs. global M2 overlay chart with adjustable day offset.
* **`scripts/custom_chart.py`**: Plots arbitrary FRED series stored in `data/fred.db`.

Future extensions will add additional custom chart scripts under `scripts/`, all driven by the same bootstrapping and command conventions.

## Usage Conventions

### Primary Commands

* **Bootstrap & default plot**:

  ```bash
  ./startup.sh
  ```

  Installs/upgrades dependencies globally and runs the default lagged-oil chart with an 18-month offset.

* **Custom plot**:

  ```bash
  ./startup.sh --offset 12 --end 2025-05-31 --extend-years 5
  ```

  (Equivalent to `./startup.sh python -m scripts.lagged_oil_unrate_chart_styled --offset 12 --end 2025-05-31 --extend-years 5`.)

* **Data refresh (offline environments)**:

  * **Do not** run `refresh_data.py` in Codex/CI — data must already be in `data/fred.db`.
  * To update data in an internet-connected shell, run:

    ```bash
    python scripts/refresh_data.py --series UNRATE DCOILWTICO
    ```

* **Run tests**:

  ```bash
  ./startup.sh pytest -q
  ```

### Argument Rules

* If the first token starts with `--`, it’s forwarded to the default chart script (`scripts.lagged_oil_unrate_chart_styled`).
* If the first token names a `.py` script, it’s executed via `python <script>` only when you explicitly need to bypass `startup.sh`.
* Otherwise, commands are executed directly (e.g., `pytest`, `flake8`).

## Coding Standards

* **Python**: Target version ≥ 3.8. Use type hints for all function signatures. Follow PEP8 with Black formatting.
* **Bash**: `startup.sh` uses `set -euo pipefail`.
* **Makefile**: Use tab-indented commands. All targets should funnel through `startup.sh`.

## Testing & Validation

* **Automated tests**: Add pytest modules under `tests/` following the pattern `test_*.py`.
* **Data mocking**: For new chart scripts, mock FRED downloads via monkeypatching `pandas_datareader.data.DataReader`.
* **Figure tests**: `tests/test_plot.py` ensures `plot_lagged` returns a figure with two axes and at least one line.

## Extending with New Charts

1. **Create** `scripts/custom_chart.py`.
2. **Implement** a `main()` with `argparse` for `--start`, `--end`, `--offset`, etc.
3. **Invoke** via:

   ```bash
   ./startup.sh python -m scripts.custom_chart --your-args
   ```
4. **Optionally** add a Makefile target if desired.

## CI / Codex Integration

* **Setup Script** →

  ```bash
  chmod +x startup.sh && ./startup.sh
  ```
* **Task Command** →

  ```bash
  ./startup.sh --offset 18
  ```