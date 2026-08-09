"""Command-line interface for statussnapshot."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from statussnapshot.core import Snapshot, load_snapshot, save_snapshot
from statussnapshot.fields import TOOL_REGISTRY, run_tool
from statussnapshot.reporters import render_summary_snapshot


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="statussnapshot", description="Snapshot and diff local environment status.")
    subparsers = parser.add_subparsers(dest="command")

    capture = subparsers.add_parser("capture", help="Capture environment snapshot from a directory.")
    capture.add_argument("--directory", default=".", help="Target directory containing projects to inspect.")
    capture.add_argument("--field", action="append", dest="fields", help="Field to capture; repeat for multiple fields.")
    capture.add_argument("--output", default="statussnapshot.json", help="Path to write snapshot JSON.")
    capture.add_argument("--overwrite", action="store_true", help="Overwrite existing snapshot output.")

    show = subparsers.add_parser("show", help="Show stored snapshot contents.")
    show.add_argument("path", default="statussnapshot.json", nargs="?")

    diff = subparsers.add_parser("diff", help="Diff two snapshots.")
    diff.add_argument("old", default="prev.json", nargs="?")
    diff.add_argument("new", default="statussnapshot.json", nargs="?")
    return parser


def capture(command_args: argparse.Namespace) -> int:
    directory = Path(command_args.directory).resolve()
    output = Path(command_args.output)
    fields = command_args.fields if command_args.fields else list(TOOL_REGISTRY.keys())
    snapshot = Snapshot(origin=str(directory))
    rows = []
    for field in fields:
        data = run_tool(directory, field)
        if not data:
            continue
        rows.append((field, data))
    for field, data in rows:
        snapshot.upsert(field, data)
    if output.exists() and not command_args.overwrite:
        print(f"error: {output} already exists; pass --overwrite to replace it", file=sys.stderr)
        return 1
    save_snapshot(snapshot, output)
    print(f"captured {len(snapshot.entries)} entries to {output}")
    return 0


def show(command_args: argparse.Namespace) -> int:
    path = Path(command_args.path)
    if not path.exists():
        print(f"error: {path} does not exist", file=sys.stderr)
        return 1
    snapshot = load_snapshot(path)
    for entry in snapshot.entries:
        details = ", ".join(f"{k}={v}" for k, v in sorted(entry.items()) if k not in {"origin", "captured_at", "updated_at"})
        print(f"{entry['tool']}: {details}")
    return 0


def diff(command_args: argparse.Namespace) -> int:
    old_path = Path(command_args.old)
    new_path = Path(command_args.new)
    for path in (old_path, new_path):
        if not path.exists():
            print(f"error: {path} does not exist", file=sys.stderr)
            return 1
    old_snapshot = load_snapshot(old_path)
    new_snapshot = load_snapshot(new_path)
    diff_rows = new_snapshot.changes_against(old_snapshot)
    rendered = render_summary_snapshot(diff_rows)
    print(rendered.header)
    if rendered.body:
        print(rendered.body)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        if exc.code == 0:
            return 0
        raise
    if parsed.command is None:
        parser.print_help()
        return 0
    handlers = {"capture": capture, "show": show, "diff": diff}
    return handlers[parsed.command](parsed)


if __name__ == "__main__":
    sys.exit(main())
