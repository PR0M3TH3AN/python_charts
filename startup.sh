#!/usr/bin/env bash
# -------------------------------------------------------------------
# startup.sh — bootstrap environment and dispatch chart aliases
# Usage:
#   ./startup.sh [alias] [args]
# Aliases:
#   bitcoin_m2       → scripts.bitcoin_m2_chart
#   lagged_oil_unrate → scripts.lagged_oil_unrate_chart_styled
#   custom_chart     → scripts.custom_chart
#   refresh_data     → scripts.refresh_data (optional)
# If alias is omitted, defaults to lagged_oil_unrate with --offset 18.
# -------------------------------------------------------------------
set -euo pipefail

REQ_FILE="requirements.txt"
DATA_DB="data/fred.db"

echo "🛠 Upgrading pip…"
if [[ "${PIP_NO_INDEX:-}" != "1" ]]; then
  pip install --upgrade pip
fi

echo "📦 Installing dependencies from $REQ_FILE…"
pip install --upgrade -r "$REQ_FILE"

if [[ ! -f "$DATA_DB" ]]; then
  echo "🔄 data/fred.db missing; running refresh_data…"
  python -m scripts.refresh_data
fi

if [[ $# -eq 0 ]]; then
  exec python -m scripts.lagged_oil_unrate_chart_styled --offset 18
fi

alias="$1"
shift || true

case "$alias" in
  bitcoin_m2)
    exec python -m scripts.bitcoin_m2_chart "$@"
    ;;
  lagged_oil_unrate)
    exec python -m scripts.lagged_oil_unrate_chart_styled "$@"
    ;;
  custom_chart)
    exec python -m scripts.custom_chart "$@"
    ;;
  refresh_data)
    exec python -m scripts.refresh_data "$@"
    ;;
  --*)
    exec python -m scripts.lagged_oil_unrate_chart_styled "$alias" "$@"
    ;;
  *)
    if [[ -f "$alias" || "$alias" == *.py ]]; then
      exec python "$alias" "$@"
    else
      exec "$alias" "$@"
    fi
    ;;
esac

