#!/usr/bin/env python3
# This file deliberately violates ty type checking.
# It sits inside .wireit, a default excluded directory: the project lint mode
# success test passes only if excluded directories are forwarded to ty
# through --exclude.
x: int = "poison"
