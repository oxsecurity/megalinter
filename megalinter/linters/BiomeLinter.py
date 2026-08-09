import json
import logging
import os

from megalinter import Linter, utils


class BiomeLinter(Linter):
    # Biome has no CLI exclusion argument: generate a config extending the
    # workspace one, overriding files.includes with negated patterns
    def manage_excluded_directories_config(self, cmd):
        user_config_file = self.final_config_file
        if user_config_file is None:
            for config_file_name in ["biome.json", "biome.jsonc"]:
                candidate = os.path.join(self.workspace, config_file_name)
                if os.path.isfile(candidate):
                    user_config_file = candidate
                    break
        # A child files.includes replaces the parent one: re-emit user entries first
        includes = ["**"]
        if user_config_file is not None:
            user_includes = (
                self.read_biome_config(user_config_file)
                .get("files", {})
                .get("includes")
            )
            if isinstance(user_includes, list) and len(user_includes) > 0:
                includes = [str(value) for value in user_includes]
        includes += [
            "!**/" + excl_dir.replace(os.sep, "/") + "/**"
            for excl_dir in self.get_project_exclude_directories()
        ]
        generated_config = {"files": {"includes": includes}}
        if user_config_file is not None:
            extends_path = os.path.relpath(user_config_file, self.report_folder)
            generated_config = {
                "extends": [extends_path.replace(os.sep, "/")],
                **generated_config,
            }
        generated_file = self.write_report_generated_file(
            "biome-generated-config.json", [json.dumps(generated_config, indent=2)]
        )
        value_index = self.find_cli_argument_value_index(cmd, ["--config-path"])
        cmd = self.replace_or_append_cli_argument(
            cmd, value_index, "--config-path", generated_file
        )
        self.log_project_exclude_forwarding(
            f"Generated {generated_file} extending the workspace Biome configuration "
            f"to forward EXCLUDED_DIRECTORIES in project lint mode "
            f"(disable with {self.name}_FORWARD_EXCLUDED_DIRECTORIES: false)"
        )
        return cmd

    def read_biome_config(self, config_file):
        with open(config_file, encoding="utf-8") as file_handler:
            content = file_handler.read()
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        try:
            return json.loads(utils.strip_jsonc(content))
        except json.JSONDecodeError:
            logging.warning(
                f"[BiomeLinter] Unable to parse {config_file}: "
                "its files.includes entries will not be preserved in the generated "
                "configuration forwarding EXCLUDED_DIRECTORIES"
            )
            return {}
