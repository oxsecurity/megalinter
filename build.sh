#!/usr/bin/env bash
set -eu

PYTHONPATH=.
export PYTHONPATH
python ./.automation/build.py

# Prettify markdown tables
echo "Formatting markdown tables..."
# shellcheck disable=SC2086
MD_FILES=$(find . -type f -name "*.md" -not -path "*/node_modules/*" -not -path "*/.automation/*") && npx markdown-table-formatter $MD_FILES

# Build online documentation
mkdocs build

# Prettify `search_index.json` after `mkdocs`
# `mkdocs` removed its own prettify few years ago: https://github.com/mkdocs/mkdocs/pull/1128
python -m json.tool ./site/search/search_index.json > ./site/search/search_index_new.json
mv -f -- ./site/search/search_index_new.json ./site/search/search_index.json

