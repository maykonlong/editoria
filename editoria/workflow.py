"""Estado editorial explícito; jamais infere aprovação a partir do manuscrito."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .project import Project


STATES = frozenset({"planejado", "rascunho", "em_revisao", "aprovado"})


def load_state(root: Path) -> dict[str, Any]:
    path = root / "planejamento" / "ESTADO.json"
    if not path.is_file():
        return {"capitulos": {}, "decisoes_pendentes": []}
    try:
        state = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"planejamento/ESTADO.json inválido: {exc}") from exc
    if not isinstance(state, dict):
        raise ValueError("planejamento/ESTADO.json deve conter um objeto JSON")
    chapters = state.get("capitulos", {})
    decisions = state.get("decisoes_pendentes", [])
    if not isinstance(chapters, dict) or any(
        not isinstance(number, str) or not re.fullmatch(r"\d{2,3}", number)
        or int(number) < 1 or chapter_state not in STATES
        for number, chapter_state in chapters.items()
    ):
        raise ValueError("ESTADO.json: capitulos deve mapear números de 2–3 dígitos para estados válidos")
    if len({int(number) for number in chapters}) != len(chapters):
        raise ValueError("ESTADO.json: há números de capítulo duplicados")
    if not isinstance(decisions, list) or any(not isinstance(item, str) or not item.strip() for item in decisions):
        raise ValueError("ESTADO.json: decisoes_pendentes deve ser uma lista de perguntas não vazias")
    return {"capitulos": chapters, "decisoes_pendentes": decisions}


def status_report(project: Project) -> dict[str, Any]:
    state = load_state(project.root)
    chapters = state["capitulos"]
    written = {chapter.number for chapter in project.chapters}
    approved = sorted(int(number) for number, value in chapters.items() if value == "aprovado")
    pending_memory: list[int] = []
    for number in approved:
        if number not in written:
            continue
        memory = project.root / "memoria" / f"CAP_{number:02d}.md"
        if not memory.is_file() or "[PREENCHER" in memory.read_text(encoding="utf-8-sig").upper():
            pending_memory.append(number)
    return {
        "titulo": project.title,
        "capitulos_planejados": len(chapters),
        "capitulos_escritos": len(written),
        "capitulos_aprovados": len(set(approved) & written),
        "capitulos_sem_estado": sorted(written - {int(number) for number in chapters}),
        "estado_sem_manuscrito": sorted(set(approved) - written),
        "memorias_pendentes": pending_memory,
        "decisoes_pendentes": state["decisoes_pendentes"],
    }
