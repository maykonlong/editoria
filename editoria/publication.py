"""Orquestra a saída privada, pública e editorial sem misturar os destinos."""

from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from pathlib import Path

from PIL import Image

from .audit import audit, has_errors
from .epub import build_epub
from .markdown import word_count
from .pdf import build_pdf
from .project import Project, safe_relative_file
from .web import write_site


def counts(project: Project) -> dict:
    per_chapter = [{"capitulo": chapter.number, "titulo": chapter.title, "palavras": word_count(chapter.body)} for chapter in project.chapters]
    story_words = sum(item["palavras"] for item in per_chapter)
    front_words = word_count(project.source("ABERTURA.md"))
    back_words = sum(word_count(project.source(name)) for name in ("AGRADECIMENTOS.md", "SOBRE_AUTORIA.md"))
    return {"capitulos": len(project.chapters), "palavras_historia": story_words, "palavras_abertura": front_words, "palavras_fechamento": back_words, "palavras_texto_total": story_words + front_words + back_words, "por_capitulo": per_chapter}


def compiled_manuscript(project: Project) -> str:
    parts = [f"# {project.title}", f"*{project.author}*"]
    for name in ("ABERTURA.md",):
        source = project.source(name).strip()
        if source:
            parts.append(source)
    for chapter in project.chapters:
        parts.append(chapter.path.read_text(encoding="utf-8-sig").strip())
    for name in ("AGRADECIMENTOS.md", "SOBRE_AUTORIA.md"):
        source = project.source(name).strip()
        if source:
            parts.append(source)
    return "\n\n---\n\n".join(parts) + "\n"


def _reset_kdp(project: Project) -> Path:
    destination = (project.root / "dist" / "kdp").resolve()
    if destination.parent != (project.root / "dist").resolve() or destination.name != "kdp":
        raise ValueError("Destino KDP inseguro")
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    return destination


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_kdp(project: Project) -> dict:
    cover = safe_relative_file(project.root, str(project.config.get("capa_ebook", "")))
    if not cover.is_file():
        raise ValueError("Capa de eBook ausente. Preencha capa_ebook no livro.json.")
    destination = _reset_kdp(project)
    with Image.open(cover) as source:
        image = source.convert("RGB")
        image.save(destination / "capa-ebook.jpg", format="JPEG", quality=93, optimize=True)
    epub = build_epub(project, destination)
    pdf, pages = build_pdf(project, destination)
    (destination / "manuscrito_integral.md").write_text(compiled_manuscript(project), encoding="utf-8")
    summary = counts(project)
    summary.update({"titulo": project.title, "autor": project.author, "idioma": project.language, "paginas_miolo": pages, "epub_bytes": epub.stat().st_size})
    (destination / "metadados.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (destination / "LEIA-ME.md").write_text(
        f"# Materiais de publicação — {project.title}\n\n"
        f"{len(project.chapters)} capítulos; {summary['palavras_historia']} palavras de história; {pages} páginas no PDF 5,5 × 8,5.\n\n"
        "Este pacote inclui EPUB, capa do eBook, fonte e miolo PDF. **Não inclui a capa completa do impresso.** "
        "A capa completa depende da paginação final e das especificações atuais da gráfica/KDP. Confira também ficha catalográfica, "
        "ISBN quando aplicável, direitos, metadados, Kindle Previewer, Previewer de impressão e prova física. "
        "Não envie este diretório inteiro para hospedagem pública.\n",
        encoding="utf-8",
    )
    files = sorted(path for path in destination.iterdir() if path.is_file())
    checksums = "".join(f"{_sha256(path)}  {path.name}\n" for path in files)
    (destination / "SHA256SUMS.txt").write_text(checksums, encoding="ascii")
    package = destination / "materiais-publicacao.zip"
    with zipfile.ZipFile(package, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(destination.iterdir()):
            if path.is_file() and path != package:
                archive.write(path, arcname=path.name)
    summary["pacote_bytes"] = package.stat().st_size
    return summary


def generate(project: Project, only: str = "tudo", allow_full: bool = False) -> dict:
    issues = audit(project)
    if has_errors(issues):
        details = "\n".join(f"- {issue.location}: {issue.message}" for issue in issues if issue.severity == "error")
        raise ValueError("Corrija antes de gerar:\n" + details)
    site = project.config.get("site", {})
    if only in {"publico", "tudo"} and site.get("modo") == "full" and not allow_full:
        raise ValueError("Site público integral bloqueado. Use --permitir-publico-completo somente após decidir conscientemente.")
    if only in {"kdp", "tudo"}:
        cover = str(project.config.get("capa_ebook", ""))
        if not cover or not safe_relative_file(project.root, cover).is_file():
            raise ValueError("Capa de eBook ausente. Preencha capa_ebook no livro.json.")
    report = counts(project)
    report["avisos"] = [issue.to_dict() for issue in issues if issue.severity == "warning"]
    report["saidas"] = {}
    if only in {"leitura", "tudo"}:
        private = write_site(project, private=True)
        (private / "manuscrito_integral.md").write_text(compiled_manuscript(project), encoding="utf-8")
        report["saidas"]["revisao"] = str(private)
    if only in {"publico", "tudo"}:
        public = write_site(project, private=False, allow_full=allow_full)
        report["saidas"]["publico"] = str(public)
    if only in {"kdp", "tudo"}:
        publication = build_kdp(project)
        report["paginas_miolo"] = publication["paginas_miolo"]
        report["epub_bytes"] = publication["epub_bytes"]
        report["saidas"]["kdp"] = str(project.root / "dist" / "kdp")
    dist = project.root / "dist"
    dist.mkdir(exist_ok=True)
    (dist / "relatorio.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report
