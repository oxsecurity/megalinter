from megalinter.constants import ML_DOC_URL

REMOVED_LINTERS_DOC_URL = f"{ML_DOC_URL}/removed-linters/"

# Linters removed from MegaLinter, keyed by the linter name they used to have.
# Their configuration variables are kept in the JSON schema (flagged as
# deprecated) and their keys stay valid in ENABLE_LINTERS / DISABLE_LINTERS, so
# existing .mega-linter.yml files keep validating after an upgrade.
REMOVED_LINTERS = {
    "CREDENTIALS_SECRETLINT": {
        "removed_in": "6.0.0",
        "replacement": "REPOSITORY_SECRETLINT",
        "reason": "The CREDENTIALS descriptor has been merged into the REPOSITORY descriptor",
    },
    "DOCKERFILE_DOCKERFILELINT": {
        "removed_in": "6.0.0",
        "replacement": "DOCKERFILE_HADOLINT",
        "reason": "Upstream is no longer maintained, and hadolint already covers all of its rules",
    },
    "GIT_GIT_DIFF": {
        "removed_in": "6.0.0",
        "replacement": "REPOSITORY_GIT_DIFF",
        "reason": "The GIT descriptor has been merged into the REPOSITORY descriptor",
    },
    "PHP_BUILTIN": {
        "removed_in": "6.0.0",
        "replacement": "PHP_PHPLINT",
        "reason": "The built-in `php -l` syntax check has been superseded by"
        " phplint, which runs the same check in parallel",
    },
    "KUBERNETES_KUBEVAL": {
        "removed_in": "7.0.0",
        "replacement": "KUBERNETES_KUBECONFORM",
        "reason": "No longer maintained, and its authors recommend kubeconform instead",
    },
    "REPOSITORY_GOODCHECK": {
        "removed_in": "7.0.0",
        "replacement": None,
        "reason": "Upstream is not open-source anymore",
    },
    "SPELL_MISSPELL": {
        "removed_in": "7.0.0",
        "replacement": None,
        "reason": "No longer maintained (no commit since 2018)",
    },
    "TERRAFORM_CHECKOV": {
        "removed_in": "7.0.0",
        "replacement": "REPOSITORY_CHECKOV",
        "reason": "Moved to the REPOSITORY descriptor so it can analyze all file types, not only Terraform",
    },
    "TERRAFORM_KICS": {
        "removed_in": "7.0.0",
        "replacement": "REPOSITORY_CHECKOV",
        "reason": "Moved to the REPOSITORY descriptor as REPOSITORY_KICS, which has since been removed too",
    },
    "CSS_SCSS_LINT": {
        "removed_in": "8.0.0",
        "replacement": "CSS_STYLELINT",
        "reason": "Project discontinued, with its authors advising to use stylelint instead",
    },
    "OPENAPI_SPECTRAL": {
        "removed_in": "8.0.0",
        "replacement": "API_SPECTRAL",
        "reason": "Replaced by API_SPECTRAL, which runs the same linter on both OpenAPI and AsyncAPI files",
    },
    "SQL_SQL_LINT": {
        "removed_in": "8.0.0",
        "replacement": "SQL_SQLFLUFF",
        "reason": "No longer maintained (joereynolds/sql-lint#262)",
    },
    "MARKDOWN_MARKDOWN_LINK_CHECK": {
        "removed_in": "9.0.0",
        "replacement": "SPELL_LYCHEE",
        "reason": "lychee can be used instead and has much better performances",
    },
    "JSON_ESLINT_PLUGIN_JSONC": {
        "removed_in": "10.0.0",
        "replacement": "JSON_PRETTIER",
        "reason": "Long-standing upstream bug in eslint-plugin-jsonc (ota-meshi/eslint-plugin-jsonc#328)",
    },
    "LUA_SELENE": {
        "removed_in": "10.0.0",
        "replacement": "LUA_LUACHECK",
        "reason": "Disabled since an unresolved upstream bug (Kampfkarren/selene#662)",
    },
    "MAKEFILE_CHECKMAKE": {
        "removed_in": "10.0.0",
        "replacement": None,
        "reason": "Disabled for security issues (checkmake/checkmake#99), and"
        " the MAKEFILE descriptor had no other linter",
    },
    "MARKDOWN_REMARK_LINT": {
        "removed_in": "10.0.0",
        "replacement": "MARKDOWN_MARKDOWNLINT",
        "reason": "Disabled since an unresolved upstream bug (remarkjs/remark-lint#322)",
    },
    "PUPPET_PUPPET_LINT": {
        "removed_in": "10.0.0",
        "replacement": None,
        "reason": "Disabled since an unresolved upstream bug"
        " (puppetlabs/puppet-lint#251), and the PUPPET descriptor had no other"
        " linter",
    },
    "REPOSITORY_GITLEAKS": {
        "removed_in": "10.0.0",
        "replacement": "REPOSITORY_BETTERLEAKS",
        "reason": "Superseded by betterleaks, created by the same author, which"
        " reads existing .gitleaks.toml and .gitleaksignore files unchanged",
    },
    "REPOSITORY_KICS": {
        "removed_in": "10.0.0",
        "replacement": "REPOSITORY_CHECKOV",
        "reason": "Disabled after the Checkmarx supply chain compromise",
    },
    "SALESFORCE_LIGHTNING_FLOW_SCANNER": {
        "removed_in": "10.0.0",
        "replacement": "SALESFORCE_CODE_ANALYZER_FLOW",
        "reason": "Upstream repository archived",
    },
    "SALESFORCE_SFDX_SCANNER_APEX": {
        "removed_in": "10.0.0",
        "replacement": "SALESFORCE_CODE_ANALYZER_APEX",
        "reason": "sfdx-scanner has been deprecated by Salesforce and is incompatible with Node.js 22+",
    },
    "SALESFORCE_SFDX_SCANNER_AURA": {
        "removed_in": "10.0.0",
        "replacement": "SALESFORCE_CODE_ANALYZER_AURA",
        "reason": "sfdx-scanner has been deprecated by Salesforce and is incompatible with Node.js 22+",
    },
    "SALESFORCE_SFDX_SCANNER_LWC": {
        "removed_in": "10.0.0",
        "replacement": "SALESFORCE_CODE_ANALYZER_LWC",
        "reason": "sfdx-scanner has been deprecated by Salesforce and is incompatible with Node.js 22+",
    },
    "SQL_TSQLLINT": {
        "removed_in": "10.0.0",
        "replacement": None,
        "reason": "Upstream unmaintained since 2024-09 and shipping unpatched"
        " .NET CVEs with no prospect of a fixed release",
    },
    "TERRAFORM_TERRASCAN": {
        "removed_in": "10.0.0",
        "replacement": "REPOSITORY_CHECKOV",
        "reason": "Upstream repository archived by Tenable and shipping"
        " unpatched CVEs with no prospect of a fixed release",
    },
}

