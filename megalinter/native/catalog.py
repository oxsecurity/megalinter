import glob
import os

import yaml

from megalinter.linter_factory import resolve_linter_extends
from megalinter.native.resolve import NativeLinterSpec
from megalinter.utils import get_descriptor_dir


def load_native_specs(descriptor_dir=None, only=None):
    descriptor_dir = descriptor_dir or get_descriptor_dir()
    specs = []
    for descriptor_file in sorted(
        glob.glob(os.path.join(descriptor_dir, "*.megalinter-descriptor.yml"))
    ):
        with open(descriptor_file, "r", encoding="utf-8") as f:
            descriptor = yaml.safe_load(f)
        descriptor_id = descriptor["descriptor_id"]
        for linter in descriptor.get("linters", []):
            spec = NativeLinterSpec(
                descriptor_id,
                descriptor.get("install"),
                resolve_linter_extends(linter),
                descriptor_file,
            )
            if only and descriptor_id not in only and spec.key not in only:
                continue
            specs.append(spec)
    return specs
