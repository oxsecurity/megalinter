import logging

from megalinter import config
from megalinter.native.context import NativeError

ALL_KEYWORD = "all"
ALL_WARNING = (
    "NATIVE_LINTERS contains 'all': every linter matching your configuration will be "
    "installed on this machine. This is discouraged: it is slower (many linters to "
    "download and install), and you must fully trust the security of every matching "
    "linter, as linters (and the configuration files they load) can execute the code "
    "of the analyzed repository. Prefer listing only the linters you need, "
    "for example NATIVE_LINTERS: [PYTHON_BLACK, JAVASCRIPT_ES]."
)
EMPTY_MESSAGE = (
    "No linter is enabled for native mode: list the linters to run without Docker in "
    "NATIVE_LINTERS (example: NATIVE_LINTERS: [PYTHON_BLACK, JAVASCRIPT_ES]), "
    "or use NATIVE_LINTERS: [all] if you fully trust every linter matching your configuration."
)


class NativeSelection:
    def __init__(self, selected, not_listed, listed_not_active, wants_all):
        self.selected = selected
        self.not_listed = not_listed
        self.listed_not_active = listed_not_active
        self.wants_all = wants_all


def configured_native_linters(request_id):
    return [
        str(item).strip()
        for item in config.get_list(request_id, "NATIVE_LINTERS", [])
        if str(item).strip() != ""
    ]


def select_native_linters(
    request_id, active_linters, known_linter_keys, configured=None
):
    configured = (
        configured_native_linters(request_id) if configured is None else configured
    )
    wants_all = any(item.lower() == ALL_KEYWORD for item in configured)
    listed = [item for item in configured if item.lower() != ALL_KEYWORD]
    unknown = sorted(set(listed) - set(known_linter_keys))
    if unknown:
        raise NativeError("Unknown linter(s) in NATIVE_LINTERS: " + ", ".join(unknown))
    if wants_all:
        logging.warning(ALL_WARNING)
        return NativeSelection(list(active_linters), [], [], True)
    active_by_key = {linter.name: linter for linter in active_linters}
    selected = [active_by_key[key] for key in listed if key in active_by_key]
    listed_not_active = [key for key in listed if key not in active_by_key]
    not_listed = [linter for linter in active_linters if linter.name not in listed]
    return NativeSelection(selected, not_listed, listed_not_active, False)
