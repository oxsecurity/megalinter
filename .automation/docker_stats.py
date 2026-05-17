#!/usr/bin/env python3
"""
Collect Docker image download counts from all registries and update flavors-stats.json.

Sources:
  - ghcr.io  : GitHub GraphQL API (requires GITHUB_TOKEN), fallback to HTML scraping
  - Docker Hub: public REST API (legacy images that migrated from Docker Hub)

Usage:
    python .automation/docker_stats.py
"""

import json
import logging
import os
import re
import sys
from datetime import date, datetime

import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import megalinter.flavor_factory  # noqa: E402
from megalinter.constants import (  # noqa: E402
    DOCKER_PACKAGES_ROOT_URL,
    ML_DOCKER_IMAGE,
    ML_DOCKER_IMAGE_LEGACY,
    ML_DOCKER_IMAGE_LEGACY_V5,
    ML_DOCKER_NAME,
    ML_DOCKER_OWNER,
    ML_REPO_NAME,
    ML_REPO_OWNER,
)

REPO_HOME = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + ".."
DOCKER_STATS_FILE = REPO_HOME + "/.automation/generated/flavors-stats.json"

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"
GITHUB_PACKAGES_HTML_URL = (
    f"https://github.com/{ML_REPO_OWNER}/{ML_REPO_NAME}/pkgs/container"
)

# Honour PYTHONHTTPSVERIFY=0 for corporate proxies that do SSL inspection.
# requests does not read this flag on its own (only urllib does).
_SSL_VERIFY: bool = os.environ.get("PYTHONHTTPSVERIFY", "1") != "0"
if not _SSL_VERIFY:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------


def _retry_session() -> requests.Session:
    session = requests.Session()
    session.verify = _SSL_VERIFY
    retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def number_human_format(num, round_to=1):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num = round(num / 1000.0, round_to)
    return "{:.{}f}{}".format(
        round(num, round_to), round_to, ["", "k", "M", "G", "T", "P"][magnitude]
    )


def keep_one_stat_by_day(flavor_stats):
    filtered = []
    prev_date = date.min
    for [count_date_iso, count] in flavor_stats:
        count_date = datetime.fromisoformat(count_date_iso).date()
        if count_date == prev_date:
            filtered.pop()
        filtered.append([count_date_iso, count])
        prev_date = count_date
    return filtered


# ---------------------------------------------------------------------------
# ghcr.io download counts
# ---------------------------------------------------------------------------


def fetch_ghcr_download_count(package_name: str) -> int:
    count = _fetch_via_graphql(package_name)
    if count:
        return count
    return _fetch_via_scraping(package_name)


def _fetch_via_graphql(package_name: str) -> int:
    github_token = os.environ.get("GITHUB_TOKEN", "")
    if not github_token:
        return 0
    query = """
query($org: String!, $name: String!) {
  organization(login: $org) {
    packages(packageType: CONTAINER, names: [$name], first: 1) {
      nodes {
        statistics { downloadsTotalCount }
      }
    }
  }
}
"""
    try:
        resp = _retry_session().post(
            GITHUB_GRAPHQL_URL,
            json={
                "query": query,
                "variables": {"org": ML_DOCKER_OWNER, "name": package_name},
            },
            headers={
                "Authorization": f"Bearer {github_token}",
                "Content-Type": "application/json",
            },
            timeout=30,
        )
        data = resp.json()
        if "errors" in data:
            logging.debug(f"GraphQL errors for {package_name}: {data['errors']}")
            return 0
        nodes = (
            data.get("data", {})
            .get("organization", {})
            .get("packages", {})
            .get("nodes", [])
        )
        if nodes:
            count = nodes[0].get("statistics", {}).get("downloadsTotalCount", 0)
            if count:
                logging.info(f"GHCR GraphQL {package_name}: {count:,}")
            return count
    except Exception as e:
        logging.warning(f"GraphQL request failed for {package_name}: {e}")
    return 0


