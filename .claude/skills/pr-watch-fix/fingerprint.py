#!/usr/bin/env python3
# Read-only: fingerprint the blocking MegaLinter errors of one or more PRs.
#
# Two PRs failing with the same fingerprint fail for the same reason (same check,
# same linter, same normalized first error line), so the fix only has to be made
# once. Output is JSON on stdout, one object per PR. Nothing is modified.
#
# Usage:
#   python fingerprint.py 9474 9473            # one JSON object per PR
#   python fingerprint.py 9474 --repo owner/name
#   python fingerprint.py --selftest           # check the parser/normalizer, no network

import argparse
import hashlib
import io
import json
import re
import subprocess
import sys

for _stream in (sys.stdout, sys.stderr):
    if isinstance(_stream, io.TextIOWrapper):
        _stream.reconfigure(encoding="utf-8", errors="replace")

MAX_LINE_LENGTH = 300

# GitHub prefixes every log line with "<job>\t<step>\t<timestamp> "
# `gh run view` prefixes lines with "<job>\t<step>\t<timestamp> ", the jobs logs API
# with "<timestamp> " only (and a BOM on the first line)
LOG_PREFIX = re.compile(r"^﻿?(?:[^\t]*\t[^\t]*\t)?\d{4}-\d\d-\d\dT[\d:.]+Z ?")
# A MegaLinter lint job ("MegaLinter", "MegaLinter for x"), not "mega-linter-runner tests"
MEGALINTER_CHECK = re.compile(r"mega-?linter(?![-\w])", re.IGNORECASE)
# A security scan job ("Trivy scan - DEV"), fingerprinted by the advisories it reports.
# Whole words only: the "repository_osv_scanner" linter test is not a scan job.
SECURITY_CHECK = re.compile(
    r"\b(?:scan|audit|vulnerabilit(?:y|ies)|security)\b", re.IGNORECASE
)
SECURITY_KEY = "SECURITY_SCAN"
ADVISORY = re.compile(r"CVE-\d{4}-\d{4,}|GHSA(?:-[a-z0-9]{4}){3}")
# A test job ("Run Test Cases - DEV"), fingerprinted by its failing pytest node ids
TEST_CHECK = re.compile(r"\b(?:tests?|pytest)\b", re.IGNORECASE)
TEST_KEY = "TEST_FAILURES"
FAILED_TEST = re.compile(r"^FAILED (\S+)", re.MULTILINE)
# Statuses Renovate sets itself: not CI, they only clear when Renovate runs
RENOVATE_STATUSES = {"renovate/stability-days"}
# The ESC character is dropped by `gh run view`, leaving a bare "[31m"
ANSI = re.compile(r"\x1b?\[\d+(?:;\d+)*m")
LINTED = re.compile(r"❌ Linted \[([^\]]+)\] files with \[([^\]]+)\]")
LINTED_ANY = re.compile(r"Linted \[[^\]]+\] files with \[")
GROUP_END = re.compile(r"##\[endgroup\]|::endgroup::")
ML_KEY = re.compile(r"^- MegaLinter key: \[([^\]]+)\]")
ERROR_DETAIL = "--Error detail:"
ERROR_HINT = re.compile(
    r"error|✗|CVE-|GHSA-|unknown word|\b[A-Z]{1,5}\d{2,5}\b", re.IGNORECASE
)
WORKSPACE_ROOTS = re.compile(
    r"/tmp/lint/|/github/workspace/|/home/runner/work/[^/\s]+/[^/\s]+/"
)
# Alternatives are tried left to right at each position: ids are kept as they are,
# so a CVE number or a GHSA id is never replaced by a placeholder.
TOKEN = re.compile(
    r"(?P<keep>CVE-\d{4}-\d{4,}|GHSA(?:-[a-z0-9]{4}){3}|(?-i:\b[A-Z]{1,5}\d{2,5}\b))"
    r"|(?P<ts>\d{4}-\d\d-\d\d[T ][\d:.]+Z?)"
    r"|(?P<loc>(?<=\w):\d+(?::\d+)?(?!\w))"
    r"|(?P<ver>\bv?\d+\.\d+(?:\.\d+)*(?:[-+][\w.]+)?\b)"
    r"|(?P<sha>\b(?=[0-9a-f]*\d)(?=[0-9a-f]*[a-f])[0-9a-f]{7,64}\b)"
    r"|(?P<num>\d+)",
    re.IGNORECASE,
)
PLACEHOLDERS = {
    "ts": "<ts>",
    "loc": ":<n>",
    "ver": "<ver>",
    "sha": "<sha>",
    "num": "<n>",
}
BUMP = re.compile(r"`([^`\n]*\d[^`\n]*)`\s*(?:->|→)\s*`([^`\n]*\d[^`\n]*)`")
# Digest and pin updates (`3a1b2c4` -> `9f8e7d6`) are not versions: skipped
VERSION = re.compile(r"^[v=^~]*(\d+(?:\.\d+)*)$")
JOB_LINK = re.compile(r"/runs/(\d+)/job/(\d+)")


