#!/usr/bin/env bash
# -------------------------------------------------------------------
# startup.sh  — prepare Python env, ensure deps & data, then run.
# Usage:
#   ./startup.sh [options]      # passes options to default plot script
#   ./startup.sh [script or cmd] # runs specified script/command
# Examples:
#   ./startup.sh --offset 12 --end 2025-05-31 --extend-years 5
#   ./startup.sh pytest -q
# -------------------------------------------------------------------
set -euo pipefail

VENV_DIR="venv"
REQ_FILE="requirements.txt"
WHEELHOUSE="wheelhouse"
DATA_DB="data/fred.db"
PYTHON="$VENV_DIR/bin/python"
DEFAULT_SCRIPT="scripts/lagged_oil_unrate_chart_styled.py"

# 1) Create or reuse venv
if [[ ! -d "$VENV_DIR" ]]; then
  echo "🔧 Creating virtual-env…"
  python3 -m venv "$VENV_DIR"
fi

# 2) Activate venv
# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

# 3) Upgrade pip & setuptools
echo "🛠 Upgrading pip & setuptools…"
$PYTHON -m pip install --upgrade pip setuptools

# 4) Install dependencies
PIP_OPTS=(install --upgrade --no-input)
if [[ -d "$WHEELHOUSE" ]]; then
  echo "📦 Installing from wheelhouse…"
  $PYTHON -m pip "${PIP_OPTS[@]}" --no-index --find-links="$WHEELHOUSE" -r "$REQ_FILE" \
    || { echo "⚠️ Wheelhouse failed—falling back…"; \
         $PYTHON -m pip "${PIP_OPTS[@]}" -r "$REQ_FILE"; }
else
  echo "🌐 Installing from PyPI…"
  $PYTHON -m pip "${PIP_OPTS[@]}" -r "$REQ_FILE"
fi

echo "✅ Virtual-env ready ($($PYTHON -V))"

# 5) Ensure data exists
if [[ ! -f "$DATA_DB" ]]; then
  echo "🔄 Data not found—downloading FRED series…"
  $PYTHON scripts/refresh_data.py
fi

# 6) Build command
if [[ $# -eq 0 ]]; then
  CMD=("$PYTHON" "$DEFAULT_SCRIPT" --offset 18)
elif [[ "$1" == --* ]]; then
  CMD=("$PYTHON" "$DEFAULT_SCRIPT" "$@")
else
  if [[ -f "$1" || "$1" == *.py ]]; then
    CMD=("$PYTHON" "$@")
  else
    CMD=("$@")
  fi
fi

# 7) Execute
echo "🚀 Executing: ${CMD[*]}"
exec "${CMD[@]}"
