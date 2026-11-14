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
LOG_PREFIX = re.compile(r"^[^\t]*\t[^\t]*\t\d{4}-\d\d-\d\dT[\d:.]+Z ?")
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
    r"(?P<keep>CVE-\d{4}-\d{4,}|GHSA(?:-[a-z0-9]{4}){3})"
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
        after = body[body.index(ERROR_DETAIL) + 1 :]
        for line in after:
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


def is_related(fingerprint, title, branch, files):
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
        "pending": any(c["bucket"] == "pending" for c in checks),
        "fingerprints": [],
        "other_failures": [],
    }
    for check in checks:
        if check["bucket"] not in ("fail", "cancel"):
            continue
        job = JOB_LINK.search(check["link"])
        is_megalinter = re.search(r"mega-?linter", check["name"], re.IGNORECASE)
        sections = []
        reason = "not a MegaLinter check" if not is_megalinter else "cancelled"
        if job and check["bucket"] == "fail" and is_megalinter:
            log = run_gh(
                ["run", "view", job.group(1), "--job", job.group(2), "--log-failed"],
                repo,
                required=False,
            )
            sections = blocking_sections(clean_log_lines(log))
            reason = (
                "log unavailable" if not log.strip() else "no blocking linter in log"
            )
        for section in sections:
            result["fingerprints"].append(
                section_fingerprint(check["name"], section, check["link"])
            )
        if not sections:
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


SELFTEST_LOG = "\n".join(
    [
        "MegaLinter\tMegaLinter\t2026-11-14T17:44:18.4095554Z ##[endgroup]",
        "MegaLinter\tMegaLinter\t2026-11-14T17:44:18.4095956Z ##[group][31m❌ Linted [SPELL] files with [cspell]: Found 4 error(s) and 0 warning(s) - (10.99s)[0m (expand for details)",
        "MegaLinter\tMegaLinter\t2026-11-14T17:44:18.4096112Z - Using [cspell v10.4.0] https://megalinter.io/x",
        "MegaLinter\tMegaLinter\t2026-11-14T17:44:18.4096200Z - MegaLinter key: [SPELL_CSPELL]",
        "MegaLinter\tMegaLinter\t2026-11-14T17:44:18.4097217Z --Error detail:",
        "MegaLinter\tMegaLinter\t2026-11-14T17:44:18.4097468Z /tmp/lint/megalinter/Jira.py:218:21    - Unknown word (noformat)",
        "MegaLinter\tMegaLinter\t2026-11-14T17:44:18.4097500Z ##[endgroup]",
        "MegaLinter\tMegaLinter\t2026-11-14T17:44:19.0000000Z ##[group][32m✅ Linted [YAML] files with [yamllint] successfully - (1s)[0m",
        "MegaLinter\tMegaLinter\t2026-11-14T17:44:19.0000001Z - MegaLinter key: [YAML_YAMLLINT]",
    ]
)


def selftest():
    sections = blocking_sections(clean_log_lines(SELFTEST_LOG))
    assert len(sections) == 1, sections
    first = section_fingerprint("MegaLinter", sections[0], "url")
    assert first["linter_key"] == "SPELL_CSPELL", first
    assert first["line"] == "megalinter/Jira.py:<n> - Unknown word (noformat)", first

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
