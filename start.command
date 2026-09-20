#!/usr/bin/env bash
# DataReady launcher (macOS, double-clickable).
cd "$(dirname "$0")"

PYTHON=python3
if [ -x "runtime/python/bin/python3" ]; then
  PYTHON="runtime/python/bin/python3"
fi

if ! "$PYTHON" -c "import nicegui" >/dev/null 2>&1; then
  echo "DataReady needs its dependencies. Installing them now…"
  "$PYTHON" -m pip install -r requirements.txt
fi

"$PYTHON" main.py