#!/usr/bin/env bash
set -ex

cd ..
echo "format-tables.sh: Formatting markdown tables..."

if [[ -z "${CI}" ]]; then
  echo "Formatting tables by using npx markdown-table-formatter..."
  find . -name "*.md" -not -path "*/node_modules/*" -print0 | xargs -0 npx --yes markdown-table-formatter@latest --verbose
else
  echo "Formatting tables by installing markdown-table-formatter..."
  npm i markdown-table-formatter@latest -g
  find . -name "*.md" -not -path "*/node_modules/*" -print0 | xargs -0 markdown-table-formatter --verbose
fi
echo "End formatting markdown tables"
