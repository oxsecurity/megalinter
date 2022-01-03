#!/usr/bin/env bash

COMMAND=("$@")

tmux new-window -t main "
  trap 'tmux wait-for -S main-neww-done' 0
  $COMMAND
  " \; wait-for main-neww-done