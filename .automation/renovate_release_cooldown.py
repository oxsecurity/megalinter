#!/usr/bin/env python3
# Blocking release cooldown for the Renovate updates that Renovate can not date itself.
#
# renovate.json5 holds an update back until the release is `minimumReleaseAge` old. Renovate
# only knows the release date for some datasources: images hosted outside Docker Hub (ghcr.io,
# quay.io, mcr.microsoft.com...) and the git-refs / git-tags datasources have none, so Renovate
# either never proposes them (minimumReleaseAgeBehaviour: timestamp-required) or proposes them
# immediately (timestamp-optional). This check dates these releases itself and fails the pull
# request until the release is `minimumReleaseAge` old:
#   - images: the GitHub release of the source repository (ghcr.io/<owner>/<repo>) and the
#     creation date recorded in the image itself
#   - git-refs: the date of the pinned commit
#   - git-tags: the GitHub release, else the date of the tagged commit
# When several dates are found, the most recent one counts.
#
# Like Renovate's own `vulnerabilityAlerts`, security updates ("[SECURITY]" in the title) are
# not delayed. The `skip-release-cooldown` label lets a maintainer accept an update anyway.
#
#   check --pr <number>   evaluate one pull request, exit code 1 while it must wait
#   recheck               re-run the failed checks of open Renovate pull requests that now pass
import argparse
import datetime
import json
import logging
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

GITHUB_API = "https://api.github.com"
WORKFLOW_FILE = "renovate-release-cooldown.yml"
RENOVATE_LOGIN = "renovate[bot]"
OVERRIDE_LABEL = "skip-release-cooldown"
SECURITY_TITLE_MARKER = "[SECURITY]"
USER_AGENT = "megalinter-renovate-release-cooldown"
REPO_ROOT = Path(__file__).resolve().parent.parent
UNTIMESTAMPED_DATASOURCES = ("git-refs", "git-tags")
DOCKER_HUB_REGISTRIES = ("docker.io", "index.docker.io", "registry-1.docker.io")
# Reproducible image builds record a fixed epoch (1970-01-01) as creation date
MIN_PLAUSIBLE_YEAR = 2000
MANIFEST_ACCEPT = ", ".join(
    [
        "application/vnd.oci.image.index.v1+json",
        "application/vnd.docker.distribution.manifest.list.v2+json",
        "application/vnd.oci.image.manifest.v1+json",
        "application/vnd.docker.distribution.manifest.v2+json",
    ]
)

# Same comment syntax as the customManagers of renovate.json5
RENOVATE_COMMENT_RE = re.compile(
    r"(?:#|//)\s*renovate:\s*datasource=(?P<datasource>[a-z0-9.-]+)\s+depName=(?P<dep_name>\S+)(?P<rest>.*)"
)
PACKAGE_NAME_RE = re.compile(r"\b(?:packageName|lookupName)=(?P<value>\S+)")
VERSION_VALUE_RES = [
    re.compile(r"_VERSION\s*[=:]\s*[\"']?(?P<value>[^\"'\s,]+)"),
    re.compile(r"\bversion:\s*[\"']?(?P<value>[^\"'\s,]+)"),
    re.compile(r"==\s*(?P<value>[^\"'\s,;]+)"),
]
GIT_DIGEST_RE = re.compile(r"@(?P<value>[0-9a-f]{40})\b")
# FROM / COPY --from= lines read by Renovate's own dockerfile manager (no renovate comment)
IMAGE_REFERENCE_RE = re.compile(
    r"^\s*(?:-\s*)?(?:FROM\s+(?:--platform=\S+\s+)?|COPY\b.*?--from=)"
    r"(?P<image>[a-z0-9-]+(?:\.[a-z0-9-]+)+(?::\d+)?/[a-z0-9._/-]+):(?P<tag>[A-Za-z0-9._-]+)(?=[\s@]|$)"
)
# Lock files carry no renovate pin: GitHub omits their (large) diff without consequence
LOCK_FILE_RE = re.compile(r"(?:\.lock|-lock\.json|-lock\.ya?ml)$")
GITHUB_URL_RE = re.compile(
    r"^(?:https?://|git@)github\.com[/:](?P<repo>[^/]+/[^/]+?)(?:\.git)?/?$"
)

