"""Field probes for local environment detection."""

from __future__ import annotations

from pathlib import Path
from typing import Any


TOOL_REGISTRY: dict[str, tuple[str, ...]] = {
    "py-version": ("python-version",),
    "python-path": ("python-path",),
    "node-version": ("node-version",),
    "npm-path": ("npm-path",),
    "git-branch": ("git-branch",),
    "git-dirty": ("git-dirty",),
    "last-commit": ("last-commit",),
}


def probe_python(probe: str) -> dict[str, Any]:
    import shutil
    import subprocess

    if probe == "py-version":
        return _probe_command_proc(shutil.which("python3"), ["--version"], "python-version")
    if probe == "python-path":
        binary = shutil.which("python3")
        if not binary:
            return {"_missing": True, "python-path": None}
        return {"_missing": False, "python-path": binary}
    return {}


def probe_node(probe: str) -> dict[str, Any]:
    import shutil
    import subprocess

    node = shutil.which("node")
    npm = shutil.which("npm")
    if probe == "node-version" and node:
        return _probe_command_proc(node, ["--version"], "node-version")
    if probe == "npm-path" and npm:
        return _probe_command_proc(npm, ["root", "-g"], "npm-path")
    return {}


def probe_git(directory: Path, probe: str) -> dict[str, Any]:
    import shutil
    import subprocess

    git = shutil.which("git")
    if not git:
        return {"_missing": True, probe.replace("-", "_"): None}
    args = [git, "-C", str(directory)]
    if probe == "git-branch":
        return _probe_command_proc(git, ["-C", str(directory), "rev-parse", "--abbrev-ref", "HEAD"], "git-branch")
    if probe == "git-dirty":
        return _probe_command_proc(git, ["-C", str(directory), "status", "--porcelain"], "git-dirty")
    if probe == "last-commit":
        return _probe_command_proc(git, ["-C", str(directory), "rev-parse", "--short", "HEAD"], "last-commit")
    return {}


def _probe_command_proc(binary: str | None, args: list[str], field: str) -> dict[str, Any]:
    if binary is None:
        return {"_missing": True, field: None}
    try:
        import subprocess

        result = subprocess.run([binary, *args], capture_output=True, text=True, check=False)
        value = result.stdout.strip()
        return {"_missing": False, field: value if value else None}
    except OSError:
        return {"_missing": True, field: None}


def run_tool(directory: Path, tool: str) -> dict[str, Any]:
    if tool in {"py-version", "python-path"}:
        info = probe_python(tool)
    elif tool in {"node-version", "npm-path"}:
        info = probe_node(tool)
    elif tool in TOOL_REGISTRY:
        info = probe_git(directory, tool)
    else:
        return {}
    info.setdefault("_missing", True if not info else False)
    return info
