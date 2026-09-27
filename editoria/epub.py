"""EPUB 3 refluível, com sumário e artes opcionais nos capítulos."""

from __future__ import annotations

import html
import io
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

from .markdown import render_html
from .project import Project, safe_relative_file


BOOK_CSS = """body{font-family:serif;line-height:1.55;margin:5%;color:#25221e}h1,h2{text-align:center;line-height:1.2}h1{font-size:1.1em;margin-top:1.5em}h2{font-size:1.6em;margin-bottom:1.3em}p{text-indent:1.2em;margin:.25em 0;text-align:left}h2+p,.art+p,.scene+p{text-indent:0}blockquote{font-style:italic;margin:1em 8%}ul,ol{margin:1em 0 1em 1.5em}li{margin:.3em 0}.scene{border:0;text-align:center;margin:1.5em 0}.scene:after{content:'• • •';letter-spacing:.6em}.art{text-align:center;margin:1em 0 1.5em}.art img{max-width:100%;height:auto}.cover{margin:0;text-align:center}.cover img{max-width:100%;height:auto}.titlepage{text-align:center;margin-top:20%}.titlepage p{text-indent:0;text-align:center}"""


def _xhtml(title: str, body: str, *, nav: bool = False, nested: bool = False) -> str:
    nav_namespace = ' xmlns:epub="http://www.idpf.org/2007/ops"' if nav else ""
    stylesheet = "../book.css" if nested else "book.css"
    return f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"{nav_namespace} xml:lang="pt-BR"><head><meta charset="utf-8"/><title>{html.escape(title)}</title><link rel="stylesheet" type="text/css" href="{stylesheet}"/></head><body>{body}</body></html>'''


def _jpeg_bytes(path: Path, max_side: int = 1800) -> bytes:
    with Image.open(path) as original:
        image = original.convert("RGB")
        image.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
        stream = io.BytesIO()
        image.save(stream, format="JPEG", quality=90, optimize=True)
        return stream.getvalue()