logger = logging.getLogger("renovate-release-cooldown")


@dataclass(frozen=True)
class Update:
    datasource: str
    package: str
    version: str

    def label(self) -> str:
        return f"{self.package} {self.version or '(version not found)'}"


@dataclass
class UpdateResult:
    update: Update
    released_at: datetime.datetime | None
    source: str
    eligible_at: datetime.datetime | None
    ready: bool


@dataclass
class Evaluation:
    blocked: bool
    reason: str
    results: list[UpdateResult]


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


NO_REDIRECT_OPENER = urllib.request.build_opener(NoRedirect)


class GitHub:
    def __init__(self, token: str, repository: str):
        self.token = token
        self.repository = repository

    def request(self, method: str, path: str) -> Any:
        url = path if path.startswith("https://") else f"{GITHUB_API}{path}"
        request = urllib.request.Request(
            url,
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "User-Agent": USER_AGENT,
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read()
        except urllib.error.HTTPError as error:
            # 404: unknown release / repository, 422: unknown commit or ref
            if error.code in (404, 422):
                return None
            raise
        return json.loads(body) if body else {}

    def get(self, path: str) -> Any:
        return self.request("GET", path)

    def get_paginated(self, path: str) -> list:
        items: list = []
        separator = "&" if "?" in path else "?"
        page = 1
        while True:
            batch = self.get(f"{path}{separator}per_page=100&page={page}") or []
            items.extend(batch)
            if len(batch) < 100:
                return items
            page += 1


class Registry:
    def __init__(self, registry: str, repository: str):
        self.base_url = f"https://{registry}/v2/{repository}"
        self.token: str | None = None

    def get_json(self, path: str, accept: str) -> dict | None:
        for _attempt in range(2):
            headers = {"Accept": accept, "User-Agent": USER_AGENT}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            url = f"{self.base_url}{path}"
            try:
                with NO_REDIRECT_OPENER.open(
                    urllib.request.Request(url, headers=headers), timeout=30
                ) as response:
                    return json.load(response)
            except urllib.error.HTTPError as error:
                if error.code == 401 and self.token is None:
                    self.token = fetch_registry_token(
                        error.headers.get("WWW-Authenticate", "")
                    )
                    if self.token:
                        continue
                if error.code in (301, 302, 303, 307, 308):
                    # Blobs are served from a signed storage URL: follow it without the token
                    location = urllib.parse.urljoin(url, error.headers["Location"])
                    with urllib.request.urlopen(
                        urllib.request.Request(
                            location, headers={"User-Agent": USER_AGENT}
                        ),
                        timeout=30,
                    ) as response:
                        return json.load(response)
                return None
        return None


def fetch_registry_token(challenge: str) -> str | None:
    if not challenge.lower().startswith("bearer "):
        return None
    params = dict(re.findall(r'(\w+)="([^"]*)"', challenge))
    realm = params.pop("realm", None)
    if not realm:
        return None
    url = f"{realm}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(
        urllib.request.Request(url, headers={"User-Agent": USER_AGENT}), timeout=30
    ) as response:
        data = json.load(response)
    return data.get("token") or data.get("access_token")


def parse_date(value: str | None) -> datetime.datetime | None:
    if not value:
        return None
    # Registries record nanoseconds, fromisoformat accepts microseconds
    normalized = re.sub(r"(\.\d{6})\d+", r"\1", value.strip()).replace("Z", "+00:00")
    try:
        date = datetime.datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if date.tzinfo is None:
        date = date.replace(tzinfo=datetime.timezone.utc)
    if date.year < MIN_PLAUSIBLE_YEAR:
        return None
    return date


def image_registry(image: str) -> str | None:
    first, separator, _rest = image.partition("/")
    if not separator:
        return None
    if ("." in first or ":" in first or first == "localhost") and (
        first not in DOCKER_HUB_REGISTRIES
    ):
        return first
    return None


