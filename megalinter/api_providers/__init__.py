#!/usr/bin/env python3
from megalinter.api_providers.ApiProvider import ApiProvider
from megalinter.api_providers.ApiProviderDatadog import ApiProviderDatadog
from megalinter.api_providers.ApiProviderElastic import ApiProviderElastic
from megalinter.api_providers.ApiProviderGrafana import ApiProviderGrafana
from megalinter.api_providers.ApiProviderNewRelic import ApiProviderNewRelic

# "auto" and "http" are aliases of the Grafana / generic HTTP provider
PROVIDER_CLASSES = {
    "auto": ApiProviderGrafana,
    "http": ApiProviderGrafana,
    "grafana": ApiProviderGrafana,
    "datadog": ApiProviderDatadog,
    "elastic": ApiProviderElastic,
    "newrelic": ApiProviderNewRelic,
}

__all__ = [
    "ApiProvider",
    "ApiProviderDatadog",
    "ApiProviderElastic",
    "ApiProviderGrafana",
    "ApiProviderNewRelic",
    "PROVIDER_CLASSES",
]
