#!/usr/bin/env bash
# One-shot setup: venv, dependencies, data download, stats + figures.
set -e
cd "$(dirname "$0")"
python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt
.venv/bin/python scripts/collect_airbnb.py   # ~600 MB, about a minute on a good connection
.venv/bin/python scripts/analyze.py          # writes data/stats.json and figures/*.png
echo "Done. See figures/ and data/stats.json"
