#!/usr/bin/env python3
"""
Run mega-linter

"""

import megalinter

# Guess who's there ? :)
megalinter.alpaca()

# Run Mega-Linter
megalinter.Megalinter({"cli": True}).run()
