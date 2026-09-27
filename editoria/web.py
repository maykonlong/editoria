"""Site estático acessível: saída pública separada da revisão privada."""

from __future__ import annotations

import html
import json
import shutil
from datetime import date
from pathlib import Path
from urllib.parse import urljoin

from .markdown import render_html
from .project import Chapter, Project, safe_relative_file


CSS = """
:root{--ink:#20332c;--paper:#f8f5ed;--card:#fffdf8;--line:#d8d4c8;--accent:#a44d39;--muted:#58675e;--measure:68ch}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font-family:Georgia,'Times New Roman',serif;line-height:1.65}
a{color:var(--accent)}a:hover{text-decoration-thickness:2px}a:focus-visible,button:focus-visible{outline:3px solid var(--accent);outline-offset:3px}
.skip{position:absolute;left:-10000px;top:auto}.skip:focus{left:1rem;top:1rem;z-index:20;background:var(--card);padding:.5rem}
.top{border-bottom:1px solid var(--line);background:var(--card)}.top-inner{max-width:1100px;margin:auto;padding:1rem 1.25rem;display:flex;align-items:center;justify-content:space-between;gap:1rem}
.brand{font-size:.9rem;letter-spacing:.06em;text-transform:uppercase;font-weight:bold;text-decoration:none;color:var(--ink)}.top nav{display:flex;gap:1rem;flex-wrap:wrap}.top nav a{font:600 .85rem/1.2 system-ui,sans-serif;text-decoration:none}
.hero,.section,.reader-shell{max-width:1100px;margin:auto;padding:clamp(2.5rem,6vw,6rem) 1.25rem}.hero{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(220px,.8fr);gap:clamp(2rem,5vw,5rem);align-items:center;min-height:70vh}.hero>*{min-width:0}
.eyebrow{font:700 .76rem/1.4 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.18em;color:var(--accent)}h1,h2,h3{line-height:1.13;letter-spacing:-.025em}h1{font-size:clamp(2.9rem,7vw,5.5rem);max-width:15ch;margin:.35em 0}h2{font-size:clamp(1.9rem,4vw,3rem)}.lead{font-size:clamp(1.1rem,2vw,1.35rem);max-width:48ch}.actions{display:flex;flex-wrap:wrap;gap:.75rem;margin-top:2rem}.button{display:inline-block;border:1px solid var(--accent);background:var(--accent);color:#fff;text-decoration:none;padding:.8rem 1.15rem;border-radius:4px;font:700 .9rem/1.3 system-ui,sans-serif}.button.secondary{background:transparent;color:var(--accent)}.button:hover{filter:brightness(.9)}
.cover{width:min(100%,370px);height:auto;aspect-ratio:5/8;object-fit:cover;display:block;margin:auto;box-shadow:18px 20px 0 #dfd9cc,0 12px 28px #20332c20}.cover-placeholder{background:var(--ink);color:var(--paper);padding:2rem;display:flex;flex-direction:column;justify-content:space-between}.cover-placeholder strong{font-size:clamp(1.6rem,4vw,2.7rem);line-height:1.05}.cover-placeholder span{font:600 .8rem system-ui,sans-serif;letter-spacing:.1em;text-transform:uppercase}
.section{border-top:1px solid var(--line)}.copy{max-width:var(--measure);font-size:1.12rem}.theme-list{list-style:none;padding:0;display:flex;gap:.65rem;flex-wrap:wrap}.theme-list li{border:1px solid var(--line);background:var(--card);border-radius:100px;padding:.45rem .85rem;font:.88rem system-ui,sans-serif}
.note{background:var(--card);border-left:3px solid var(--accent);padding:1.1rem 1.3rem;max-width:var(--measure)}.footer{padding:2rem 1.25rem;border-top:1px solid var(--line);font:.8rem/1.5 system-ui,sans-serif;color:var(--muted);text-align:center}
.reader-shell{max-width:800px;padding-top:2.5rem}.reader-shell h1{font-size:clamp(2.3rem,6vw,4rem)}.toc{list-style:none;padding:0}.toc li{border-bottom:1px solid var(--line)}.toc a{display:flex;justify-content:space-between;gap:1rem;padding:.9rem 0;text-decoration:none;color:var(--ink)}.toc a:hover{color:var(--accent)}.toc small{font:600 .75rem system-ui,sans-serif;color:var(--muted)}
.toolbar{display:flex;gap:.5rem;flex-wrap:wrap;padding:1rem 0;border-block:1px solid var(--line);font:600 .8rem system-ui,sans-serif}.toolbar button{border:1px solid var(--line);background:var(--card);color:var(--ink);padding:.45rem .7rem;cursor:pointer;border-radius:3px}.chapter{font-size:var(--reader-size,1.12rem);max-width:var(--measure);margin:2rem auto;line-height:1.85}.chapter h2{font-size:2.2em;margin:.3em 0 1em}.chapter h3{font-size:1.3em}.chapter p{text-align:left;margin:0 0 1em}.chapter blockquote{margin:1.5em 1em;color:var(--muted);font-style:italic}.chapter .scene{border:0;text-align:center;margin:2em 0}.chapter .scene:after{content:'• • •';letter-spacing:.5em;color:var(--accent)}.chapter-art{max-width:100%;height:auto;display:block;margin:1.5rem auto 2rem}.chapter-nav{display:flex;justify-content:space-between;gap:1rem;border-top:1px solid var(--line);padding-top:1.5rem;margin-top:3rem;font:600 .9rem system-ui,sans-serif}
.progress{position:fixed;top:0;left:0;height:3px;background:var(--accent);width:0;z-index:10}.page-dark{--ink:#e8e5d9;--paper:#1d2522;--card:#27312c;--line:#59625b;--accent:#e6a08b;--muted:#b9c3b9}
@media(max-width:700px){.hero{grid-template-columns:minmax(0,1fr);min-height:auto;padding-top:2rem}.hero .cover{width:min(75vw,260px)}.top-inner{align-items:flex-start;flex-direction:column}.reader-shell{padding-top:1rem}.chapter{line-height:1.75}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
"""

