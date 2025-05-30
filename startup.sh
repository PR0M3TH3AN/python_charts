#!/usr/bin/env bash
# -------------------------------------------------------------------
# startup.sh  — prepare Python env, ensure dependencies, FRED data,
#              and run a command inside the venv
# Usage:
#   ./startup.sh [command…]
# Automatically:
#  - Upgrades pip & setuptools (ensuring distutils on Python 3.12+)
#  - Creates venv if missing
#  - Installs requirements
#  - Downloads data/fred.db if missing
# -------------------------------------------------------------------
set -euo pipefail

VENV_DIR="venv"
REQ_FILE="requirements.txt"
WHEELHOUSE="wheelhouse"
DATA_DB="data/fred.db"

# 1) Create or reuse venv
if [[ ! -d "$VENV_DIR" ]]; then
  echo "🔧 Creating virtual-env…"
  python3 -m venv "$VENV_DIR"
fi
# Activate
# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

# 2) Upgrade pip & setuptools (to provide distutils on Py3.12+)
echo "🛠 Upgrading pip & setuptools…"
pip install --upgrade pip setuptools

# 3) Install project dependencies
PIP_OPTS=(install --upgrade --no-input)
if [[ -d "$WHEELHOUSE" ]]; then
  echo "📦 Installing from wheelhouse…"
  pip "${PIP_OPTS[@]}" --no-index --find-links="$WHEELHOUSE" -r "$REQ_FILE" \
    || { echo "⚠️ Wheelhouse failed—falling back to PyPI…"; \
         pip "${PIP_OPTS[@]}" -r "$REQ_FILE"; }
else
  echo "🌐 Installing from PyPI…"
  pip "${PIP_OPTS[@]}" -r "$REQ_FILE"
fi

echo "✅ Virtual-env ready ($(python -V))"

# 4) Ensure data/fred.db exists
if [[ ! -f "$DATA_DB" ]]; then
  echo "🔄 $DATA_DB not found—downloading FRED series…"
  python scripts/refresh_data.py
fi

# 5) Decide what to run
if [[ $# -gt 0 ]]; then
  CMD=("$@")
else
  CMD=(python scripts/lagged_oil_unrate_chart_styled.py --offset 18)
fi

echo "🚀 Executing: ${CMD[*]}"
exec "${CMD[@]}"