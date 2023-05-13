#!/usr/bin/env python3
"""
Run mega-linter

"""

import uuid

import megalinter

linter = megalinter.Megalinter({"cli": True, "request_id": str(uuid.uuid1())})

# Run MegaLinter
linter.run()