# Linter keys that were never shipped under that exact name but have been valid
# in ENABLE_LINTERS / DISABLE_LINTERS at some point. Kept in the JSON schema
# enum only, so configurations using them keep validating.
REMOVED_LINTER_ALIASES = [
    "CSS_SCSSLINT",  # typo for CSS_SCSS_LINT, in the schema enum since v8
]

# Descriptors removed from MegaLinter. Their keys stay valid in ENABLE / DISABLE.
REMOVED_DESCRIPTORS = {
    "CREDENTIALS": {
        "removed_in": "6.0.0",
        "replacement": "REPOSITORY",
        "reason": "Merged into the REPOSITORY descriptor",
    },
    "GIT": {
        "removed_in": "6.0.0",
        "replacement": "REPOSITORY",
        "reason": "Merged into the REPOSITORY descriptor",
    },
    "OPENAPI": {
        "removed_in": "8.0.0",
        "replacement": "API",
        "reason": "Superseded by the API descriptor",
    },
    "MAKEFILE": {
        "removed_in": "10.0.0",
        "replacement": None,
        "reason": "Its only linter, MAKEFILE_CHECKMAKE, has been removed",
    },
    "PUPPET": {
        "removed_in": "10.0.0",
        "replacement": None,
        "reason": "Its only linter, PUPPET_PUPPET_LINT, has been removed",
    },
}


def _match_prefix(property_name: str, removed_keys) -> str | None:
    # Longest key first so SALESFORCE_SFDX_SCANNER_APEX wins over a shorter prefix
    for removed_key in sorted(removed_keys, key=len, reverse=True):
        if property_name == removed_key or property_name.startswith(removed_key + "_"):
            return removed_key
    return None


def is_removed_related_variable(property_name: str) -> bool:
    return (
        _match_prefix(property_name, REMOVED_LINTERS) is not None
        or _match_prefix(property_name, REMOVED_DESCRIPTORS) is not None
    )


def find_removed_references(config_keys, linter_names, descriptor_names) -> list[str]:
    found = {name for name in linter_names if name in REMOVED_LINTERS}
    found |= {name for name in descriptor_names if name in REMOVED_DESCRIPTORS}
    for config_key in config_keys:
        matched = _match_prefix(config_key, REMOVED_LINTERS) or _match_prefix(
            config_key, REMOVED_DESCRIPTORS
        )
        if matched is not None:
            found.add(matched)
    return sorted(found)
