"""
Custom flavor generation utilities for MegaLinter
"""

import logging
import os
import yaml
from megalinter import linter_factory
from megalinter.constants import (
    DEFAULT_DOCKERFILE_FLAVOR_ARGS,
    DEFAULT_DOCKERFILE_FLAVOR_CARGO_PACKAGES,
)


def generate_custom_flavor_dockerfile(custom_flavor_file):
    """Generate Dockerfile-custom-flavor from megalinter-custom-flavor.yml"""
    if not os.path.exists(custom_flavor_file):
        logging.error(f"Custom flavor file not found: {custom_flavor_file}")
        return False
    
    try:
        # Load custom flavor configuration
        with open(custom_flavor_file, "r", encoding="utf-8") as f:
            custom_flavor_config = yaml.safe_load(f)
        
        # Validate required fields
        required_fields = ["flavor_name", "flavor_description", "linters", "docker_image"]
        for field in required_fields:
            if field not in custom_flavor_config:
                logging.error(f"Missing required field '{field}' in custom flavor configuration")
                return False
        
        # Get base linter data
        descriptor_and_linters = []
        descriptor_files = linter_factory.list_descriptor_files()
        
        # Map custom flavor linters to their descriptors
        linter_keys_to_include = set(custom_flavor_config["linters"])
        
        for descriptor_file in descriptor_files:
            with open(descriptor_file, "r", encoding="utf-8") as f:
                descriptor = yaml.safe_load(f)
            
            if "linters" in descriptor:
                for linter in descriptor["linters"]:
                    linter_key = f"{descriptor['descriptor_id']}_{linter['linter_name']}"
                    if linter_key in linter_keys_to_include:
                        # Add descriptor-level install if not already added
                        descriptor_copy = descriptor.copy()
                        descriptor_copy["linter_name"] = linter["linter_name"]
                        # Merge linter-specific install with descriptor install
                        if "install" in linter:
                            if "install" not in descriptor_copy:
                                descriptor_copy["install"] = {}
                            for install_type, packages in linter["install"].items():
                                if install_type not in descriptor_copy["install"]:
                                    descriptor_copy["install"][install_type] = []
                                descriptor_copy["install"][install_type].extend(packages)
                        descriptor_and_linters.append(descriptor_copy)
        
        # Add additional dependencies from custom flavor config
        if "additional_dependencies" in custom_flavor_config:
            additional_deps = custom_flavor_config["additional_dependencies"]
            custom_descriptor = {
                "descriptor_id": "CUSTOM_FLAVOR",
                "linter_name": "custom_dependencies",
                "install": additional_deps
            }
            descriptor_and_linters.append(custom_descriptor)
        
        # Generate Dockerfile
        dockerfile_path = os.path.join(os.path.dirname(custom_flavor_file), "Dockerfile-custom-flavor")
        
        # Extra lines for custom flavor
        extra_lines = [
            "COPY entrypoint.sh /entrypoint.sh",
            "RUN chmod +x entrypoint.sh",
            'ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]',
        ]
        
        # Add custom dockerfile commands if specified
        if "custom_dockerfile_commands" in custom_flavor_config:
            extra_lines.extend(custom_flavor_config["custom_dockerfile_commands"])
        
        # Add default environment variables
        if "environment_variables" in custom_flavor_config:
            for env_var, env_value in custom_flavor_config["environment_variables"].items():
                extra_lines.append(f'ENV {env_var}="{env_value}"')
        
        # Import build_dockerfile here to avoid circular imports
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '.automation'))
        from build import build_dockerfile
        
        build_dockerfile(
            dockerfile_path,
            descriptor_and_linters,
            False,  # requires_docker
            custom_flavor_config["flavor_name"],
            extra_lines,
            DEFAULT_DOCKERFILE_FLAVOR_ARGS.copy(),
            {"cargo": DEFAULT_DOCKERFILE_FLAVOR_CARGO_PACKAGES.copy()},
        )
        
        logging.info(f"Generated custom flavor Dockerfile: {dockerfile_path}")
        return True
        
    except Exception as e:
        logging.error(f"Error generating custom flavor Dockerfile: {str(e)}")
        return False
