#!/usr/bin/env bash
set -ex

cd ..
echo "format-tables.sh: Formatting markdown tables..."

if [[ -z "${CI}" ]]; then
  echo "Formatting tables by using npx markdown-table-formatter..."
  npx --yes markdown-table-formatter@latest --verbose "./**/*.md"
else
  echo "Formatting tables by installing markdown-table-formatter..."
  npm i markdown-table-formatter@latest -g
  markdown-table-formatter --verbose "./**/*.md"
fi
echo "End formatting markdown tables"
