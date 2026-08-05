#!/usr/bin/env python3
# This file deliberately violates ruff default rules (E401, F401).
# It sits inside .wireit, a default excluded directory: the project lint mode
# success test passes only if excluded directories are forwarded to ruff
# through --extend-exclude.
import os, sys