def build_epub(project: Project, destination: Path) -> Path:
    cover_value = str(project.config.get("capa_ebook", ""))
    cover = safe_relative_file(project.root, cover_value)
    if not cover.is_file():
        raise ValueError("Adicione capa_ebook em livro.json antes de gerar o EPUB.")
    destination.mkdir(parents=True, exist_ok=True)
    filename = str(project.config.get("id", "livro")) + ".epub"
    target = destination / filename

    entries: list[tuple[str, str, str]] = []  # id, href, title
    contents: dict[str, bytes] = {}
    manifest: list[str] = [
        '<item id="css" href="book.css" media-type="text/css"/>',
        '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
        '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>',
        '<item id="cover-image" href="images/cover.jpg" media-type="image/jpeg" properties="cover-image"/>',
        '<item id="cover-page" href="cover.xhtml" media-type="application/xhtml+xml"/>',
    ]
    spine = ['<itemref idref="cover-page"/>']
    contents["OEBPS/book.css"] = BOOK_CSS.encode("utf-8")
    contents["OEBPS/images/cover.jpg"] = _jpeg_bytes(cover, 2560)
    contents["OEBPS/cover.xhtml"] = _xhtml(project.title, '<div class="cover"><img src="images/cover.jpg" alt="Capa do livro"/></div>').encode("utf-8")

    contents["OEBPS/titlepage.xhtml"] = _xhtml("Página de rosto", f'<div class="titlepage"><h1>{html.escape(project.title)}</h1><p>{html.escape(project.author)}</p></div>').encode("utf-8")
    contents["OEBPS/copyright.xhtml"] = _xhtml("Direitos autorais", f'<section><h1>Direitos autorais</h1><p>© {project.config["ano_publicacao"]} {html.escape(project.author)}. Todos os direitos reservados.</p><p>Esta é uma obra de ficção. Personagens e acontecimentos foram criados para esta narrativa.</p></section>').encode("utf-8")
    manifest.extend(['<item id="titlepage" href="titlepage.xhtml" media-type="application/xhtml+xml"/>', '<item id="copyright" href="copyright.xhtml" media-type="application/xhtml+xml"/>'])
    spine.extend(['<itemref idref="titlepage"/>', '<itemref idref="copyright"/>'])
    entries.extend([("titlepage", "titlepage.xhtml", "Página de rosto"), ("copyright", "copyright.xhtml", "Direitos autorais")])

    opening = project.source("ABERTURA.md")
    if opening.strip():
        section_id = "opening"
        href = "opening.xhtml"
        body = f'<section epub:type="frontmatter" xmlns:epub="http://www.idpf.org/2007/ops">{render_html(opening)}</section>'
        contents[f"OEBPS/{href}"] = _xhtml("Abertura", body).encode("utf-8")
        manifest.append(f'<item id="{section_id}" href="{href}" media-type="application/xhtml+xml"/>')
        spine.append(f'<itemref idref="{section_id}"/>')
        entries.append((section_id, href, "Abertura"))

    for chapter in project.chapters:
        section_id = f"chapter-{chapter.number:03d}"
        href = f"chapters/{section_id}.xhtml"
        art_markup = ""
        art = project.art_for(chapter.number)
        if art:
            source, alt = art
            img_id = f"art-{chapter.number:03d}"
            image_href = f"images/{img_id}.jpg"
            contents[f"OEBPS/{image_href}"] = _jpeg_bytes(source)
            manifest.append(f'<item id="{img_id}" href="{image_href}" media-type="image/jpeg"/>')
            art_markup = f'<div class="art"><img src="../{image_href}" alt="{html.escape(alt, quote=True)}"/></div>'
        body = f'<section><h1>Capítulo {chapter.number}</h1><h2>{html.escape(chapter.title)}</h2>{art_markup}{render_html(chapter.body)}</section>'
        contents[f"OEBPS/{href}"] = _xhtml(chapter.title, body, nested=True).encode("utf-8")
        manifest.append(f'<item id="{section_id}" href="{href}" media-type="application/xhtml+xml"/>')
        spine.append(f'<itemref idref="{section_id}"/>')
        entries.append((section_id, href, f"{chapter.number}. {chapter.title}"))

    for name, title, section_id in (("AGRADECIMENTOS.md", "Agradecimentos", "thanks"), ("SOBRE_AUTORIA.md", "Sobre a autoria", "about")):
        source = project.source(name)
        if source.strip():
            href = f"{section_id}.xhtml"
            contents[f"OEBPS/{href}"] = _xhtml(title, render_html(source)).encode("utf-8")
            manifest.append(f'<item id="{section_id}" href="{href}" media-type="application/xhtml+xml"/>')
            spine.append(f'<itemref idref="{section_id}"/>')
            entries.append((section_id, href, title))

    nav_items = "".join(f'<li><a href="{html.escape(href, quote=True)}">{html.escape(title)}</a></li>' for _, href, title in entries)
    contents["OEBPS/nav.xhtml"] = _xhtml("Sumário", f'<nav epub:type="toc" id="toc"><h1>Sumário</h1><ol>{nav_items}</ol></nav>', nav=True).encode("utf-8")
    identifier = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, str(project.config.get("id", project.title))))
    ncx_items = "".join(f'<navPoint id="n{index}" playOrder="{index}"><navLabel><text>{html.escape(title)}</text></navLabel><content src="{html.escape(href, quote=True)}"/></navPoint>' for index, (_, href, title) in enumerate(entries, 1))
    contents["OEBPS/toc.ncx"] = f'''<?xml version="1.0" encoding="utf-8"?><ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1"><head><meta name="dtb:uid" content="{identifier}"/></head><docTitle><text>{html.escape(project.title)}</text></docTitle><navMap>{ncx_items}</navMap></ncx>'''.encode("utf-8")
    modified = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    contents["OEBPS/content.opf"] = f'''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" xmlns:dc="http://purl.org/dc/elements/1.1/" version="3.0" unique-identifier="bookid" xml:lang="{html.escape(project.language, quote=True)}">
<metadata><dc:identifier id="bookid">{identifier}</dc:identifier><dc:title>{html.escape(project.title)}</dc:title><dc:creator>{html.escape(project.author)}</dc:creator><dc:language>{html.escape(project.language)}</dc:language><dc:description>{html.escape(str(project.config.get("sinopse", "")))}</dc:description><meta property="dcterms:modified">{modified}</meta><meta name="cover" content="cover-image"/></metadata>
<manifest>{''.join(manifest)}</manifest><spine toc="ncx">{''.join(spine)}</spine></package>'''.encode("utf-8")
    contents["META-INF/container.xml"] = b'''<?xml version="1.0" encoding="utf-8"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>'''

    with zipfile.ZipFile(target, "w") as archive:
        archive.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        for name, data in contents.items():
            archive.writestr(name, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return target
