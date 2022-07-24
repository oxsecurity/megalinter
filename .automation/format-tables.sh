#!/usr/bin/env bash
set -e

cd ..
echo "Formatting markdown tables..."

if [[ -z "${CI}" ]]; then
  echo "Formatting tables by using npx markdown-table-formatter..."
  npx --yes markdown-table-formatter@latest "./**/*.md"
else
  echo "Formatting tables by installing markdown-table-formatter..."
  npm i markdown-table-formatter@latest -g
  markdown-table-formatter "./**/*.md"
fi
