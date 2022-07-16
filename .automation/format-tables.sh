#!/usr/bin/env bash

cd ..
echo "Formatting markdown tables..."
npx --yes markdown-table-formatter "./**/*.md"
