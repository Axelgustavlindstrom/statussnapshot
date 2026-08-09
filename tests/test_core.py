import tempfile
from pathlib import Path

from statussnapshot.core import Snapshot, load_snapshot, save_snapshot


def test_upsert_adds_and_updates_same_tool_entry():
    snapshot = Snapshot()
    snapshot.upsert("toolA", {"python-version": "3.11"})
    snapshot.upsert("toolA", {"python-path": "/usr/bin/python3"})
    assert snapshot.entries == [
        {"tool": "toolA", "python-version": "3.11", "python-path": "/usr/bin/python3"}
    ]


def test_changes_against_no_diff():
    old = Snapshot(entries=[{"tool": "python", "version": "3.11"}])
    new = Snapshot(entries=[{"tool": "python", "version": "3.11"}])
    assert new.changes_against(old) == []


def test_changes_against_added_and_changed():
    old = Snapshot(entries=[{"tool": "python", "version": "3.10"}])
    new = Snapshot(entries=[
        {"tool": "python", "version": "3.11"},
    ])
    diffs = new.changes_against(old)
    keys = {(row.tool, row.key, row.old_value, row.new_value) for row in diffs}
    assert ("python", "version", "3.10", "3.11") in keys


def test_round_trip_preservation():
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "snapshot.json"
        original = Snapshot(origin="/tmp", entries=[
            {"tool": "python", "python-version": "3.11"}
        ])
        save_snapshot(original, path)
        reloaded = load_snapshot(path)
        assert reloaded.entries == original.entries