def is_untimestamped(datasource: str, package: str) -> bool:
    if datasource in UNTIMESTAMPED_DATASOURCES:
        return True
    return datasource == "docker" and image_registry(package) is not None


def update_from_comment(comment: re.Match, line: str) -> Update | None:
    datasource = comment["datasource"]
    package_match = PACKAGE_NAME_RE.search(comment["rest"])
    package = package_match["value"] if package_match else comment["dep_name"]
    if not is_untimestamped(datasource, package):
        return None
    version = ""
    if datasource == "git-refs":
        digest = GIT_DIGEST_RE.search(line)
        version = digest["value"] if digest else ""
    else:
        for regex in VERSION_VALUE_RES:
            value = regex.search(line)
            if value:
                version = value["value"]
                break
    if not version:
        logger.warning(
            f"::warning::Could not read the version of {package} in: {line.strip()}"
        )
    return Update(datasource, package, version)


def find_untimestamped_updates(files: list[dict]) -> list[Update]:
    updates: list[Update] = []
    for file in files:
        patch = file.get("patch")
        if patch is None:
            if file.get("status") != "removed" and not LOCK_FILE_RE.search(
                file.get("filename", "")
            ):
                logger.warning(
                    f"::warning::No diff available for {file.get('filename')} (too large): its updates are not checked"
                )
            continue
        pending_comment = None
        for line in patch.splitlines():
            if line.startswith("@@"):
                pending_comment = None
                continue
            # Removed lines and "\ No newline at end of file" markers
            if not line or line[0] not in "+ ":
                continue
            content = line[1:]
            comment = RENOVATE_COMMENT_RE.search(content)
            if comment:
                pending_comment = comment
                continue
            if line[0] == "+":
                if pending_comment is not None:
                    update = update_from_comment(pending_comment, content)
                    if update is not None:
                        updates.append(update)
                image = IMAGE_REFERENCE_RE.search(content)
                if (
                    image
                    and image["tag"] != "latest"
                    and is_untimestamped("docker", image["image"])
                ):
                    updates.append(Update("docker", image["image"], image["tag"]))
            if content.strip():
                pending_comment = None
    return list(dict.fromkeys(updates))


def tag_candidates(version: str) -> list[str]:
    candidates = [version]
    base = re.match(r"v?\d+(?:\.\d+)*", version)
    if base:
        candidates.append(base[0])
    with_prefix = [c if c.startswith("v") else f"v{c}" for c in candidates]
    return list(dict.fromkeys(candidates + with_prefix))


def github_repository(url: str) -> str | None:
    match = GITHUB_URL_RE.match(url)
    return match["repo"] if match else None


def commit_date(github: GitHub, repository: str, ref: str) -> datetime.datetime | None:
    commit = github.get(
        f"/repos/{repository}/commits/{urllib.parse.quote(ref, safe='')}"
    )
    if not commit:
        return None
    return parse_date(commit["commit"]["committer"]["date"])


def github_release_date(
    github: GitHub, repository: str, version: str
) -> datetime.datetime | None:
    candidates = tag_candidates(version)
    for tag in candidates:
        release = github.get(
            f"/repos/{repository}/releases/tags/{urllib.parse.quote(tag, safe='')}"
        )
        if release and release.get("published_at"):
            return parse_date(release["published_at"])
    for tag in candidates:
        date = commit_date(github, repository, tag)
        if date:
            return date
    return None


