"""Renderers for statussnapshot summaries and diffs."""

from __future__ import annotations

from dataclasses import dataclass

from statussnapshot.core import DiffRecord


@dataclass(frozen=True, slots=True)
class RenderedSnapshot:
    header: str
    body: str
    footer_comments_only: str


def render_summary_snapshot(diff: list[DiffRecord]) -> RenderedSnapshot:
    if not diff:
        return RenderedSnapshot(header="(no changes)", body="", footer_comments_only="# empty")
    lines = [f"- {row.tool}.{row.key}: {row.old_value} -> {row.new_value}" for row in diff]
    return RenderedSnapshot(header=f"diff ({len(diff)} changes)", body="\n".join(lines), footer_comments_only="# empty")
