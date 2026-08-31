#!/usr/bin/env bash
set -eu

PYTHONPATH=.
export PYTHONPATH
if type python3 >/dev/null 2>/dev/null; then
  python3 ./.automation/build.py "$@"
else
  python ./.automation/build.py "$@"
fi

# Regenerate observability dashboards from the metrics contract
if type python3 >/dev/null 2>/dev/null; then
  python3 ./.automation/build_dashboards.py
else
  python ./.automation/build_dashboards.py
fi

# Build online documentation
zensical build
