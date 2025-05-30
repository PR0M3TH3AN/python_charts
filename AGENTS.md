# AGENTS.md — Guidance for OpenAI Codex

## Project Overview

This repository, **python\_charts**, provides a framework for fetching economic time series from FRED, storing them locally, and producing custom matplotlib charts with configurable parameters. The core components are:

* **`startup.sh`**: Single-entrypoint script to bootstrap a Python venv, install dependencies, fetch data, and run specified commands under the venv interpreter.
* **`Makefile`**: Convenient high-level targets (`install`, `data`, `plot`, `plot-custom`, `test`, `clean`) that funnel through `startup.sh` for reproducible builds.
* **`scripts/refresh_data.py`**: Downloads UNRATE and DCOILWTICO series into `data/fred.db`.
* **`scripts/lagged_oil_unrate_chart_styled.py`**: Generates the lagged oil vs. unemployment chart with fixed axes styling and log scale.

Future extensions will add additional custom chart scripts under `scripts/`, all driven by the same bootstrapping and command conventions.

## Usage Conventions

### Primary Commands

* **Bootstrap & default plot**: `./startup.sh` or `make plot` — runs the lagged-oil chart with an 18‑month offset.
* **Custom plot**: `./startup.sh --offset 12 --end 2025-05-31 --extend-years 5` or `make plot-custom ARGS="--offset 12 --end 2025-05-31 --extend-years 5"`.
* **Data refresh**: `./startup.sh scripts/refresh_data.py` or `make data`.
* **Run tests**: `./startup.sh pytest -q` or `make test`.

### Argument Rules

* Arguments beginning with `--` are forwarded to the default chart script.
* If the first token is a `.py` script or executable, it is invoked under the venv’s Python.
* Otherwise, commands are executed directly (e.g. linters, test frameworks).

## Coding Standards

* **Python**: Target version 3.12. Use type hints for all function signatures. Follow PEP8 with **Black** formatting.
* **Bash**: `startup.sh` must use `set -euo pipefail` and always call `$VENV_DIR/bin/python` to avoid system‑Python mismatches.
* **Makefile**: Use tab‑indented commands. All tasks should funnel to `startup.sh`.

## Testing & Validation

* **Automated tests**: No current tests; add pytest modules under `tests/` following the pattern `test_*.py`.
* **Data mocking**: For new chart scripts, mock FRED downloads via monkeypatching `pandas_datareader.data.DataReader`.

## Extending with New Charts

1. **Create a new script** under `scripts/`, for example `scripts/custom_chart.py`.
2. **Implement** a `main()` accepting `--start`, `--end`, `--offset` or custom args using `argparse`.
3. **Leverage** `startup.sh` invocation: add usage example in your script’s docstring.
4. **Update** the `Makefile` if you need a dedicated target, otherwise users can call:

   ```bash
   ./startup.sh python scripts/custom_chart.py --your-args
   ```

## CI / Codex Integration

* In Codex cloud or CLI tasks, set the **Setup Script** to `./startup.sh install data` to ensure dependencies and data are ready.
* **Task Commands** should call `make plot` or `make test`, which delegates to `startup.sh`.
* **AGENTS.md** is automatically loaded by Codex to understand structure and commands.

## PR & Commit Guidelines

* Prefix branches/PRs with `feature/` or `fix/`.
* Commit messages: `<type>(<scope>): <description>` (e.g. `feat(charts): add custom inflation plot`).
* Include screenshots or saved chart outputs under `outputs/` for visual verification.

---

*End of AGENTS.md — tailored for python\_charts repo*
