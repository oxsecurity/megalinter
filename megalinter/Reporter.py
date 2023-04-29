#!/usr/bin/env python3
"""
Template class for custom reporters: any linter class in /reporters folder must inherit from this class
"""


from typing import Optional

from megalinter.Linter import Linter


class Reporter:
    # Report definition
    name: Optional[str] = None
    report_folder: Optional[str] = None
    scope: Optional[str] = None  # Can be megalinter or linter

    # Constructor: Initialize Linter instance with name and config variables
    def __init__(self, params=None):
        self.processing_order = 0
        self.master: Linter = params["master"]
        self.report_folder = params["report_folder"]
        # Any reporter is inactive by default except if __init__ is overridden on sub class
        if not hasattr(self, "is_active"):
            self.is_active = False
        self.report_items = []
        self.manage_activation()

    # Method produce_report can be overridden at custom report class
    def manage_activation(self):
        pass

    # Method produce_report can be overridden at custom report class
    def initialize(self, **kwargs):
        pass

    # Method produce_report can be overridden at custom report class
    def add_report_item(self, **kwargs):
        pass

    # Method produce_report can be overridden at custom report class
    def produce_report(self):
        pass