def _fetch_via_scraping(package_name: str) -> int:
    url = f"{GITHUB_PACKAGES_HTML_URL}/{package_name}"
    try:
        resp = _retry_session().get(url, headers={"Accept": "text/html"}, timeout=30)
        resp.raise_for_status()
        # HTML contains:  Total downloads</span>
        #                   <h3 title="1234567">1.2M</h3>
        match = re.search(
            r'Total downloads</span>\s*<h3[^>]*title="([\d,]+)"',
            resp.text,
        )
        if match:
            count = int(match.group(1).replace(",", ""))
            logging.info(f"GHCR scrape  {package_name}: {count:,}")
            return count
        logging.warning(f"Download count not found in HTML for {package_name} ({url})")
    except Exception as e:
        logging.warning(f"Scraping failed for {package_name}: {e}")
    return 0


# ---------------------------------------------------------------------------
# Docker Hub download counts (legacy images)
# ---------------------------------------------------------------------------


def _fetch_dockerhub_download_count(image_url: str) -> int:
    try:
        resp = _retry_session().get(image_url, timeout=30)
        data = resp.json()
        count = data.get("pull_count", 0)
        logging.info(f"Docker Hub {image_url}: {count}")
        return count
    except Exception as e:
        logging.warning(f"Docker Hub request failed for {image_url}: {e}")
        return 0


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------


def update_docker_pulls_counter():
    logging.info("Fetching docker pull counters on flavors images")
    total_count = 0
    all_flavors_ids = list(megalinter.flavor_factory.get_all_flavors().keys())
    all_flavors_ids.insert(0, "all")

    with open(DOCKER_STATS_FILE, "r", encoding="utf-8") as f:
        docker_stats = json.load(f)

    now_str = datetime.now().replace(microsecond=0).isoformat()

    for flavor_id in all_flavors_ids:
        if flavor_id == "all":
            package_name = ML_DOCKER_NAME
            dockerhub_url = f"{DOCKER_PACKAGES_ROOT_URL}/{ML_DOCKER_IMAGE}"
            legacy_url = f"{DOCKER_PACKAGES_ROOT_URL}/{ML_DOCKER_IMAGE_LEGACY}"
            legacy_v5_url = f"{DOCKER_PACKAGES_ROOT_URL}/{ML_DOCKER_IMAGE_LEGACY_V5}"
        else:
            package_name = f"{ML_DOCKER_NAME}-{flavor_id}"
            dockerhub_url = f"{DOCKER_PACKAGES_ROOT_URL}/{ML_DOCKER_IMAGE}-{flavor_id}"
            legacy_url = (
                f"{DOCKER_PACKAGES_ROOT_URL}/{ML_DOCKER_IMAGE_LEGACY}-{flavor_id}"
            )
            legacy_v5_url = (
                f"{DOCKER_PACKAGES_ROOT_URL}/{ML_DOCKER_IMAGE_LEGACY_V5}-{flavor_id}"
            )

        ghcr_count = fetch_ghcr_download_count(package_name)
        dockerhub_count = _fetch_dockerhub_download_count(dockerhub_url)
        legacy_count = _fetch_dockerhub_download_count(legacy_url)
        legacy_v5_count = _fetch_dockerhub_download_count(legacy_v5_url)
        flavor_count = ghcr_count + dockerhub_count + legacy_count + legacy_v5_count

        logging.info(f"- docker pulls for {flavor_id}: {flavor_count}")
        total_count += flavor_count

        flavor_stats = list(docker_stats.get(flavor_id, []))
        flavor_stats.append([now_str, flavor_count])
        docker_stats[flavor_id] = keep_one_stat_by_day(flavor_stats)

    total_count_human = number_human_format(total_count)
    logging.info(f"Total docker pulls: {total_count_human} ({total_count})")

    # Update badge in README files
    badge_pattern = re.compile(r"(?<=pulls-)[^-]+(?=-blue)")
    for readme in [
        f"{REPO_HOME}/README.md",
        f"{REPO_HOME}/mega-linter-runner/README.md",
    ]:
        text = open(readme, encoding="utf-8").read()
        updated = badge_pattern.sub(total_count_human, text)
        if updated != text:
            open(readme, "w", encoding="utf-8").write(updated)

    with open(DOCKER_STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(docker_stats, f, indent=4, sort_keys=True)


# ---------------------------------------------------------------------------
# Standalone execution — print a summary table
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    update_docker_pulls_counter()
