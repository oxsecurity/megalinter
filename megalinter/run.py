#!/usr/bin/env python3
"""
Run mega-linter

"""

import megalinter
import uuid

linter = megalinter.Megalinter({
    "cli": True,
    "request_id": uuid.uuid1()
})

# Guess who's there ? :)
megalinter.alpaca()

# Run MegaLinter
linter.run()
