# statussnapshot

Snapshot and diff local development environment status from the command line.

## About

`statussnapshot` captures a lightweight JSON snapshot of environment facts for a project directory—Python version/path, Node version/path, current git branch, dirty state, and last commit. Later snapshots can be diffed to see exactly what changed in your environment since the last capture.

## Features

- Capture environment fields with `statussnapshot capture`
- Inspect stored snapshots with `statussnapshot show`
- Diff two snapshots with `statussnapshot diff`
- Output is plain JSON, easy to pipe into other tooling
- Pure stdlib vended package; install optional

## Installation

```bash
python -m pip install -e .
```

## Usage

```bash
statussnapshot capture --directory . --output .statussnapshot.json
statussnapshot show .statussnapshot.json
statussnapshot diff prev.json .statussnapshot.json
```

### Available fields

By default, capture uses: `py-version`, `python-path`, `node-version`, `npm-path`, `git-branch`, `git-dirty`, `last-commit`.

Override with `--field`:

```bash
statussnapshot capture --directory . --field py-version --field git-branch
```

## Project structure

```
statussnapshot/
├── pyproject.toml
├── README.md
├── src/ or flat package layout
├── statussnapshot/
│   ├── __init__.py
│   ├── cli.py
│   ├── core.py
│   ├── fields.py
│   └── reporters.py
├── tests/
└── docs/
```

## Tags / keywords

cli, environment, git, snapshot, python, node, developer-tools, json


Repository: https://github.com/Axelgustavlindstrom/statussnapshot
