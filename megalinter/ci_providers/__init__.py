#!/usr/bin/env python3
from megalinter.ci_providers.CiProvider import CiProvider
from megalinter.ci_providers.CiProviderAzurePipelines import CiProviderAzurePipelines
from megalinter.ci_providers.CiProviderBitbucket import CiProviderBitbucket
from megalinter.ci_providers.CiProviderGithubActions import CiProviderGithubActions
from megalinter.ci_providers.CiProviderGitlab import CiProviderGitlab
from megalinter.ci_providers.CiProviderJenkins import (
    CiProviderJenkins,
    apply_jenkins_ci_vars,
)

# Order matters: the first provider recognizing the environment wins. Jenkins
# comes last because it maps its own variables onto the other platforms, so a
# real GitHub/GitLab/Azure/Bitbucket build must be recognized first
PROVIDER_CLASSES = [
    CiProviderAzurePipelines,
    CiProviderGithubActions,
    CiProviderGitlab,
    CiProviderBitbucket,
    CiProviderJenkins,
]


# Returns the provider of the platform running the current build. When the
# platform is not auto-detected, the neutral base provider is returned so
# callers never have to handle a missing provider
def get_ci_provider(request_id, workspace=None):
    for provider_class in PROVIDER_CLASSES:
        if provider_class.is_current():
            return provider_class(request_id, workspace)
    return CiProvider(request_id, workspace)


# Returns the provider matching the current Pull Request context, falling back
# to the neutral base provider the same way as get_ci_provider
def get_pr_ci_provider(request_id, workspace=None):
    for provider_class in PROVIDER_CLASSES:
        if provider_class.is_pr_context():
            return provider_class(request_id, workspace)
    return CiProvider(request_id, workspace)


__all__ = [
    "CiProvider",
    "CiProviderAzurePipelines",
    "CiProviderBitbucket",
    "CiProviderGithubActions",
    "CiProviderGitlab",
    "CiProviderJenkins",
    "PROVIDER_CLASSES",
    "apply_jenkins_ci_vars",
    "get_ci_provider",
    "get_pr_ci_provider",
]
