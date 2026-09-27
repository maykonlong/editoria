"""Leitura do projeto; nenhum dado de um livro específico fica no motor."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CHAPTER_RE = re.compile(r"^CAP_(\d{2,3})_[A-Z0-9_]+\.md$")


@dataclass(frozen=True)
class Chapter:
    number: int
    path: Path
    title: str
    body: str


@dataclass(frozen=True)
class Project:
    root: Path
    config: dict[str, Any]
    chapters: tuple[Chapter, ...]

    @property
    def title(self) -> str:
        return str(self.config.get("titulo", "")).strip()

    @property
    def author(self) -> str:
        return str(self.config.get("autor", "")).strip()

    @property
    def language(self) -> str:
        return str(self.config.get("idioma", "pt-BR")).strip()

    def source(self, name: str) -> str:
        path = self.root / "manuscrito" / name
        return path.read_text(encoding="utf-8-sig") if path.is_file() else ""

    def art_for(self, chapter_number: int) -> tuple[Path, str] | None:
        for item in self.config.get("artes", []):
            if item.get("capitulo") == chapter_number:
                return safe_relative_file(self.root, str(item.get("arquivo", ""))), str(item.get("descricao", ""))
        return None


def safe_relative_file(root: Path, value: str) -> Path:
    """Impede que configuração leia arquivos fora do projeto por engano."""
    if not value or Path(value).is_absolute():
        raise ValueError(f"Caminho inválido no livro.json: {value!r}")
    candidate = (root / value).resolve()
    if not candidate.is_relative_to(root.resolve()):
        raise ValueError(f"Caminho sai do projeto: {value!r}")
    return candidate


def load_project(path: str | Path) -> Project:
    root = Path(path).resolve()
    config_path = root / "livro.json"
    if not config_path.is_file():
        raise FileNotFoundError(f"livro.json não encontrado em {root}")
    config = json.loads(config_path.read_text(encoding="utf-8-sig"))
    if not isinstance(config, dict):
        raise ValueError("livro.json precisa conter um objeto JSON")

    chapters: list[Chapter] = []
    manuscript = root / "manuscrito"
    for file in sorted(manuscript.glob("CAP_*.md")):
        match = CHAPTER_RE.fullmatch(file.name)
        if not match:
            raise ValueError(f"Nome de capítulo inválido: {file.name}")
        number = int(match.group(1))
        text = file.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
        lines = text.splitlines()
        title = lines[1][3:].strip() if len(lines) > 1 and lines[1].startswith("## ") else ""
        body = "\n".join(lines[2:]).strip() if len(lines) > 2 else ""
        chapters.append(Chapter(number, file, title, body))

    return Project(root, config, tuple(sorted(chapters, key=lambda chapter: chapter.number)))
