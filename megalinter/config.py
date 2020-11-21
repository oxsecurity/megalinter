#!/usr/bin/env python3
import os

# Initialize runtime config
RUNTIME_CONFIG = os.environ.copy()


def get(config_var=None, default=None):
    if config_var is None:
        return RUNTIME_CONFIG
    return RUNTIME_CONFIG.get(config_var, default)


def set_value(config_var, val):
    RUNTIME_CONFIG[config_var] = val


def exists(config_var):
    return config_var in RUNTIME_CONFIG


def copy():
    return RUNTIME_CONFIG.copy()


def delete(key):
    del RUNTIME_CONFIG[key]
