# AGENTS.md — Guidance for OpenAI Codex

## Execution Commands
- **Always** invoke Python scripts via the startup wrapper, which installs dependencies globally and then runs your code under the system Python:
  
  ```bash
  ./startup.sh --offset <months> --end <YYYY-MM-DD> --extend-years <N>
````

* **Never** call `refresh_data.py` from within a Task Command. This environment has **no internet access**, so attempts to fetch external data will fail. Data in `data/fred.db` must already be present.

## Project Overview

This repository, **python\_charts**, provides a framework for fetching economic time series from FRED, storing them locally, and producing custom matplotlib charts with configurable parameters. The core components are:

* **`startup.sh`**: Single‐entrypoint script to install dependencies globally, ensure local data is present, and run specified commands under system Python.
* **`Makefile`**: Convenient high‐level targets (`install`, `data`, `plot`, `plot‐custom`, `test`, `clean`) that funnel through `startup.sh` for reproducible builds.
* **`scripts/refresh_data.py`**: Downloads UNRATE and DCOILWTICO series into `data/fred.db`—**only run in an internet-connected environment**, not in Codex/CI.
* **`scripts/lagged_oil_unrate_chart_styled.py`**: Generates the lagged oil vs. unemployment chart with fixed axes styling and log scale.

Future extensions will add additional custom chart scripts under `scripts/`, all driven by the same bootstrapping and command conventions.

## Usage Conventions

### Primary Commands

* **Bootstrap & default plot**:

  ```bash
  ./startup.sh
  ```

  Installs/upgrades dependencies globally and runs the default lagged‐oil chart with an 18-month offset.

* **Custom plot**:

  ```bash
  ./startup.sh --offset 12 --end 2025-05-31 --extend-years 5
  ```

* **Data refresh (offline environments)**:

  * **Do not** run `refresh_data.py` in Codex/CI — data must already be in `data/fred.db`.
  * To update data in an internet-connected shell, run:

    ```bash
    python scripts/refresh_data.py
    ```

* **Run tests**:

  ```bash
  ./startup.sh pytest -q
  ```

### Argument Rules

* If the first token starts with `--`, it’s forwarded to the default chart script.
* If the first token names a `.py` script, it’s executed via `python <script>`.
* Otherwise, commands are executed directly (e.g., `pytest`, `flake8`).

## Coding Standards

* **Python**: Target version ≥ 3.8. Use type hints for all function signatures. Follow PEP8 with Black formatting.
* **Bash**: `startup.sh` uses `set -euo pipefail`.
* **Makefile**: Use tab-indented commands. All targets should funnel through `startup.sh`.

## Testing & Validation

* **Automated tests**: Add pytest modules under `tests/` following the pattern `test_*.py`.
* **Data mocking**: For new chart scripts, mock FRED downloads via monkeypatching `pandas_datareader.data.DataReader`.

## Extending with New Charts

1. **Create** `scripts/custom_chart.py`.
2. **Implement** a `main()` with `argparse` for `--start`, `--end`, `--offset`, etc.
3. **Invoke** via:

   ```bash
   ./startup.sh python scripts/custom_chart.py --your-args
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

*End of AGENTS.md — tailored for python\_charts repo*