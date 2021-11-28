# !/usr/bin/env python3
"""
Build architecture diagram of MegaLinter
"""

from build_arch_diagram import BuildArchDiagram

diag = BuildArchDiagram(29, 11, 13)
print(diag.get_image_text())
print(diag.get_image_file("svg", "docs/assets/images/architecture"))
