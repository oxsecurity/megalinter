#!/usr/bin/env bash

cd ..
echo "Formatting markdown tables..."
# shellcheck disable=SC2086
MD_FILES=$(find . -type f -name "*.md" -not -path "*/node_modules/*" -not -path "*/.automation/*") && npx markdown-table-formatter $MD_FILES