def image_created_date(image: str, version: str) -> datetime.datetime | None:
    registry, _separator, repository = image.partition("/")
    client = Registry(registry, repository)
    tags = [version] if version.startswith("v") else [version, f"v{version}"]
    try:
        for tag in tags:
            manifest = client.get_json(
                f"/manifests/{urllib.parse.quote(tag)}", MANIFEST_ACCEPT
            )
            if manifest is None:
                continue
            date = manifest_annotation_date(manifest)
            if date:
                return date
            if "manifests" in manifest:
                entries = manifest["manifests"]
                chosen = next(
                    (
                        entry
                        for entry in entries
                        if entry.get("platform", {}).get("os") == "linux"
                        and entry.get("platform", {}).get("architecture") == "amd64"
                    ),
                    entries[0] if entries else None,
                )
                if chosen is None:
                    continue
                date = manifest_annotation_date(chosen)
                if date:
                    return date
                manifest = client.get_json(
                    f"/manifests/{chosen['digest']}", MANIFEST_ACCEPT
                )
                if manifest is None:
                    continue
                date = manifest_annotation_date(manifest)
                if date:
                    return date
            config_digest = manifest.get("config", {}).get("digest")
            if not config_digest:
                continue
            config = client.get_json(f"/blobs/{config_digest}", "application/json, */*")
            date = parse_date(config.get("created")) if config else None
            if date:
                return date
    except (urllib.error.URLError, TimeoutError, ValueError, KeyError) as error:
        logger.info(
            f"Could not read the creation date of {image}:{version} from its registry: {error}"
        )
    return None


def manifest_annotation_date(manifest: dict) -> datetime.datetime | None:
    return parse_date(
        manifest.get("annotations", {}).get("org.opencontainers.image.created")
    )


def release_date(
    github: GitHub, update: Update
) -> tuple[datetime.datetime | None, str]:
    if not update.version:
        return None, ""
    dates: dict[str, datetime.datetime | None] = {}
    if update.datasource == "git-refs":
        repository = github_repository(update.package)
        if repository:
            dates[f"commit {update.version[:12]}"] = commit_date(
                github, repository, update.version
            )
    elif update.datasource == "git-tags":
        repository = github_repository(update.package)
        if repository:
            dates["GitHub release"] = github_release_date(
                github, repository, update.version
            )
    else:
        if update.package.startswith("ghcr.io/"):
            repository = "/".join(update.package.split("/")[1:3])
            dates["GitHub release"] = github_release_date(
                github, repository, update.version
            )
        dates["image creation"] = image_created_date(update.package, update.version)
    found = {source: date for source, date in dates.items() if date}
    if not found:
        return None, ""
    source = max(found, key=lambda key: found[key])
    return found[source], source


def read_cooldown() -> datetime.timedelta:
    text = (REPO_ROOT / "renovate.json5").read_text(encoding="utf-8")
    match = re.search(
        r"^  minimumReleaseAge:\s*['\"](?P<days>\d+)\s*days?['\"]", text, re.MULTILINE
    )
    if not match:
        raise SystemExit(
            "::error::Top-level minimumReleaseAge ('<N> days') not found in renovate.json5"
        )
    return datetime.timedelta(days=int(match["days"]))


def evaluate(
    github: GitHub,
    pull_request: dict,
    cooldown: datetime.timedelta,
    now: datetime.datetime,
) -> Evaluation:
    labels = [label["name"] for label in pull_request.get("labels", [])]
    if OVERRIDE_LABEL in labels:
        return Evaluation(
            False, f"label `{OVERRIDE_LABEL}`: cooldown skipped by a maintainer", []
        )
    if SECURITY_TITLE_MARKER in pull_request["title"]:
        return Evaluation(
            False,
            "security update: not delayed, like Renovate vulnerability alerts",
            [],
        )
    files = github.get_paginated(
        f"/repos/{github.repository}/pulls/{pull_request['number']}/files"
    )
    updates = find_untimestamped_updates(files)
    if not updates:
        return Evaluation(
            False,
            "no update without release date (Renovate applies the cooldown itself)",
            [],
        )
    results: list[UpdateResult] = []
    for update in updates:
        released_at, source = release_date(github, update)
        eligible_at = released_at + cooldown if released_at else None
        ready = eligible_at is not None and now >= eligible_at
        results.append(UpdateResult(update, released_at, source, eligible_at, ready))
    blocked = not all(result.ready for result in results)
    reason = (
        f"releases must be {cooldown.days} days old"
        if blocked
        else f"every release is at least {cooldown.days} days old"
    )
    return Evaluation(blocked, reason, results)


def format_date(date: datetime.datetime | None) -> str:
    return date.strftime("%Y-%m-%d %H:%M UTC") if date else "unknown"


