# !/usr/bin/env python3
"""
Automatically generate source code
"""
# pylint: disable=import-error
import logging
import os
import sys

import megalinter
import terminaltables

REPO_HOME = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + ".."


def list_references_to_megalinter():
    linters = megalinter.linter_factory.list_all_linters()
    table_header = ["Descriptor", "Linter", "Status", "URL"]
    table_data = [table_header]
    for linter in linters:
        status = "Not submitted"
        url = ""
        if hasattr(linter, "linter_megalinter_ref_url"):
            url = linter.linter_megalinter_ref_url
            if linter.linter_megalinter_ref_url == "no":
                status = "Rejected"
                url = "-------------"
            elif linter.linter_megalinter_ref_url == "never":
                status = "Not applicable"
                url = "-------------"
            elif "/pull/" in str(url):
                status = "Pending"
                url = "PR: " + url
            else:
                status = "Published"
        table_line = [
            linter.descriptor_id,
            linter.linter_name,
            status,
            url,
        ]
        table_data += [table_line]
    # Display results
    table = terminaltables.AsciiTable(table_data)
    table.title = "----Reference to Mega-Linter in linters documentation summary"
    # Output table in console
    logging.info("")
    for table_line in table.table.splitlines():
        logging.info(table_line)
    logging.info("")
    # Write in file
    with open(REPO_HOME + "/docs/references.md", "w", encoding="utf-8") as outfile:
        outfile.write("<!-- markdownlint-disable -->\n\n")
        outfile.write("# References\n\n")
        for table_line in table.table.splitlines():
            if table_line.startswith("+"):
                if table_line.startswith("+--------"):
                    outfile.write("| :--- | :---- | :----: | :---- |\n")
            else:
                outfile.write("%s\n" % table_line)


if __name__ == "__main__":
    logging.basicConfig(
        force=True,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    list_references_to_megalinter()
