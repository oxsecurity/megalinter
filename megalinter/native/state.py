import contextlib
import json
import os
import time

from megalinter.native.context import NativeError

LOCK_WAIT_SECONDS = 120
LOCK_POLL_SECONDS = 0.2
STALE_LOCK_SECONDS = 600


def state_path(home):
    return os.path.join(home, "state.json")


@contextlib.contextmanager
def state_lock(home):
    lock_file = os.path.join(home, "state.lock")
    deadline = time.time() + LOCK_WAIT_SECONDS
    while True:
        try:
            handle = os.open(lock_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.close(handle)
            break
        except FileExistsError:
            if time.time() - os.path.getmtime(lock_file) > STALE_LOCK_SECONDS:
                os.remove(lock_file)
                continue
            if time.time() > deadline:
                raise NativeError(f"Timeout waiting for {lock_file}") from None
            time.sleep(LOCK_POLL_SECONDS)
    try:
        yield
    finally:
        if os.path.exists(lock_file):
            os.remove(lock_file)


def read_state(home):
    path = state_path(home)
    if not os.path.isfile(path):
        return {"linters": {}, "runtimes": {}}
    with open(path, "r", encoding="utf-8") as f:
        state = json.load(f)
    state.setdefault("linters", {})
    state.setdefault("runtimes", {})
    return state


def update_state(home, section, key, value):
    with state_lock(home):
        state = read_state(home)
        if value is None:
            state[section].pop(key, None)
        else:
            state[section][key] = value
        temp_path = state_path(home) + ".tmp"
        with open(temp_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(state, f, indent=2, sort_keys=True)
        os.replace(temp_path, state_path(home))
