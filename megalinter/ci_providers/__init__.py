#!/usr/bin/env python3
from megalinter.ci_providers.CiProvider import CiProvider
from megalinter.ci_providers.CiProviderAzurePipelines import (
    CiProviderAzurePipelines,
)
from megalinter.ci_providers.CiProviderGithubActions import (
    CiProviderGithubActions,
)
from megalinter.ci_providers.CiProviderGitlab import CiProviderGitlab

# Order matters: the first provider recognizing the environment wins
PROVIDER_CLASSES = [
    CiProviderAzurePipelines,
    CiProviderGithubActions,
    CiProviderGitlab,
]


# Returns the provider matching the current Pull Request context. When the
# platform is not auto-detected, the neutral base provider is returned so
# callers never have to handle a missing provider
def get_pr_ci_provider(request_id, workspace):
    for provider_class in PROVIDER_CLASSES:
        if provider_class.is_pr_context():
            return provider_class(request_id, workspace)
    return CiProvider(request_id, workspace)


__all__ = [
    "CiProvider",
    "CiProviderAzurePipelines",
    "CiProviderGithubActions",
    "CiProviderGitlab",
    "PROVIDER_CLASSES",
    "get_pr_ci_provider",
]
