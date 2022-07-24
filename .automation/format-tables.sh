#!/usr/bin/env bash

cd ..
echo "Formatting markdown tables..."

if [[ -z "${CI}" ]]; then
  npm i markdown-table-formatter -g
  markdown-table-formatter "./**/*.md"
else
  npx --yes markdown-table-formatter "./**/*.md"
fi
