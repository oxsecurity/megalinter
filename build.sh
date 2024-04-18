#!/usr/bin/env bash
set -eu

PYTHONPATH=.
export PYTHONPATH
if type python3 >/dev/null 2>/dev/null; then
  python3 ./.automation/build.py "$@"
else
  python ./.automation/build.py "$@"
fi

# Build online documentation
if type python3 >/dev/null 2>/dev/null; then
  python3 -m mkdocs build
else
  python -m mkdocs build
fi

# Prettify `search_index.json` after `mkdocs`
# `mkdocs` removed its own prettify few years ago: https://github.com/mkdocs/mkdocs/pull/1128
if type python3 >/dev/null 2>/dev/null; then
  python3 -m json.tool ./site/search/search_index.json >./site/search/search_index_new.json
else
  python -m json.tool ./site/search/search_index.json >./site/search/search_index_new.json
fi
mv -f -- ./site/search/search_index_new.json ./site/search/search_index.json
