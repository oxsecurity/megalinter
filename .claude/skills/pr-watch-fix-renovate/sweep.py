#!/usr/bin/env python3
# Deterministic helpers of the /pr-watch-fix-renovate sweep: group the PRs that fail
# with the same MegaLinter error, pick one carrier PR per group, and keep the
# sweep state between runs. Nothing here talks to GitHub.
#
# Usage:
#   python fingerprint.py 9474 9473 > fp.json        # from .claude/skills/pr-watch-fix
#   python sweep.py plan fp.json                     # groups, carriers, roles -> JSON
#   python sweep.py state show                       # state file content
#   python sweep.py state save plan.json             # record the groups of a plan
#   python sweep.py state update <fp_id> '{"carrier": {"status": "green"}}'
#   python sweep.py state drop <fp_id>
#   python sweep.py --selftest

import argparse
import io
import json
import subprocess
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if isinstance(_stream, io.TextIOWrapper):
        _stream.reconfigure(encoding="utf-8", errors="replace")


def state_path():
    common = subprocess.run(
        ["git", "rev-parse", "--git-common-dir"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    return Path(common).resolve() / "pr-watch-fix-renovate" / "state.json"


def load_state():
    path = state_path()
    if not path.exists():
        return {"groups": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def write_state(state):
    path = state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def build_plan(prs):
    open_prs = {p["pr"]: p for p in prs if p["state"] == "OPEN"}

    # A PR without any check is not green: its CI never ran (approval gate...)
    no_checks = sorted(n for n, p in open_prs.items() if p["checks"] == 0)
    pending = sorted(
        n for n, p in open_prs.items() if p["pending"] and n not in no_checks
    )
    ready = {
        n: p for n, p in open_prs.items() if n not in no_checks and n not in pending
    }

    shared = {}
    for number, pr in sorted(ready.items()):
        for fp in pr["fingerprints"]:
            entry = shared.setdefault(fp["id"], {"fp": fp, "prs": []})
            if number not in entry["prs"]:
                entry["prs"].append(number)
    groups = {gid: e for gid, e in shared.items() if len(e["prs"]) >= 2}

    def rank(number, gid):
        pr = ready[number]
        other = bool(pr["other_failures"]) or any(
            fp["id"] not in groups for fp in pr["fingerprints"]
        )
        related = any(fp["related"] for fp in pr["fingerprints"] if fp["id"] == gid)
        return (
            other,
            related,
            pr["update_type"] == "major",
            pr["changed_files"],
            number,
        )

    # A PR that already carries another group is preferred: fewer PRs to merge
    carriers = set()
    for gid in sorted(groups, key=lambda g: (-len(groups[g]["prs"]), g)):
        candidates = groups[gid]["prs"]
        pool = [c for c in candidates if c in carriers] or candidates
        groups[gid]["carrier"] = min(pool, key=lambda c: rank(c, gid))
        carriers.add(groups[gid]["carrier"])

    roles = {}
    for number, pr in sorted(ready.items()):
        carries = [g for g in groups if groups[g]["carrier"] == number]
        defers = [g for g in groups if number in groups[g]["prs"] and g not in carries]
        unshared = bool(pr["other_failures"]) or any(
            fp["id"] not in groups for fp in pr["fingerprints"]
        )
        if carries:
            role = "carrier"
        elif defers and unshared:
            role = "member"
        elif defers:
            role = "waiting"
        elif unshared:
            role = "unique"
        else:
            role = "green"
        roles[number] = {
            "role": role,
            "carries": carries,
            "defers": defers,
            "branch": pr["branch"],
            "title": pr["title"],
            "head_sha": pr["head_sha"],
        }
    return {
        "groups": [
            {
                "fp_id": gid,
                "linter_key": g["fp"]["linter_key"],
                "line": g["fp"]["line"],
                "carrier": g["carrier"],
                "members": [n for n in g["prs"] if n != g["carrier"]],
                "branches": {str(n): ready[n]["branch"] for n in g["prs"]},
            }
            for gid, g in groups.items()
        ],
        "prs": {str(n): r for n, r in roles.items()},
        "pending": pending,
        "no_checks": no_checks,
    }


def save_groups(plan):
    state = load_state()
    for group in plan["groups"]:
        state["groups"].setdefault(
            group["fp_id"],
            {
                "fp_id": group["fp_id"],
                "linter_key": group["linter_key"],
                "line": group["line"],
                "carrier": {
                    "pr": group["carrier"],
                    "branch": group["branches"][str(group["carrier"])],
                    "status": "fixing",
                },
                "members": [
                    {"pr": n, "branch": group["branches"][str(n)]}
                    for n in group["members"]
                ],
            },
        )
    write_state(state)


def update_group(fp_id, patch):
    state = load_state()
    group = state["groups"][fp_id]
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(group.get(key), dict):
            group[key].update(value)
        else:
            group[key] = value
    write_state(state)


def selftest():
    def pr(number, fps=(), other=(), kind="patch", files=2, related=False):
        return {
            "pr": number,
            "state": "OPEN",
            "checks": 3,
            "pending": False,
            "branch": f"renovate/b{number}",
            "title": f"t{number}",
            "head_sha": "x",
            "update_type": kind,
            "changed_files": files,
            "fingerprints": [
                {"id": f, "linter_key": "K", "line": "l", "related": related}
                for f in fps
            ],
            "other_failures": [{"check": c} for c in other],
        }

    prs = [
        pr(10, ["aa"], kind="major"),
        pr(11, ["aa"], other=["Trivy"]),
        pr(12, ["aa"], files=1),
        pr(13, ["bb"]),
        pr(14, ["aa", "cc"]),
        pr(15),
        pr(16, other=["Tests"]),
    ]
    prs.append({**pr(17), "pending": True})
    prs.append({**pr(18, ["aa"]), "state": "CLOSED"})
    prs.append({**pr(19), "checks": 0})
    plan = build_plan(prs)
    assert [g["carrier"] for g in plan["groups"]] == [12], plan["groups"]
    roles = {n: r["role"] for n, r in plan["prs"].items()}
    assert roles == {
        "10": "waiting",
        "11": "member",
        "12": "carrier",
        "13": "unique",
        "14": "member",
        "15": "green",
        "16": "unique",
    }, roles
    assert plan["pending"] == [17]
    assert plan["no_checks"] == [19]
    assert plan["prs"]["14"]["defers"] == ["aa"]

    # a related PR is a worse carrier; an existing carrier is reused across groups
    prs = [
        pr(1, ["aa"], related=True),
        pr(2, ["aa", "bb"]),
        pr(3, ["bb"], files=1),
        pr(4, ["aa"], files=9),
    ]
    plan = build_plan(prs)
    carriers = {g["fp_id"]: g["carrier"] for g in plan["groups"]}
    assert carriers == {"aa": 2, "bb": 2}, carriers
    print("selftest OK")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    sub = parser.add_subparsers(dest="command")
    plan_cmd = sub.add_parser("plan")
    plan_cmd.add_argument("fingerprints", help="JSON written by fingerprint.py")
    state_cmd = sub.add_parser("state")
    state_cmd.add_argument("action", choices=["show", "save", "update", "drop"])
    state_cmd.add_argument("args", nargs="*")
    args = parser.parse_args()

    if args.selftest:
        selftest()
    elif args.command == "plan":
        prs = json.loads(Path(args.fingerprints).read_text(encoding="utf-8-sig"))
        print(json.dumps(build_plan(prs), indent=2, ensure_ascii=False))
    elif args.command == "state":
        if args.action == "show":
            print(json.dumps(load_state(), indent=2, ensure_ascii=False))
        elif args.action == "save":
            save_groups(json.loads(Path(args.args[0]).read_text(encoding="utf-8-sig")))
        elif args.action == "update":
            update_group(args.args[0], json.loads(args.args[1]))
        else:
            state = load_state()
            state["groups"].pop(args.args[0], None)
            write_state(state)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