JS = """(()=>{const body=document.body;const saved=localStorage.getItem('editoria-theme');if(saved==='dark')body.classList.add('page-dark');let size=Number(localStorage.getItem('editoria-font')||1.12);const apply=()=>body.style.setProperty('--reader-size',size+'rem');apply();document.querySelector('[data-font-plus]')?.addEventListener('click',()=>{size=Math.min(1.7,size+.1);apply();localStorage.setItem('editoria-font',size)});document.querySelector('[data-font-minus]')?.addEventListener('click',()=>{size=Math.max(.9,size-.1);apply();localStorage.setItem('editoria-font',size)});document.querySelector('[data-theme]')?.addEventListener('click',()=>{body.classList.toggle('page-dark');localStorage.setItem('editoria-theme',body.classList.contains('page-dark')?'dark':'light')});const progress=document.querySelector('.progress');if(progress){const update=()=>{const max=document.documentElement.scrollHeight-innerHeight;progress.style.width=(max>0?Math.min(100,scrollY/max*100):100)+'%'};addEventListener('scroll',update,{passive:true});update()}})();"""


def _reset_output(root: Path, destination: Path) -> None:
    resolved = destination.resolve()
    allowed = (root / "dist").resolve()
    if resolved.parent != allowed or resolved.name not in {"revisao", "publico"}:
        raise ValueError(f"Recusa limpar saída inesperada: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)
    resolved.mkdir(parents=True)


def _html_document(title: str, description: str, content: str, *, canonical: str = "", robots: str = "index,follow", jsonld: dict | None = None, asset_prefix: str = "") -> str:
    meta = f'<link rel="canonical" href="{html.escape(canonical, quote=True)}">' if canonical else ""
    json_text = json.dumps(jsonld, ensure_ascii=False).replace("</", "<\\/") if jsonld else ""
    ld = f'<script type="application/ld+json">{json_text}</script>' if jsonld else ""
    return f'''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="{robots}"><meta name="description" content="{html.escape(description[:155], quote=True)}">
<meta property="og:type" content="book"><meta property="og:title" content="{html.escape(title, quote=True)}"><meta property="og:description" content="{html.escape(description[:155], quote=True)}">
<title>{html.escape(title)}</title>{meta}<link rel="stylesheet" href="{asset_prefix}style.css">{ld}</head>
<body><a class="skip" href="#principal">Pular para o conteúdo</a>{content}<script src="{asset_prefix}reader.js" defer></script></body></html>'''


def _top(title: str, in_chapter: bool = False, show_reader: bool = True) -> str:
    home = "../index.html" if in_chapter else "index.html"
    reader = "../ler.html" if in_chapter else "ler.html"
    reader_link = f'<a href="{reader}">Leitura</a>' if show_reader else ""
    return f'<header class="top"><div class="top-inner"><a class="brand" href="{home}">{html.escape(title)}</a><nav aria-label="Navegação principal"><a href="{home}">Sobre o livro</a>{reader_link}</nav></div></header>'


def _asset(project: Project, source: Path, destination: Path, name: str) -> str:
    suffix = source.suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise ValueError(f"Formato de imagem não aceito no site: {source.name}")
    assets = destination / "assets"
    assets.mkdir(exist_ok=True)
    target = assets / f"{name}{suffix}"
    shutil.copy2(source, target)
    return f"assets/{target.name}"


def _landing(project: Project, destination: Path, mode: str, count: int, private: bool) -> None:
    config = project.config
    site = config.get("site", {})
    title = project.title
    subtitle = str(config.get("subtitulo", ""))
    synopsis = str(config.get("sinopse", ""))
    themes = [str(item) for item in config.get("temas", [])]
    cover_html = f'<div class="cover cover-placeholder"><span>Romance</span><strong>{html.escape(title)}</strong><span>{html.escape(project.author)}</span></div>'
    cover_value = config.get("capa_ebook")
    if cover_value:
        cover = safe_relative_file(project.root, str(cover_value))
        if cover.is_file():
            relative = _asset(project, cover, destination, "capa")
            cover_html = f'<img class="cover" src="{relative}" alt="Capa de {html.escape(title, quote=True)}" width="500" height="800">'

    actions = []
    if count:
        label = "Ler o livro" if mode == "full" else "Ler a prévia"
        actions.append(f'<a class="button" href="ler.html">{label}</a>')
    buy_url = str(site.get("url_compra", "")).strip()
    if buy_url.startswith("https://"):
        actions.append(f'<a class="button secondary" href="{html.escape(buy_url, quote=True)}" rel="noopener">Comprar o livro</a>')
    if not actions:
        actions.append('<span class="note">Leitura e compra em preparação.</span>')
    theme_html = "".join(f"<li>{html.escape(value)}</li>" for value in themes)
    reader_note = (
        f"Os {count} capítulos disponíveis estão no leitor." if count == len(project.chapters) and count else
        f"Leia os {count} primeiros capítulos; a continuação depende dos canais de venda definidos pelo autor." if count else
        "A leitura ainda não está pública."
    )
    content = f'''{_top(title, show_reader=count > 0)}<main id="principal"><section class="hero"><div><p class="eyebrow">{html.escape(str(config.get("genero", "romance")))}</p>
<h1>{html.escape(title)}</h1><p class="lead">{html.escape(subtitle or synopsis)}</p><p>{html.escape(project.author)}</p>
<div class="actions">{"".join(actions)}</div></div><div class="cover-wrap">{cover_html}</div></section>
<section class="section" id="historia"><p class="eyebrow">A história</p><h2>Uma história para sentir e continuar</h2><p class="copy">{html.escape(synopsis)}</p></section>
<section class="section" id="temas"><p class="eyebrow">Por dentro do livro</p><h2>Temas que atravessam a história</h2><ul class="theme-list">{theme_html}</ul></section>
<section class="section"><p class="eyebrow">Como ler</p><h2>Escolha seu momento</h2><p class="copy">{html.escape(reader_note)}</p><div class="actions">{"".join(actions)}</div></section></main>
<footer class="footer">© {date.today().year} {html.escape(project.author)}. Obra de ficção.</footer>'''
    base = str(site.get("url", "")).strip().rstrip("/") + "/" if site.get("url") else ""
    graph = {"@context": "https://schema.org", "@type": "Book", "name": title, "author": {"@type": "Person", "name": project.author}, "inLanguage": project.language, "description": synopsis, "about": [{"@type": "Thing", "name": value} for value in themes]}
    if base:
        graph["url"] = base
    (destination / "index.html").write_text(_html_document(title, synopsis, content, canonical=base if not private else "", robots="noindex,nofollow" if private else "index,follow", jsonld=None if private else graph), encoding="utf-8")
    if base and not private:
        entries = [base] + ([urljoin(base, "ler.html")] if count else [])
        sitemap = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{html.escape(url)}</loc></url>" for url in entries) + "</urlset>"
        (destination / "sitemap.xml").write_text(sitemap, encoding="utf-8")
        (destination / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: " + urljoin(base, "sitemap.xml") + "\n", encoding="utf-8")
        (destination / "llms.txt").write_text(f"# {title}\n\n{synopsis}\n\nTemas: {', '.join(themes)}\nFonte canônica: {base}\n", encoding="utf-8")


def _reader(project: Project, destination: Path, chapters: tuple[Chapter, ...], mode: str, private: bool) -> None:
    title = project.title
    synopsis = str(project.config.get("sinopse", ""))
    items = "".join(f'<li><a href="capitulos/capitulo-{chapter.number:02d}.html"><span>{chapter.number:02d}. {html.escape(chapter.title)}</span><small>Ler capítulo</small></a></li>' for chapter in chapters)
    content = f'''{_top(title)}<main id="principal" class="reader-shell"><p class="eyebrow">Leitura online</p><h1>{html.escape(title)}</h1><p class="lead">{html.escape(synopsis)}</p><h2>Índice</h2><ol class="toc">{items}</ol></main><footer class="footer">{html.escape(project.author)} · {len(chapters)} capítulos disponíveis</footer>'''
    (destination / "ler.html").write_text(_html_document(f"Ler {title}", synopsis, content, robots="noindex,nofollow" if private else "index,follow"), encoding="utf-8")
    chapters_dir = destination / "capitulos"
    chapters_dir.mkdir(exist_ok=True)
    for index, chapter in enumerate(chapters):
        art = project.art_for(chapter.number)
        art_html = ""
        if art:
            source, alt = art
            relative = _asset(project, source, destination, f"arte-{chapter.number:02d}")
            art_html = f'<img class="chapter-art" src="../{relative}" alt="{html.escape(alt, quote=True)}" loading="lazy">'
        previous = f'<a href="capitulo-{chapters[index-1].number:02d}.html">← Capítulo anterior</a>' if index else '<a href="../ler.html">← Índice</a>'
        next_link = f'<a href="capitulo-{chapters[index+1].number:02d}.html">Próximo capítulo →</a>' if index + 1 < len(chapters) else ""
        if not next_link and mode == "preview":
            buy_url = str(project.config.get("site", {}).get("url_compra", ""))
            next_link = f'<a href="{html.escape(buy_url, quote=True)}" rel="noopener">Continuar na loja →</a>' if buy_url.startswith("https://") else '<span>Fim da prévia</span>'
        article = f'''<div class="progress" aria-hidden="true"></div>{_top(title, True)}<main id="principal" class="reader-shell">
<p class="eyebrow">Capítulo {chapter.number} de {len(project.chapters)}</p><h1>{html.escape(chapter.title)}</h1>
<div class="toolbar" role="group" aria-label="Preferências de leitura"><button type="button" data-font-minus aria-label="Diminuir texto">A−</button><button type="button" data-font-plus aria-label="Aumentar texto">A+</button><button type="button" data-theme>Alternar contraste</button></div>
<article class="chapter">{art_html}{render_html(chapter.body)}</article><nav class="chapter-nav" aria-label="Capítulos">{previous}{next_link}</nav></main>
<footer class="footer">{html.escape(project.author)} · <a href="../ler.html">Voltar ao índice</a></footer>'''
        (chapters_dir / f"capitulo-{chapter.number:02d}.html").write_text(_html_document(f"{chapter.title} — {title}", synopsis, article, robots="noindex,nofollow" if private else "index,follow", asset_prefix="../"), encoding="utf-8")


def write_site(project: Project, *, private: bool, allow_full: bool = False) -> Path:
    site = project.config.get("site", {})
    configured_mode = site.get("modo", "landing")
    mode = "full" if private else configured_mode
    if mode == "full" and not private and not allow_full:
        raise ValueError("Site público integral bloqueado. Use --permitir-publico-completo somente após decidir conscientemente.")
    count = len(project.chapters) if mode == "full" else int(site.get("capitulos_gratis", 0)) if mode == "preview" else 0
    destination = project.root / "dist" / ("revisao" if private else "publico")
    _reset_output(project.root, destination)
    (destination / "style.css").write_text(CSS, encoding="utf-8")
    (destination / "reader.js").write_text(JS, encoding="utf-8")
    _landing(project, destination, mode, count, private)
    if count:
        _reader(project, destination, project.chapters[:count], mode, private)
    return destination
