#!/usr/bin/env python3
# Helper for the /prepare-release skill.
# Performs the mechanical CHANGELOG transformation for a release:
#   - converts the "Unreleased" block into a dated release entry
#   - prunes empty sections from the release entry
#   - collapses linter-version bumps to one line per linter (chronological
#     first-seen "from" -> last-seen "to"), alphabetically sorted, no date
#   - strips the linter-versions-end marker from the release entry
#   - prepends a fresh empty "Unreleased" block holding the sole marker
#
# PR-number backfill is a JUDGMENT step left to the caller: run `analyze` to
# list the content lines that lack a MegaLinter reference, decide the PR(s) for
# each (via git log / gh), then pass those decisions to `apply` as JSON.
#
# Usage:
#   python prepare_changelog.py analyze [--changelog CHANGELOG.md]
#   python prepare_changelog.py apply --version vX.Y.Z [--date YYYY-MM-DD]
#       [--prs prs.json] [--changelog CHANGELOG.md] [--out PATH]
#
# prs.json maps the candidate id (from `analyze`) to PR number(s):
#   {"0": "8216", "1": "8216", "12": "8133,8134"}

import argparse
import json
import re
import sys
from datetime import date

VERSION_RE = re.compile(r"^v[0-9]+\.[0-9]+\.[0-9]+$")
SECTION_RE = re.compile(r"^- (.+)$")
CONTENT_RE = re.compile(r"^  - ")
MARKER = "<!-- linter-versions-end -->"
LV_PREFIX = "Linter versions upgrades"
LV_LINE_RE = re.compile(
    r"^  - \[([^\]]+)\]\(([^)]+)\)\s+from\s+(\S+)\s+to\s+\*\*([^*]+)\*\*"
)


def split_blocks(lines):
    start = next(i for i, line in enumerate(lines) if line.startswith("## [Unreleased]"))
    end = next(i for i in range(start + 1, len(lines)) if lines[i].startswith("## ["))
    return lines[:start], lines[start:end], lines[end:]


def parse_sections(block):
    idxs = [i for i, line in enumerate(block) if SECTION_RE.match(line)]
    sections = []
    for k, idx in enumerate(idxs):
        name = block[idx][2:].strip()
        nxt = idxs[k + 1] if k + 1 < len(idxs) else len(block)
        sections.append((block[idx], name, block[idx+1:nxt]))
    return sections


def has_reference(line):
    if re.search(r"\(#\d+\)", line):
        return True
    if re.search(r"(?:^|[\s(])#\d+", line):
        return True
    if "github.com/oxsecurity/megalinter" in line:
        return True
    return False


def candidates(sections):
    out = []
    cid = 0
    for _, name, content in sections:
        if name.startswith(LV_PREFIX):
            continue
        for line in content:
            if not CONTENT_RE.match(line):
                continue
            if has_reference(line):
                continue
            out.append({"id": cid, "section": name, "text": line.strip()})
            cid += 1
    return out


def candidate_ids(sections):
    ids = {}
    cid = 0
    for _, name, content in sections:
        if name.startswith(LV_PREFIX):
            continue
        for j, line in enumerate(content):
            if not CONTENT_RE.match(line) or has_reference(line):
                continue
            ids[(name, j)] = cid
            cid += 1
    return ids


def collapse_versions(content):
    order = []
    data = {}
    for line in content:
        m = LV_LINE_RE.match(line)
        if not m:
            continue
        name, url, frm, to = m.groups()
        if name not in data:
            data[name] = {"url": url, "first_from": frm, "last_to": to}
            order.append(name)
        else:
            data[name]["last_to"] = to
    lines = []
    for name in sorted(data, key=str.lower):
        d = data[name]
        lines.append(f"  - [{name}]({d['url']}) from {d['first_from']} to **{d['last_to']}**")
    return lines


def format_prs(value):
    if isinstance(value, list):
        nums = [str(v).lstrip("#") for v in value]
    else:
        nums = [p.strip().lstrip("#") for p in str(value).split(",") if p.strip()]
    return " (" + ", ".join(f"#{n}" for n in nums) + ")"


def cmd_analyze(args):
    lines = open(args.changelog, encoding="utf-8").read().split("\n")
    _, block, _ = split_blocks(lines)
    sections = parse_sections(block)
    print(json.dumps(candidates(sections), indent=2, ensure_ascii=False))


def cmd_apply(args):
    if not VERSION_RE.match(args.version):
        sys.exit(f"--version must match vX.Y.Z, got: {args.version}")
    release_date = args.date or date.today().strftime("%Y-%m-%d")

    prs = {}
    if args.prs:
        prs = json.load(open(args.prs, encoding="utf-8"))

    lines = open(args.changelog, encoding="utf-8").read().split("\n")
    preamble, block, rest = split_blocks(lines)
    sections = parse_sections(block)
    ids = candidate_ids(sections)

    # Fresh Unreleased block (repo convention keeps the (N) placeholder).
    fresh = [
        "## [Unreleased] (beta, main branch content)",
        "",
        "Note: Can be used with `oxsecurity/megalinter@beta` in your GitHub Action "
        "mega-linter.yml file, or with `oxsecurity/megalinter:beta` docker image",
        "",
    ]
    for header, name, _ in sections:
        if name.startswith(LV_PREFIX):
            fresh.append(f"- {LV_PREFIX} (N)")
            fresh.append(MARKER)
        else:
            fresh.append(header)
        fresh.append("")

    # Released entry.
    released = [f"## [{args.version}] - {release_date}", ""]
    for header, name, content in sections:
        is_lv = name.startswith(LV_PREFIX)
        has_item = any(CONTENT_RE.match(c) for c in content)
        if not is_lv and not has_item:
            continue
        if is_lv:
            collapsed = collapse_versions(content)
            released.append(f"- {LV_PREFIX} ({len(collapsed)})")
            released.extend(collapsed)
        else:
            released.append(header)
            for j, line in enumerate(content):
                if line.strip() == "" or line.strip() == MARKER:
                    continue
                cid = ids.get((name, j))
                if cid is not None and str(cid) in prs:
                    line = line + format_prs(prs[str(cid)])
                released.append(line)
        released.append("")

    out_lines = preamble + fresh + released + rest
    out_path = args.out or args.changelog
    open(out_path, "w", encoding="utf-8").write("\n".join(out_lines))
    print(f"Wrote {out_path} (release {args.version} - {release_date}, "
          f"{len([s for s in sections if s[1].startswith(LV_PREFIX)])} version section)")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="CHANGELOG release transformer")
    sub = parser.add_subparsers(dest="cmd", required=True)

    pa = sub.add_parser("analyze", help="list content lines lacking a PR reference")
    pa.add_argument("--changelog", default="CHANGELOG.md")
    pa.set_defaults(func=cmd_analyze)

    pp = sub.add_parser("apply", help="perform the release transformation")
    pp.add_argument("--version", required=True)
    pp.add_argument("--date", default=None)
    pp.add_argument("--prs", default=None, help="JSON file: {candidate_id: pr_numbers}")
    pp.add_argument("--changelog", default="CHANGELOG.md")
    pp.add_argument("--out", default=None, help="write here instead of in place")
    pp.set_defaults(func=cmd_apply)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