def run_gh(args, repo=None, required=True):
    cmd = ["gh"] + args
    if repo:
        cmd += ["--repo", repo]
    proc = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    # `gh pr checks` exits 8 while checks are pending but still prints the JSON
    if proc.returncode not in (0, 8):
        if required:
            sys.exit(f"ERROR: `{' '.join(cmd)}` failed:\n{proc.stderr.strip()}")
        return ""
    return proc.stdout


def normalize(line):
    line = ANSI.sub("", line)
    line = WORKSPACE_ROOTS.sub("", line)
    line = re.sub(r"\s+", " ", line).strip().removeprefix("./")

    def replace(match):
        if match.lastgroup == "keep":
            return match.group(0)
        return PLACEHOLDERS[match.lastgroup]

    return TOKEN.sub(replace, line)[:MAX_LINE_LENGTH]


def fingerprint_id(check, linter_key, line):
    return hashlib.sha1(f"{check}|{linter_key}|{line}".encode()).hexdigest()[:10]


def clean_log_lines(text):
    return [ANSI.sub("", LOG_PREFIX.sub("", raw)).rstrip() for raw in text.splitlines()]


def blocking_sections(lines):
    sections = []
    current = None
    for line in lines:
        header = LINTED.search(line)
        if header:
            current = {"descriptor": header.group(1), "linter": header.group(2)}
            current["body"] = []
            sections.append(current)
            continue
        if current is not None and (LINTED_ANY.search(line) or GROUP_END.search(line)):
            current = None
            continue
        if current is not None:
            current["body"].append(line)
    return sections


def first_error_line(body):
    if ERROR_DETAIL in body:
        start = body.index(ERROR_DETAIL) + 1
        for line in body[start:]:
            if line.strip():
                return line
    candidates = [ln for ln in body if ln.strip() and not ln.startswith("- ")]
    for line in candidates:
        if ERROR_HINT.search(line):
            return line
    return candidates[0] if candidates else ""


def section_fingerprint(check, section, run_url):
    linter_key = ""
    for line in section["body"]:
        key = ML_KEY.match(line)
        if key:
            linter_key = key.group(1)
            break
    if not linter_key:
        name = section["linter"].upper().replace("-", "_")
        linter_key = f"{section['descriptor']}_{name}"
    raw = first_error_line(section["body"])
    line = normalize(raw)
    return {
        "id": fingerprint_id(check, linter_key, line),
        "check": check,
        "linter_key": linter_key,
        "linter": section["linter"],
        "line": line,
        "raw": ANSI.sub("", raw).strip()[:MAX_LINE_LENGTH],
        "run_url": run_url,
    }


def update_type(body):
    best = "unknown"
    rank = {"unknown": 0, "patch": 1, "minor": 2, "major": 3}
    for old, new in BUMP.findall(body or ""):
        old_v = VERSION.match(old.strip())
        new_v = VERSION.match(new.strip())
        if not old_v or not new_v:
            continue
        old_parts = old_v.group(1).split(".")
        new_parts = new_v.group(1).split(".")
        found = "patch"
        if old_parts[:1] != new_parts[:1]:
            found = "major"
        elif old_parts[:2] != new_parts[:2]:
            found = "minor"
        if rank[found] > rank[best]:
            best = found
    return best


def job_log(job_id, repo):
    # `gh run view --log-failed` returns nothing for many runs, while the jobs
    # logs API still serves the full log
    path = f"repos/{repo or '{owner}/{repo}'}/actions/jobs/{job_id}/logs"
    return run_gh(["api", path], required=False)


def set_fingerprint(check, key, ids, run_url):
    # The same job failing on the same set of ids is the same failure, whatever
    # the order or the number of times each id is printed
    ids = sorted(set(ids))
    if not ids:
        return []
    line = " ".join(ids)[:MAX_LINE_LENGTH]
    return [
        {
            "id": fingerprint_id(check, key, line),
            "check": check,
            "linter_key": key,
            "linter": "",
            "line": line,
            "raw": line,
            "run_url": run_url,
        }
    ]


