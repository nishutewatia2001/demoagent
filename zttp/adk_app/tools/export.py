"""Export helpers for writing Markdown artifacts."""

from __future__ import annotations

from pathlib import Path


def md_export(path: str, content: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")

