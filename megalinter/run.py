#!/usr/bin/env python3
"""
Run mega-linter

"""

import megalinter

linter = megalinter.Megalinter({"cli": True})

# Guess who's there ? :)
megalinter.alpaca()

# Run MegaLinter
linter.run()