def security_fingerprint(check, log, run_url):
    return set_fingerprint(check, SECURITY_KEY, ADVISORY.findall(log), run_url)


def test_fingerprint(check, log, run_url):
    failed = FAILED_TEST.findall("\n".join(clean_log_lines(log)))
    return set_fingerprint(check, TEST_KEY, failed, run_url)


def is_related(fingerprint, title, branch, files):
    if not fingerprint["linter"]:
        return False
    name = fingerprint["linter"].lower()
    variants = {name, name.replace("-", "_"), name.replace("-", "")}
    haystack = f"{title} {branch}".lower()
    paths = [f.lower() for f in files]
    return any(v in haystack for v in variants) or any(
        v in path for v in variants for path in paths
    )


def fingerprint_pr(number, repo):
    pr = json.loads(
        run_gh(
            [
                "pr",
                "view",
                str(number),
                "--json",
                "headRefOid,title,headRefName,body,files,state",
            ],
            repo,
        )
    )
    # A PR without any check ("no checks reported") makes `gh pr checks` fail
    checks = json.loads(
        run_gh(
            ["pr", "checks", str(number), "--json", "name,bucket,link"],
            repo,
            required=False,
        )
        or "[]"
    )
    files = [f["path"] for f in pr.get("files", [])]
    result = {
        "pr": number,
        "state": pr["state"],
        "head_sha": pr["headRefOid"],
        "title": pr["title"],
        "branch": pr["headRefName"],
        "update_type": update_type(pr.get("body")),
        "changed_files": len(files),
        "checks": len(checks),
        "pending": any(
            c["bucket"] == "pending" and c["name"] not in RENOVATE_STATUSES
            for c in checks
        ),
        "waiting_renovate": any(
            c["bucket"] == "pending" and c["name"] in RENOVATE_STATUSES for c in checks
        ),
        "fingerprints": [],
        "other_failures": [],
    }
    for check in checks:
        if check["bucket"] not in ("fail", "cancel"):
            continue
        job = JOB_LINK.search(check["link"])
        failed_job = job if check["bucket"] == "fail" else None
        found = []
        reason = "cancelled"
        if failed_job and MEGALINTER_CHECK.match(check["name"]):
            log = job_log(failed_job.group(2), repo)
            found = [
                section_fingerprint(check["name"], section, check["link"])
                for section in blocking_sections(clean_log_lines(log))
            ]
            reason = "log unavailable" if not log.strip() else "no blocking linter"
        elif failed_job and SECURITY_CHECK.search(check["name"]):
            log = job_log(failed_job.group(2), repo)
            found = security_fingerprint(check["name"], log, check["link"])
            reason = "log unavailable" if not log.strip() else "no CVE/GHSA id in log"
        elif failed_job and TEST_CHECK.search(check["name"]):
            log = job_log(failed_job.group(2), repo)
            found = test_fingerprint(check["name"], log, check["link"])
            reason = "log unavailable" if not log.strip() else "no FAILED test in log"
        elif failed_job:
            reason = "not a MegaLinter, security scan or test check"
        result["fingerprints"] += found
        if not found:
            result["other_failures"].append(
                {
                    "check": check["name"],
                    "bucket": check["bucket"],
                    "link": check["link"],
                    "reason": reason,
                }
            )
    for fingerprint in result["fingerprints"]:
        fingerprint["related"] = is_related(
            fingerprint, pr["title"], pr["headRefName"], files
        )
    return result


SELFTEST_PREFIX = "MegaLinter\tMegaLinter\t2026-11-14T17:44:18.4095554Z "
SELFTEST_LOG = "\n".join(
    SELFTEST_PREFIX + line
    for line in [
        "##[endgroup]",
        "##[group][31m❌ Linted [SPELL] files with [cspell]: Found 4 error(s)"
        " and 0 warning(s) - (10.99s)[0m (expand for details)",
        "- Using [cspell v10.4.0] https://megalinter.io/x",
        "- MegaLinter key: [SPELL_CSPELL]",
        "--Error detail:",
        "/tmp/lint/megalinter/Jira.py:218:21    - Unknown word (noformat)",
        "##[endgroup]",
        "##[group][32m✅ Linted [YAML] files with [yamllint] successfully - (1s)[0m",
        "- MegaLinter key: [YAML_YAMLLINT]",
    ]
)


