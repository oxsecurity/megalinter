#!/usr/bin/env python3
"""
Use golang-ci to lint golang files
"""
from itertools import groupby
from pathlib import Path

from megalinter import Linter, utils


class GolangCILinter(Linter):

    # Build the CLI command to call to lint a file
    def build_lint_command(self, file=None):    
        cmd = []
        # Find all go.mod files and run golangci-lint at the parent directory if possible
        files = utils.filter_files(all_files=self.files, file_names_regex=".*/go.mod")
        if len(files) > 0:
            for file in files: 
                path = Path(file)
                if len(cmd) > 0:
                    cmd.append("&&")
                cmd.extend["cd", path.parent, "&&", "golangci-lint", "run"]
        else:
            # If no go.mod files are found, group all go files by their parent directory and lint against them
            files = utils.filter_files(all_files=self.files, file_extensions=[".go"])
            for group in groupby(files, lambda x: x.rpartition("/")): 
                if len(cmd) > 0:
                    cmd.append("&&")
                cmd.extend["golangci-lint", "run", " ".join(group)]
        
        return cmd