def report(evaluation: Evaluation, cooldown: datetime.timedelta) -> None:
    status = "⏳ Waiting" if evaluation.blocked else "✅ Ready"
    lines = [f"## Renovate release cooldown: {status}", "", evaluation.reason, ""]
    if evaluation.results:
        lines += [
            "| Update | Released | Source | Eligible from | Status |",
            "|---|---|---|---|---|",
        ]
        for result in evaluation.results:
            lines.append(
                f"| `{result.update.label()}` | {format_date(result.released_at)} | {result.source or '-'} "
                f"| {format_date(result.eligible_at)} | {'✅' if result.ready else '⏳'} |"
            )
        lines.append("")
    for result in evaluation.results:
        if result.ready:
            logger.info(
                f"{result.update.label()}: released {format_date(result.released_at)} ({result.source}), OK"
            )
        elif result.released_at is None:
            logger.info(
                f"::error title=Release cooldown::{result.update.label()}: release date not found. "
                f"Check it was published at least {cooldown.days} days ago, then add the `{OVERRIDE_LABEL}` label"
            )
        else:
            logger.info(
                f"::error title=Release cooldown::{result.update.label()}: released {format_date(result.released_at)} "
                f"({result.source}), can be merged from {format_date(result.eligible_at)}. "
                "This check is re-run daily"
            )
    logger.info(evaluation.reason)
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_file:
        with open(summary_file, "a", encoding="utf-8") as summary:
            summary.write("\n".join(lines) + "\n")


def command_check(github: GitHub, pr_number: int) -> int:
    cooldown = read_cooldown()
    pull_request = github.get(f"/repos/{github.repository}/pulls/{pr_number}")
    if pull_request is None:
        raise SystemExit(f"::error::Pull request #{pr_number} not found")
    evaluation = evaluate(
        github, pull_request, cooldown, datetime.datetime.now(datetime.timezone.utc)
    )
    report(evaluation, cooldown)
    return 1 if evaluation.blocked else 0


def command_recheck(github: GitHub) -> int:
    cooldown = read_cooldown()
    now = datetime.datetime.now(datetime.timezone.utc)
    pull_requests = github.get_paginated(f"/repos/{github.repository}/pulls?state=open")
    for pull_request in pull_requests:
        if pull_request["user"]["login"] != RENOVATE_LOGIN:
            continue
        number = pull_request["number"]
        head_sha = pull_request["head"]["sha"]
        runs = github.get(
            f"/repos/{github.repository}/actions/workflows/{WORKFLOW_FILE}/runs"
            f"?head_sha={head_sha}&event=pull_request&per_page=1"
        )
        latest = (runs or {}).get("workflow_runs", [])
        if (
            not latest
            or latest[0]["status"] != "completed"
            or latest[0]["conclusion"] != "failure"
        ):
            continue
        evaluation = evaluate(github, pull_request, cooldown, now)
        if evaluation.blocked:
            logger.info(f"#{number}: still waiting ({evaluation.reason})")
            continue
        github.request(
            "POST",
            f"/repos/{github.repository}/actions/runs/{latest[0]['id']}/rerun-failed-jobs",
        )
        logger.info(f"#{number}: cooldown over, check re-run ({latest[0]['html_url']})")
    return 0


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)
    parser = argparse.ArgumentParser(
        description="Release cooldown for Renovate updates without release date"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    check_parser = subparsers.add_parser("check", help="Evaluate one pull request")
    check_parser.add_argument("--pr", type=int, required=True)
    subparsers.add_parser(
        "recheck", help="Re-run the failed checks whose cooldown is over"
    )
    args = parser.parse_args()
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    repository = os.environ.get("GITHUB_REPOSITORY", "oxsecurity/megalinter")
    if not token:
        raise SystemExit("GH_TOKEN or GITHUB_TOKEN is required")
    github = GitHub(token, repository)
    if args.command == "check":
        return command_check(github, args.pr)
    return command_recheck(github)


if __name__ == "__main__":
    sys.exit(main())
