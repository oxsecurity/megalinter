# !/usr/bin/env python3
"""
Generate architecture diagram of MegaLinter
See how to do it at https://kroki.io/#how
"""
import base64
import tempfile
import zlib
from string import Template

# pylint: disable=import-error
import requests


class BuildArchDiagram:
    GATEWAY_SERVER = "https://kroki.io"
    DIAGRAM_TEMPLATE = "docs/assets/archi.blockdiag.txt"

    def __init__(
        self,
        descriptor_language_count,
        descriptor_format_count,
        descriptor_tooling_format_count,
    ):
        self.diagram_dict = dict(
            language=str(descriptor_language_count),
            format=str(descriptor_format_count),
            tooling_format=str(descriptor_tooling_format_count),
        )

        self.build_diagram()

    # Generate binary image following specified format
    def get_image_bin(self, format="svg", tempfile="kroki"):
        image_content = self.run_query(
            self.GATEWAY_SERVER, "blockdiag", format, self.encoded_diagram
        )

        output_file = f"{tempfile}.{format}"
        with open(output_file, "wb") as file:
            file.write(image_content)

        return output_file

    # Get diagram textual description
    def get_image_text(self):
        return self.asset

    # Get generated image from gateway (default: kroki.io server)"
    def run_query(self, gateway, diagram_type, diagram_format, encoded_diagram):
        request = requests.get(
            f"{gateway}/{diagram_type}/{diagram_format}/{encoded_diagram}"
        )
        if request.status_code == 200:
            return request.content
        else:
            raise Exception(
                f"Query failed to run by returning code of {request.status_code}"
            )

    # Build diagram textual description and return deflate + base64 encoded version
    def build_diagram(self):
        with open(self.DIAGRAM_TEMPLATE, "r") as file:
            diagram_source = file.read().rstrip()

        self.asset = Template(diagram_source).safe_substitute(self.diagram_dict)

        try:
            temp = tempfile.NamedTemporaryFile(prefix="MegaLinter_")
            temp.write(self.asset.encode())
            temp.seek(0)
            encoded_diagram = base64.urlsafe_b64encode(zlib.compress(temp.read(), 9))
            self.encoded_diagram = encoded_diagram.decode()
        finally:
            temp.close()
