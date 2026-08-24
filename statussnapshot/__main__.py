"""Allow ``python -m statussnapshot`` to launch the CLI."""

from statussnapshot.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
