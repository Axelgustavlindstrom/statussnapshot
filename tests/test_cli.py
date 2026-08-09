import contextlib
import io
from pathlib import Path

from statussnapshot.cli import main
from statussnapshot.reporters import render_summary_snapshot


def test_main_help_returns_zero():
    rc = main(["--help"])
    assert rc == 0


def test_capture_creates_snapshot(tmp_path: Path):
    output = tmp_path / "snapshot.json"
    rc = main(["capture", "--directory", str(tmp_path), "--output", str(output)])
    assert rc == 0
    assert output.exists()


def test_capture_refuses_overwrite_without_flag(tmp_path: Path):
    output = tmp_path / "snapshot.json"
    rc = main(["capture", "--directory", str(tmp_path), "--output", str(output)])
    assert rc == 0
    rc = main(["capture", "--directory", str(tmp_path), "--output", str(output)])
    assert rc == 1


def test_show_missing_snapshot_returns_one(tmp_path: Path):
    path = tmp_path / "missing.json"
    rc = main(["show", str(path)])
    assert rc == 1


def test_diff_missing_snapshot_returns_one(tmp_path: Path):
    old = tmp_path / "old.json"
    new = tmp_path / "new.json"
    rc = main(["diff", str(old), str(new)])
    assert rc == 1


def test_diff_snapshots_renders_changes(tmp_path: Path):
    old = tmp_path / "old.json"
    new = tmp_path / "new.json"
    old.write_text('{"origin": ".", "captured_at": "", "entries": [{"tool": "python", "version": "3.10"}]}')
    new.write_text('{"origin": ".", "captured_at": "", "entries": [{"tool": "python", "version": "3.11"}]}')
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        rc = main(["diff", str(old), str(new)])
    assert rc == 0
    text = stdout.getvalue()
    assert "3.10 -> 3.11" in text


def test_render_summary_snapshot_empty():
    rendered = render_summary_snapshot([])
    assert rendered.header == "(no changes)"
    assert rendered.body == ""


def test_render_summary_snapshot_changes():
    rendered = render_summary_snapshot([type("DiffRecord", (), {"tool": "python", "key": "version", "old_value": "3.10", "new_value": "3.11"})()])
    assert "3.10 -> 3.11" in rendered.body