def selftest():
    sections = blocking_sections(clean_log_lines(SELFTEST_LOG))
    assert len(sections) == 1, sections
    first = section_fingerprint("MegaLinter", sections[0], "url")
    assert first["linter_key"] == "SPELL_CSPELL", first
    assert first["line"] == "megalinter/Jira.py:<n> - Unknown word (noformat)", first

    # Same log as served by the jobs logs API: BOM, timestamp-only prefix
    api_log = "﻿" + "\n".join(
        line.split("\t", 2)[2] for line in SELFTEST_LOG.splitlines()
    )
    api_sections = blocking_sections(clean_log_lines(api_log))
    assert len(api_sections) == 1, api_sections
    assert section_fingerprint("MegaLinter", api_sections[0], "url") == first

    for name in ("MegaLinter", "MegaLinter for mega-linter-runner", "megalinter"):
        assert MEGALINTER_CHECK.match(name), name
    for name in ("mega-linter-runner tests - DEV", "Trivy scan - DEV"):
        assert not MEGALINTER_CHECK.match(name), name

    assert SECURITY_CHECK.search("Trivy scan - DEV")
    assert not SECURITY_CHECK.search("DEV/Linters (repository_osv_scanner, linux)")
    scan_a = security_fingerprint(
        "Trivy scan - DEV",
        "x CVE-2026-2002 GHSA-p3jp-9v83-76w9 CVE-2026-1001 CVE-2026-2002",
        "u",
    )
    scan_b = security_fingerprint(
        "Trivy scan - DEV", "GHSA-p3jp-9v83-76w9 CVE-2026-1001\nCVE-2026-2002", "v"
    )
    assert scan_a[0]["id"] == scan_b[0]["id"], (scan_a, scan_b)
    assert scan_a[0]["line"] == "CVE-2026-1001 CVE-2026-2002 GHSA-p3jp-9v83-76w9"
    assert security_fingerprint("Trivy scan - DEV", "no advisory", "u") == []

    for name in ("Run Test Cases - DEV", "mega-linter-runner tests - DEV"):
        assert TEST_CHECK.search(name), name
    assert not TEST_CHECK.search("Build Docker Image - DEV")
    stamp = "2026-11-15T01:00:00.0000000Z "
    tests_a = test_fingerprint(
        "Run Test Cases - DEV",
        f"{stamp}FAILED a_test.py::t::test_x - AssertionError: boom\n"
        f"{stamp}FAILED b_test.py::t::test_y\n",
        "u",
    )
    tests_b = test_fingerprint(
        "Run Test Cases - DEV",
        "FAILED b_test.py::t::test_y - ValueError\nFAILED a_test.py::t::test_x\n",
        "v",
    )
    assert tests_a[0]["id"] == tests_b[0]["id"], (tests_a, tests_b)
    assert tests_a[0]["line"] == "a_test.py::t::test_x b_test.py::t::test_y"
    assert test_fingerprint("Run Test Cases - DEV", "all passed", "u") == []

    same = fingerprint_id(
        "C", "K", normalize("a/b.py:12:3 - bad thing v1.2.3 at 2026-11-14T10:00:00Z")
    )
    assert same == fingerprint_id(
        "C", "K", normalize("a/b.py:99:7 - bad thing v2.0.1 at 2027-01-01T01:02:03Z")
    )
    assert normalize("Found CVE-2026-1234 in x 1.2.3") != normalize(
        "Found CVE-2026-9999 in x 1.2.3"
    )
    assert normalize("/github/workspace/a.py deadbeef12") == "a.py <sha>"
    # Rule codes identify the error: E501 and E302 must not collide
    assert normalize("b.py:3:80: E501 line too long (95 > 79)") == (
        "b.py:<n>: E501 line too long (<n> > <n>)"
    )
    assert update_type("| x | `1.2.3` -> `2.0.0` |") == "major"
    assert update_type("| x | `1.2.3` -> `1.3.0` |") == "minor"
    assert update_type("| x | `==1.2.3` -> `==1.2.4` |") == "patch"
    assert update_type("nothing") == "unknown"
    assert update_type("| x | `3a1b2c4` -> `9f8e7d6` |") == "unknown"
    assert update_type("| x | `v4.1.0` -> `a1b2c3d` |") == "unknown"
    digest_a = "sha256:" + "3a1b2c3d" * 8
    digest_b = "sha256:" + "9f8e7d6c" * 8
    assert normalize(f"Error: {digest_a}") == normalize(f"Error: {digest_b}")
    print("selftest OK")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("prs", nargs="*", type=int)
    parser.add_argument("--repo", default=None, help="owner/name (default: current)")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        selftest()
        return
    if not args.prs:
        parser.error("give at least one PR number")
    results = [fingerprint_pr(number, args.repo) for number in args.prs]
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
