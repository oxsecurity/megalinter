#!/usr/bin/env bash
set -ex

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}/.."
echo "format-tables.sh: Formatting markdown tables from $(pwd)..."

if [[ -z "${CI}" ]]; then
  echo "Formatting tables by using npx markdown-table-formatter..."
  find . -name "*.md" -not -path "*/node_modules/*" -not -path "*/.venv/*" -not -path "*/.automation/*" -not -path "*/site/*" -print0 | xargs -0 -n 200 npx --yes markdown-table-formatter@latest --verbose
else
  echo "Formatting tables by installing markdown-table-formatter..."
  npm i markdown-table-formatter@latest -g
  find . -name "*.md" -not -path "*/node_modules/*" -not -path "*/.venv/*" -not -path "*/.automation/*" -not -path "*/site/*" -print0 | xargs -0 -n 200 markdown-table-formatter --verbose
fi
echo "End formatting markdown tables"
