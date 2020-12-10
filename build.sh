#!/usr/bin/env bash
set -eu

PYTHONPATH=.
export PYTHONPATH
ls
python ./.automation/build.py
mkdocs build

# Prettify `search_index.json` after `mkdocs` to have better diffs in git.
# `mkdocs` broke this few years ago: https://github.com/mkdocs/mkdocs/pull/1128
python -m json.tool ./site/search/search_index.json > ./site/search/search_index_new.json
mv -f -- ./site/search/search_index_new.json ./site/search/search_index.json
