#!/usr/bin/env python3
# Tick checkboxes in the Renovate "Dependency Dashboard" GitHub issue.
#
# Renovate watches its dashboard issue body: a ticked checkbox is an instruction
# (create a rate-limited PR, rebase an open PR, run again now...). This script
# finds the dashboard issue, ticks the checkboxes of the requested sections and
# pushes the new body back with `gh issue edit`.
#
# Usage:
#   python tick_dashboard.py                       # rate-limited + open, aggregate checkboxes
#   python tick_dashboard.py --dry-run             # show what would be ticked, change nothing
#   python tick_dashboard.py --individual          # tick every PR line instead of the "all" box
#   python tick_dashboard.py --sections open       # only one section
#   python tick_dashboard.py --branches renovate/a,renovate/b   # rebase only these PRs
#   python tick_dashboard.py --trigger-run         # also tick "run Renovate again now"
#   python tick_dashboard.py --issue 3630 --repo oxsecurity/megalinter

import argparse
import io
import json
import os
import re
import subprocess
import sys
import tempfile

# Renovate labels checkboxes with emoji; the Windows console defaults to cp1252
# and would crash printing them.
for _stream in (sys.stdout, sys.stderr):
    if isinstance(_stream, io.TextIOWrapper):
        _stream.reconfigure(encoding="utf-8", errors="replace")

DASHBOARD_TITLE_DEFAULT = "Dependency Dashboard"
RENOVATE_AUTHORS = ("app/renovate", "renovate[bot]", "renovate-bot")

# Section name (normalized) -> aggregate checkbox marker Renovate puts at its end
AGGREGATE_MARKERS = {
    "rate-limited": "create-all-rate-limited-prs",
    "open": "rebase-all-open-prs",
    "pending approval": "approve-all-pending-prs",
}

# Accepted aliases -> canonical section key
SECTION_ALIASES = {
    "rate-limited": "rate-limited",
    "rate limited": "rate-limited",
    "ratelimited": "rate-limited",
    "open": "open",
    "pending approval": "pending approval",
    "awaiting schedule": "awaiting schedule",
    "pending status checks": "pending status checks",
    "pr edited (blocked)": "pr edited (blocked)",
    "pr closed (blocked)": "pr closed (blocked)",
}

UNCHECKED = re.compile(r"^(\s*[-*]\s+)\[ \](.*)$")
CHECKED = re.compile(r"^(\s*[-*]\s+)\[x\](.*)$", re.IGNORECASE)
HEADER = re.compile(r"^#{1,6}\s+(.*?)\s*$")
REBASE_BRANCH = re.compile(r"<!--\s*rebase-branch=(\S+?)\s*-->")
MANUAL_JOB = "<!-- manual job -->"


def run_gh(args, repo=None):
    cmd = ["gh"] + args
    if repo:
        cmd += ["--repo", repo]
    proc = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    if proc.returncode != 0:
        sys.exit(f"ERROR: `{' '.join(cmd)}` failed:\n{proc.stderr.strip()}")
    return proc.stdout


def find_dashboard_issue(repo, title):
    raw = run_gh(
        [
            "issue",
            "list",
            "--state",
            "open",
            "--search",
            f'"{title}" in:title',
            "--json",
            "number,title,author",
            "--limit",
            "50",
        ],
        repo,
    )
    issues = json.loads(raw)
    exact = [i for i in issues if i["title"].strip() == title]
    candidates = exact or issues
    bot = [
        i
        for i in candidates
        if i.get("author", {}).get("login", "") in RENOVATE_AUTHORS
        or i.get("author", {}).get("is_bot")
    ]
    pool = bot or candidates
    if not pool:
        sys.exit(
            f"ERROR: no open issue titled '{title}' found. "
            "If renovate.json sets `dependencyDashboardTitle`, pass --title, "
            "or pass --issue <number>."
        )
    if len(pool) > 1:
        listing = ", ".join(f"#{i['number']} {i['title']}" for i in pool)
        sys.exit(f"ERROR: several dashboard candidates ({listing}) - pass --issue.")
    return pool[0]["number"]


def normalize(name):
    key = name.strip().lower()
    return SECTION_ALIASES.get(key, key)


def split_sections(lines):
    # -> list of (canonical_name, start_index, end_index_exclusive); preamble is ""
    bounds = []
    current = ("", 0)
    for idx, line in enumerate(lines):
        match = HEADER.match(line)
        if match:
            bounds.append((current[0], current[1], idx))
            current = (normalize(match.group(1)), idx)
    bounds.append((current[0], current[1], len(lines)))
    return bounds


