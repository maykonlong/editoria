"""Checagens objetivas, com avisos para temas que exigem leitura humana."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass

from .lexicon import SUGGESTIONS
from .markdown import word_count
from .project import Project, safe_relative_file
from .workflow import status_report


@dataclass(frozen=True)
class Issue:
    severity: str
    code: str
    location: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def audit(project: Project) -> list[Issue]:
    issues: list[Issue] = []

    def add(severity: str, code: str, location: str, message: str) -> None:
        issues.append(Issue(severity, code, location, message))

    for key, label in (("titulo", "título"), ("autor", "autor"), ("sinopse", "sinopse"), ("publico", "público")):
        value = project.config.get(key)
        if not isinstance(value, str) or not value.strip() or "[PREENCHER" in value.upper():
            add("error", "METADADO", "livro.json", f"Preencha {label}.")
    year = project.config.get("ano_publicacao")
    if not isinstance(year, int) or not 1900 <= year <= 2200:
        add("error", "ANO_PUBLICACAO", "livro.json", "Defina ano_publicacao como ano válido antes de gerar os arquivos.")

    if not project.chapters:
        add("error", "SEM_CAPITULOS", "manuscrito/", "Escreva pelo menos um capítulo.")
    else:
        numbers = [chapter.number for chapter in project.chapters]
        expected = list(range(1, len(numbers) + 1))
        if numbers != expected:
            add("error", "SEQUENCIA", "manuscrito/", f"Capítulos: {numbers}; esperados: {expected}.")

    seen_titles: set[str] = set()
    sentences: dict[str, set[int]] = {}
    for chapter in project.chapters:
        location = f"manuscrito/{chapter.path.name}"
        text = chapter.path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
        if not text.startswith(f"# CAPÍTULO {chapter.number}\n## "):
            add("error", "CABECALHO", location, "Use # CAPÍTULO N na primeira linha e ## Título na segunda.")
        if not chapter.title:
            add("error", "TITULO", location, "Título do capítulo ausente.")
        elif chapter.title.casefold() in seen_titles:
            add("warning", "TITULO_REPETIDO", location, f"Título repetido: {chapter.title}.")
        seen_titles.add(chapter.title.casefold())

        count = word_count(chapter.body)
        if count < 300:
            add("warning", "CENA_CURTA", location, f"{count} palavras. Confirme se o capítulo tem uma virada ou consequência, sem alongar só por número.")
        if re.search(r"\[PREENCHER[^\]]*\]|\b(?:TODO|TBD|FIXME)\b", text, re.I):
            add("error", "RASCUNHO", location, "Há marcador de rascunho no texto.")
        if re.search(r"(?m)^\s*<[^>]+>", chapter.body):
            add("warning", "HTML", location, "HTML cru não é renderizado pelo conversor simples.")

        for term, suggestion in SUGGESTIONS.items():
            if re.search(rf"\b{re.escape(term)}\b", chapter.body, re.I):
                add("warning", "LINGUAGEM", location, f"Considere se '{term}' cabe no público; opção: {suggestion}.")

        for sentence in re.split(r"(?<=[.!?])\s+", chapter.body):
            normalized = " ".join(re.findall(r"[\wÀ-ÿ]+", sentence.casefold()))
            if len(normalized.split()) >= 12:
                sentences.setdefault(normalized, set()).add(chapter.number)

    for sentence, numbers in sentences.items():
        if len(numbers) > 1:
            sample = sentence[:85] + ("..." if len(sentence) > 85 else "")
            add("warning", "REPETICAO", "manuscrito/", f"Frase longa repetida nos capítulos {sorted(numbers)}: {sample}")

    arts = project.config.get("artes", [])
    if not isinstance(arts, list) or any(not isinstance(art, dict) for art in arts):
        add("error", "ARTES_FORMATO", "livro.json", "artes deve ser uma lista de objetos.")
        arts = []
    for art in arts:
        number = art.get("capitulo")
        try:
            file = safe_relative_file(project.root, str(art.get("arquivo", "")))
        except ValueError as exc:
            add("error", "ARTE_CAMINHO", "livro.json", str(exc))
            continue
        if number not in [chapter.number for chapter in project.chapters]:
            add("error", "ARTE_CAPITULO", "livro.json", f"Arte aponta para capítulo inexistente: {number}.")
        if not file.is_file():
            add("error", "ARTE_AUSENTE", "livro.json", f"Arquivo não encontrado: {file.name}.")
        if not str(art.get("descricao", "")).strip():
            add("error", "ARTE_ALT", "livro.json", f"Escreva texto alternativo para a arte do capítulo {number}.")

    cover = project.config.get("capa_ebook", "")
    if cover:
        try:
            if not safe_relative_file(project.root, str(cover)).is_file():
                add("warning", "CAPA_AUSENTE", "livro.json", "A capa do eBook não existe; geração KDP ficará bloqueada.")
        except ValueError as exc:
            add("error", "CAPA_CAMINHO", "livro.json", str(exc))
    else:
        add("warning", "SEM_CAPA", "livro.json", "Adicione uma capa antes de gerar o pacote KDP.")

    for source_name in ("ABERTURA.md", "AGRADECIMENTOS.md", "SOBRE_AUTORIA.md", "ULTIMA_PALAVRA.md"):
        source = project.source(source_name)
        if re.search(r"\[PREENCHER[^\]]*\]|\b(?:TODO|TBD|FIXME)\b", source, re.I):
            add("error", "RASCUNHO", f"manuscrito/{source_name}", "Há marcador de rascunho no texto de abertura/fecho.")

    site = project.config.get("site", {})
    mode = site.get("modo", "landing") if isinstance(site, dict) else ""
    if mode not in {"landing", "preview", "full"}:
        add("error", "SITE_MODO", "livro.json", "site.modo deve ser landing, preview ou full.")
    if mode == "full":
        add("warning", "PUBLICO_COMPLETO", "livro.json", "Texto integral no site público exige decisão explícita de direitos e distribuição.")
    if mode == "preview":
        count = site.get("capitulos_gratis", 0)
        if not isinstance(count, int) or not 1 <= count <= len(project.chapters):
            add("error", "PREVIA", "livro.json", "Defina site.capitulos_gratis entre 1 e o total de capítulos.")

    try:
        status = status_report(project)
    except ValueError as exc:
        add("error", "ESTADO_INVALIDO", "planejamento/ESTADO.json", str(exc))
    else:
        for number in status["estado_sem_manuscrito"]:
            add("error", "APROVADO_SEM_TEXTO", "planejamento/ESTADO.json", f"Capítulo {number} está aprovado, mas não há manuscrito.")
        for number in status["memorias_pendentes"]:
            add("warning", "MEMORIA_PENDENTE", f"memoria/CAP_{number:02d}.md", f"Registre a memória do capítulo {number} aprovado.")

    return issues


def has_errors(issues: list[Issue]) -> bool:
    return any(issue.severity == "error" for issue in issues)
