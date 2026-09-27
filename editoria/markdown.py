"""Subset deliberado de Markdown: seguro e igual no site, EPUB e PDF."""

from __future__ import annotations

import html
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Block:
    kind: str
    text: str = ""


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\wÀ-ÿ]+\b", text, flags=re.UNICODE))


def blocks(source: str) -> list[Block]:
    result: list[Block] = []
    paragraph: list[str] = []

    def flush() -> None:
        if paragraph:
            result.append(Block("paragraph", " ".join(paragraph)))
            paragraph.clear()

    for raw in source.replace("\r\n", "\n").replace("\ufeff", "").splitlines():
        line = raw.strip()
        if not line:
            flush()
        elif line in {"---", "***"}:
            flush()
            result.append(Block("scene"))
        elif line.startswith("### "):
            flush()
            result.append(Block("h3", line[4:]))
        elif line.startswith("## "):
            flush()
            result.append(Block("h2", line[3:]))
        elif line.startswith("# "):
            flush()
            result.append(Block("h1", line[2:]))
        elif line.startswith("> "):
            flush()
            result.append(Block("quote", line[2:]))
        elif re.match(r"^[-*] \S", line):
            flush()
            result.append(Block("bullet", line[2:]))
        elif re.match(r"^\d+\. \S", line):
            flush()
            result.append(Block("number", re.sub(r"^\d+\. ", "", line)))
        elif line.startswith("—") or line.startswith('*"'):
            flush()
            result.append(Block("paragraph", line))
        else:
            paragraph.append(line)
    flush()
    return result


def inline(text: str) -> str:
    escaped = html.escape(text, quote=False)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", escaped)
    return escaped


def render_html(source: str) -> str:
    output: list[str] = []
    open_list: str | None = None
    for block in blocks(source):
        wanted = "ul" if block.kind == "bullet" else "ol" if block.kind == "number" else None
        if open_list and wanted != open_list:
            output.append(f"</{open_list}>")
            open_list = None
        if wanted:
            if not open_list:
                output.append(f"<{wanted}>")
                open_list = wanted
            output.append(f"<li>{inline(block.text)}</li>")
        elif block.kind == "scene":
            output.append('<hr class="scene"/>')
        elif block.kind == "quote":
            output.append(f"<blockquote>{inline(block.text)}</blockquote>")
        elif block.kind in {"h1", "h2", "h3"}:
            output.append(f"<{block.kind}>{inline(block.text)}</{block.kind}>")
        else:
            output.append(f"<p>{inline(block.text)}</p>")
    if open_list:
        output.append(f"</{open_list}>")
    return "\n".join(output)
