#!/usr/bin/env python3
"""
Run mega-linter

"""

import faulthandler
import multiprocessing as mp
import threading
import uuid

import megalinter

# musl (Alpine) gives every thread a 128 KiB stack, where glibc gives 8 MiB, and
# CPython below 3.14.7 miscomputed its stack guard there. Deep recursion in a
# thread then crashed the process with SIGSEGV instead of raising RecursionError:
# multiprocessing.Pool pickles the linter object graph (which reaches the whole
# Megalinter instance through Linter.master) inside its handler threads, which is
# exactly such a recursion. Ask for a glibc-sized stack for the threads we create.
THREAD_STACK_SIZE = 8 * 1024 * 1024


def enable_crash_diagnostics() -> None:
    # Print a traceback when killed by SIGSEGV, SIGBUS, SIGFPE, SIGABRT or SIGILL,
    # instead of dying silently and leaving nothing to report. A stack overflow is
    # the one case this can not report, as the handler has no stack left to run on:
    # that case is what the thread stack size below prevents.
    faulthandler.enable()
    # Only applies to threads started after this call, so it must run before the
    # logging queue listener and the linters pool are created
    threading.stack_size(THREAD_STACK_SIZE)


def main() -> None:
    enable_crash_diagnostics()

    linter = megalinter.Megalinter({"cli": True, "request_id": str(uuid.uuid1())})

    # Run MegaLinter
    linter.run()


if __name__ == "__main__":
    mp.freeze_support()
    main()