def tick(lines, start, end, individual, section, branches=None):
    """Tick checkboxes in lines[start:end]. Returns list of ticked labels."""
    marker = AGGREGATE_MARKERS.get(section)
    aggregate_idx = None
    if marker and not individual and branches is None:
        for idx in range(start, end):
            if marker in lines[idx] and UNCHECKED.match(lines[idx]):
                aggregate_idx = idx
                break
    if aggregate_idx is not None:
        targets = [aggregate_idx]
    else:
        targets = [
            idx
            for idx in range(start, end)
            if UNCHECKED.match(lines[idx])
            and (branches is None or branch_of(lines[idx]) in branches)
        ]
    ticked = []
    for idx in targets:
        match = UNCHECKED.match(lines[idx])
        lines[idx] = f"{match.group(1)}[x]{match.group(2)}"
        ticked.append(label_of(lines[idx]))
    return ticked


def branch_of(line):
    match = REBASE_BRANCH.search(line)
    return match.group(1) if match else None


def label_of(line):
    text = re.sub(r"<!--.*?-->", "", line).strip().lstrip("-* ").strip()
    text = re.sub(r"^\[[ xX]\]\s*", "", text)
    return text or line.strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo", default=None, help="owner/name (default: current repo)"
    )
    parser.add_argument(
        "--issue", type=int, default=None, help="dashboard issue number"
    )
    parser.add_argument("--title", default=DASHBOARD_TITLE_DEFAULT)
    parser.add_argument(
        "--sections",
        default=None,
        help="comma-separated section names to tick "
        "(default: rate-limited,open; just open with --branches)",
    )
    parser.add_argument(
        "--branches",
        default=None,
        help="comma-separated renovate branches: tick only their lines (one by one, "
        "never the 'all at once' box), only in the sections requested",
    )
    parser.add_argument(
        "--individual",
        action="store_true",
        help="tick every PR checkbox instead of the section's 'all at once' box",
    )
    parser.add_argument(
        "--trigger-run",
        action="store_true",
        help="also tick the 'run Renovate again on this repository' checkbox",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    branches = None
    if args.branches is not None:
        branches = {b.strip() for b in args.branches.split(",") if b.strip()}
        # An empty filter must never fall back to ticking everything
        if not branches:
            sys.exit("ERROR: --branches is empty - nothing to rebase.")
    sections_arg = args.sections or (
        "open" if branches is not None else "rate-limited,open"
    )
    wanted = [normalize(s) for s in sections_arg.split(",") if s.strip()]
    issue = args.issue or find_dashboard_issue(args.repo, args.title)

    body = run_gh(
        ["issue", "view", str(issue), "--json", "body", "-q", ".body"], args.repo
    )
    lines = body.splitlines()
    sections = split_sections(lines)
    present = {name for name, _, _ in sections if name}

    report = {}
    listed = set()
    for name in wanted:
        matches = [(s, e) for n, s, e in sections if n == name]
        if not matches:
            report[name] = None  # section absent
            continue
        ticked = []
        for start, end in matches:
            listed.update(branch_of(lines[idx]) for idx in range(start, end))
            ticked += tick(lines, start, end, args.individual, name, branches)
        report[name] = ticked
    missing = sorted(branches - listed) if branches is not None else []

    manual = []
    if args.trigger_run:
        for idx, line in enumerate(lines):
            if MANUAL_JOB in line:
                match = UNCHECKED.match(line)
                if match:
                    lines[idx] = f"{match.group(1)}[x]{match.group(2)}"
                    manual.append(label_of(lines[idx]))
                break

    print(f"Dashboard issue: #{issue}")
    print(f"Sections present: {', '.join(sorted(s for s in present)) or '(none)'}")
    for name in wanted:
        ticked = report[name]
        if ticked is None:
            print(f"  {name}: SECTION ABSENT - nothing to do")
        elif not ticked:
            print(f"  {name}: no unticked checkbox (already ticked, or empty)")
        else:
            print(f"  {name}: ticked {len(ticked)}")
            for label in ticked:
                print(f"    - {label}")
    if args.trigger_run:
        print(f"  manual run: {'ticked' if manual else 'no unticked checkbox found'}")

    if missing:
        print(
            f"  NOT LISTED in {', '.join(wanted)} - will NOT be rebased "
            f"(edited/blocked by Renovate, closed, or unknown): {', '.join(missing)}"
        )

    total = sum(len(v) for v in report.values() if v) + len(manual)
    if total == 0:
        print("\nNothing changed - no request sent to Renovate.")
    elif args.dry_run:
        print(f"\nDRY RUN - would tick {total} checkbox(es); issue not modified.")
    else:
        fd, path = tempfile.mkstemp(suffix=".md", text=True)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write("\n".join(lines) + "\n")
            run_gh(["issue", "edit", str(issue), "--body-file", path], args.repo)
        finally:
            os.unlink(path)
        print(
            f"\nTicked {total} checkbox(es) on issue #{issue}. Renovate will act on its next run."
        )
    # Requested branches left out must be noticed by the caller
    if missing:
        sys.exit(2)


if __name__ == "__main__":
    main()
