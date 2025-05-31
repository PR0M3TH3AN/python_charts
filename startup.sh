#!/usr/bin/env bash
# -------------------------------------------------------------------
# startup.sh  — install deps globally, fetch data, then run command
# Usage:
#   ./startup.sh [options]       # passes options to default plot script
#   ./startup.sh <script> [args] # runs specified script with system Python
# Examples:
#   ./startup.sh --offset 12 --end 2025-05-31 --extend-years 5
#   ./startup.sh pytest -q
# -------------------------------------------------------------------
set -euo pipefail

REQ_FILE="requirements.txt"
DATA_DB="data/fred.db"
DEFAULT_MODULE="scripts.lagged_oil_unrate_chart_styled"

# 1) Ensure pip & setuptools are up to date
if [[ -n "${PIP_NO_INDEX:-}" ]]; then
  echo "🔒 Offline mode detected; skipping upgrade"
else
  echo "🛠 Upgrading pip & setuptools…"
  pip install --upgrade pip setuptools
fi

# 2) Install project dependencies globally
echo "📦 Installing dependencies from $REQ_FILE…"
pip install --upgrade -r "$REQ_FILE"

# 3) Ensure data exists
if [[ ! -f "$DATA_DB" ]]; then
  echo "🔄 Data not found—downloading FRED series…"
  python -m scripts.refresh_data
fi

# 4) Dispatch to the right command
if [[ $# -eq 0 ]]; then
  # no args → run default plot module with offset 18
  CMD=(python -m "$DEFAULT_MODULE" --offset 18)
elif [[ "$1" == --* ]]; then
  # args start with -- → forward to default plot module
  CMD=(python -m "$DEFAULT_MODULE" "$@")
else
  # first token is script or other command
  if [[ -f "$1" || "$1" == *.py ]]; then
    # If they explicitly say “scripts/whatever.py …” or “some_test.py …”, run as script
    CMD=(python "$@")
  else
    CMD=("$@")
  fi
fi

echo "🚀 Executing: ${CMD[*]}"
exec "${CMD[@]}"
