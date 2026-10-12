#!/usr/bin/env bash
# Start IDRF Reader on Linux or macOS:  ./run.sh
set -e
cd "$(dirname "$0")"

if [ ! -f .env ]; then
  cp .env.example .env
  echo
  echo "  A settings file .env was created."
  echo "  Open it, change ADMIN_PASSWORD, save it, then run ./run.sh again."
  echo
  exit 1
fi

if [ ! -x .venv/bin/python ]; then
  echo "Creating a Python environment, first time only..."
  python3 -m venv .venv
fi

.venv/bin/python -m pip install --quiet --upgrade pip
.venv/bin/python -m pip install --quiet -r requirements.txt
exec .venv/bin/python run.py
