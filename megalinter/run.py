#!/usr/bin/env python3
"""
Run mega-linter

"""

import multiprocessing as mp
import uuid

import megalinter


def main() -> None:
    linter = megalinter.Megalinter({"cli": True, "request_id": str(uuid.uuid1())})

    # Run MegaLinter
    linter.run()


if __name__ == "__main__":
    mp.freeze_support()
    main()
