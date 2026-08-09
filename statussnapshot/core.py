"""Snapshot data model and diff logic."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class DiffRecord:
    tool: str
    key: str
    old_value: Any = None
    new_value: Any = None
    event: str = "added"
    updated_at: str = ""


@dataclass
class Snapshot:
    origin: str = "."
    captured_at: str = ""
    entries: list[dict[str, object]] = field(default_factory=list)

    MISSING_KEYS = {"origin", "captured_at", "updated_at", "tool"}

    def upsert(self, tool: str, fields: dict[str, object]) -> None:
        existing = None
        for entry in self.entries:
            if entry.get("tool") == tool:
                existing = entry
                break
        if existing is None:
            entry: dict[str, object] = {"tool": tool}
            entry.update(fields)
            self.entries.append(entry)
            return
        existing.update(fields)

    def changes_against(self, previous: Snapshot) -> list[DiffRecord]:
        old_map: dict[str, dict[str, object]] = {}
        for entry in (previous.entries if previous and previous.entries else []):
            if "tool" in entry:
                old_map[entry["tool"]] = {k: v for k, v in entry.items() if k not in self.MISSING_KEYS}
        new_map: dict[str, dict[str, object]] = {}
        for entry in (self.entries if self.entries else []):
            if "tool" in entry:
                new_map[entry["tool"]] = {k: v for k, v in entry.items() if k not in self.MISSING_KEYS}

        diffs: list[DiffRecord] = []
        for tool, new_fields in new_map.items():
            old_fields = old_map.get(tool, {})
            for key, value in new_fields.items():
                if value != old_fields.get(key):
                    diffs.append(DiffRecord(tool=tool, key=str(key), old_value=old_fields.get(key), new_value=value, event="added", updated_at=self.captured_at))
        return diffs


def load_snapshot(path: Path) -> Snapshot:
    text = path.read_text(encoding="utf-8")
    data = json.loads(text)
    if isinstance(data, list):
        entries = [dict(entry) for entry in data]
        origin = entries[0].get("origin", ".") if entries else "."
        return Snapshot(origin=origin, entries=entries)
    entries = [dict(entry) for entry in data.get("entries", [])]
    return Snapshot(origin=str(data.get("origin", ".")), captured_at=str(data.get("captured_at", "")), entries=entries)


def save_snapshot(snapshot: Snapshot, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {"origin": snapshot.origin, "captured_at": snapshot.captured_at, "entries": snapshot.entries}
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def render_diff(diff: list[DiffRecord]) -> str:
    if not diff:
        return "(no changes)"
    return "\n".join(f"- {row.tool}.{row.key}: {row.old_value} -> {row.new_value}" for row in diff)
