#!/usr/bin/env bash

cd ..
echo "Formatting markdown tables..."
npm_config_yes=true npx markdown-table-formatter "./**/*.md"
