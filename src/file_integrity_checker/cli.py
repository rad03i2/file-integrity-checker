from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .core import build_baseline, load_baseline, report_dict, save_baseline, verify


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="file-integrity", description="Create and verify local SHA-256 file integrity baselines.")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__} — Radwan Abdulhadi Ahmed / @rad03i2")
    sub = p.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Create an integrity baseline")
    init.add_argument("root", type=Path)
    init.add_argument("-o", "--output", type=Path, default=Path("integrity-baseline.json"))
    init.add_argument("--include-hidden", action="store_true")
    init.add_argument("--overwrite", action="store_true")

    check = sub.add_parser("check", help="Verify files against a baseline")
    check.add_argument("baseline", type=Path)
    check.add_argument("--root", type=Path, help="Verify another copy/location instead of the recorded root")
    check.add_argument("--include-hidden", action="store_true")
    check.add_argument("--json", action="store_true", dest="as_json")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "init":
            data = build_baseline(args.root, args.include_hidden)
            save_baseline(data, args.output, args.overwrite)
            print(f"Baseline written: {args.output} ({len(data['files'])} files)")
            return 0
        baseline = load_baseline(args.baseline)
        changes = verify(baseline, args.root, args.include_hidden)
        report = report_dict(changes)
        if args.as_json:
            print(json.dumps(report, indent=2, ensure_ascii=False))
        elif not changes:
            print("OK: all tracked files match the baseline.")
        else:
            for change in changes:
                print(f"{change.status.upper():8} {change.path}")
            s = report["summary"]
            print(f"Changes: {len(changes)} (added={s['added']}, modified={s['modified']}, missing={s['missing']})")
        return 0 if not changes else 1
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
