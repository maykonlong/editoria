"""Site estático acessível: saída pública separada da revisão privada."""

from __future__ import annotations

import html
import json
import re
import shutil
from datetime import date
from pathlib import Path
from urllib.parse import urljoin

from .markdown import render_html
from .pwa import write_pwa
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
.front-cover{width:min(100%,280px);height:auto;display:block;margin:1.5rem auto 2.5rem;box-shadow:0 14px 35px #20332c26}.opening{max-width:var(--measure);margin:2rem auto 3rem;padding-bottom:2rem;border-bottom:1px solid var(--line)}.opening h2{font-size:1.7rem}.reader-actions{margin:1.5rem 0 2rem}.offline-message{max-width:var(--measure)}[hidden]{display:none!important}
@media(max-width:700px){.hero{grid-template-columns:minmax(0,1fr);min-height:auto;padding-top:2rem}.hero .cover{width:min(75vw,260px)}.top-inner{align-items:flex-start;flex-direction:column}.reader-shell{padding-top:1rem}.chapter{line-height:1.75}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
"""

JS = r"""(() => {
  const body = document.body;
  const root = body.dataset.root || './';
  const bookId = body.dataset.bookId || 'livro';
  const maxChapter = Number(body.dataset.maxChapter || 0);
  const chapter = Number(body.dataset.chapter || 0);
  const progressKey = `editoria-progresso-${bookId}`;
  const params = new URLSearchParams(location.search);
  let storage = null;
  try { storage = localStorage; } catch (_) { /* Leitura continua sem armazenamento. */ }
  const get = key => { try { return storage?.getItem(key); } catch (_) { return null; } };
  const set = (key, value) => { try { storage?.setItem(key, value); } catch (_) { /* Opcional. */ } };
  const savedTheme = get('editoria-theme');
  if (savedTheme === 'dark') body.classList.add('page-dark');
  let size = Number(get('editoria-font') || 1.12);
  if (!Number.isFinite(size) || size < .9 || size > 1.7) size = 1.12;
  const applyFont = () => body.style.setProperty('--reader-size', `${size}rem`);
  applyFont();
  document.querySelector('[data-font-plus]')?.addEventListener('click', () => {
    size = Math.min(1.7, +(size + .1).toFixed(2)); applyFont(); set('editoria-font', String(size));
  });
  document.querySelector('[data-font-minus]')?.addEventListener('click', () => {
    size = Math.max(.9, +(size - .1).toFixed(2)); applyFont(); set('editoria-font', String(size));
  });
  document.querySelector('[data-theme]')?.addEventListener('click', () => {
    body.classList.toggle('page-dark');
    set('editoria-theme', body.classList.contains('page-dark') ? 'dark' : 'light');
  });

  let saved = null;
  try {
    const value = JSON.parse(get(progressKey) || 'null');
    if (value && Number.isInteger(value.chapter) && value.chapter >= 1 && value.chapter <= maxChapter &&
        Number.isFinite(value.y) && value.y >= 0) saved = value;
  } catch (_) { /* Progresso antigo inválido. */ }
  const chapterURL = number => `${root}capitulos/capitulo-${String(number).padStart(2, '0')}.html`;
  document.querySelectorAll('[data-continue-reading]').forEach(link => {
    if (!saved) return;
    link.href = chapterURL(saved.chapter);
    link.hidden = false;
  });
  if (saved) document.querySelectorAll('[data-start-reading]').forEach(link => {
    link.textContent = 'Recomeçar da capa';
  });

  if (!chapter && params.has('retomar') && saved) {
    location.replace(chapterURL(saved.chapter));
    return;
  }
  if (params.has('inicio')) {
    history.replaceState(null, '', location.pathname + location.hash);
    if (chapter) scrollTo(0, 0);
  }
  if (chapter) {
    const bar = document.querySelector('.progress');
    const updateBar = () => {
      if (!bar) return;
      const maximum = document.documentElement.scrollHeight - innerHeight;
      bar.style.width = `${maximum > 0 ? Math.min(100, scrollY / maximum * 100) : 100}%`;
    };
    let timer = 0;
    const saveProgress = () => {
      set(progressKey, JSON.stringify({chapter, y: Math.max(0, Math.round(scrollY))}));
      updateBar();
    };
    addEventListener('scroll', () => {
      updateBar();
      clearTimeout(timer);
      timer = setTimeout(saveProgress, 180);
    }, {passive: true});
    addEventListener('pagehide', saveProgress);
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden') saveProgress();
    });
    if (saved?.chapter === chapter && !params.has('inicio') && !location.hash) {
      if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
      addEventListener('load', () => {
        scrollTo(0, Math.min(saved.y, document.documentElement.scrollHeight - innerHeight));
        updateBar();
      }, {once: true});
    } else {
      addEventListener('load', saveProgress, {once: true});
    }
    updateBar();
  }

  if ('serviceWorker' in navigator && document.querySelector('link[rel="manifest"]')) {
    addEventListener('load', () => navigator.serviceWorker.register(`${root}sw.js`).catch(() => {}));
  }
  const installButton = document.querySelector('[data-install-app]');
  let installPrompt = null;
  addEventListener('beforeinstallprompt', event => {
    event.preventDefault(); installPrompt = event;
    if (installButton) installButton.hidden = false;
  });
  installButton?.addEventListener('click', async () => {
    if (!installPrompt) return;
    installPrompt.prompt();
    await installPrompt.userChoice;
    installPrompt = null;
    installButton.hidden = true;
  });
  if (body.dataset.retirePwa === 'true') {
    const scope = new URL(root, location.href).href;
    navigator.serviceWorker?.getRegistrations().then(registrations => {
      registrations.filter(registration => registration.scope === scope).forEach(registration => registration.unregister());
    }).catch(() => {});
    const cacheSlug = bookId.toLowerCase().replace(/[^a-z0-9-]/g, '-');
    window.caches?.keys().then(names => Promise.all(names.filter(name =>
      name.startsWith(`editoria-shell-${cacheSlug}-`)).map(name => caches.delete(name)))).catch(() => {});
  }
})();"""


def _reset_output(root: Path, destination: Path) -> None:
    resolved = destination.resolve()
    allowed = (root / "dist").resolve()
    if resolved.parent != allowed or resolved.name not in {"revisao", "publico"}:
        raise ValueError(f"Recusa limpar saída inesperada: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)
    resolved.mkdir(parents=True)


def _html_document(title: str, description: str, content: str, *, canonical: str = "", robots: str = "index,follow", jsonld: dict | None = None, asset_prefix: str = "", pwa: bool = False, body_attrs: str = "") -> str:
    meta = f'<link rel="canonical" href="{html.escape(canonical, quote=True)}">' if canonical else ""
    json_text = json.dumps(jsonld, ensure_ascii=False).replace("</", "<\\/") if jsonld else ""
    ld = f'<script type="application/ld+json">{json_text}</script>' if jsonld else ""
    app_meta = f'<link rel="manifest" href="{asset_prefix}manifest.webmanifest"><link rel="apple-touch-icon" href="{asset_prefix}assets/app-icon-180.png"><meta name="theme-color" content="#20332c">' if pwa else ""
    return f'''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="{robots}"><meta name="description" content="{html.escape(description[:155], quote=True)}">
<meta property="og:type" content="book"><meta property="og:title" content="{html.escape(title, quote=True)}"><meta property="og:description" content="{html.escape(description[:155], quote=True)}">
<title>{html.escape(title)}</title>{meta}{app_meta}<link rel="stylesheet" href="{asset_prefix}style.css">{ld}</head>
<body {body_attrs}><a class="skip" href="#principal">Pular para o conteúdo</a>{content}<script src="{asset_prefix}reader.js" defer></script></body></html>'''


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
        actions.append(f'<a class="button" data-start-reading href="ler.html?inicio=1">{label}</a>')
        actions.append('<a class="button secondary" data-continue-reading href="ler.html?retomar=1" hidden>Continuar de onde parei</a>')
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
    install = '<button class="button secondary" type="button" data-install-app hidden>Adicionar à tela inicial</button>' if count and not private else ""
    content = f'''{_top(title, show_reader=count > 0)}<main id="principal"><section class="hero"><div><p class="eyebrow">{html.escape(str(config.get("genero", "romance")))}</p>
<h1>{html.escape(title)}</h1><p class="lead">{html.escape(subtitle or synopsis)}</p><p>{html.escape(project.author)}</p>
<div class="actions">{"".join(actions)}</div></div><div class="cover-wrap">{cover_html}</div></section>
<section class="section" id="historia"><p class="eyebrow">A história</p><h2>Uma história para sentir e continuar</h2><p class="copy">{html.escape(synopsis)}</p></section>
<section class="section" id="temas"><p class="eyebrow">Por dentro do livro</p><h2>Temas que atravessam a história</h2><ul class="theme-list">{theme_html}</ul></section>
<section class="section"><p class="eyebrow">Como ler</p><h2>Escolha seu momento</h2><p class="copy">{html.escape(reader_note)}</p><p class="copy">Neste aparelho, o leitor lembra seu capítulo e ponto de leitura. A história não fica guardada para leitura offline.</p><div class="actions">{"".join(actions)}{install}</div></section></main>
<footer class="footer">© {date.today().year} {html.escape(project.author)}. Obra de ficção.</footer>'''
    base = str(site.get("url", "")).strip().rstrip("/") + "/" if site.get("url") else ""
    graph = {"@context": "https://schema.org", "@type": "Book", "name": title, "author": {"@type": "Person", "name": project.author}, "inLanguage": project.language, "description": synopsis, "about": [{"@type": "Thing", "name": value} for value in themes]}
    if base:
        graph["url"] = base
    retire = ' data-retire-pwa="true"' if not private and not count else ""
    body_attrs = f'data-book-id="{html.escape(str(config.get("id", "livro")), quote=True)}" data-max-chapter="{count}" data-root="./"{retire}'
    (destination / "index.html").write_text(_html_document(title, synopsis, content, canonical=base if not private else "", robots="noindex,nofollow" if private else "index,follow", jsonld=None if private else graph, pwa=count > 0 and not private, body_attrs=body_attrs), encoding="utf-8")
    if base and not private:
        entries = [base] + ([urljoin(base, "ler.html")] if count else [])
        sitemap = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{html.escape(url)}</loc></url>" for url in entries) + "</urlset>"
        (destination / "sitemap.xml").write_text(sitemap, encoding="utf-8")
        (destination / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: " + urljoin(base, "sitemap.xml") + "\n", encoding="utf-8")
        (destination / "llms.txt").write_text(f"# {title}\n\n{synopsis}\n\nTemas: {', '.join(themes)}\nFonte canônica: {base}\n", encoding="utf-8")


def _reader(project: Project, destination: Path, chapters: tuple[Chapter, ...], mode: str, private: bool) -> None:
    title = project.title
    synopsis = str(project.config.get("sinopse", ""))
    items = "".join(f'<li><a href="capitulos/capitulo-{chapter.number:02d}.html?inicio=1"><span>{chapter.number:02d}. {html.escape(chapter.title)}</span><small>Ler capítulo</small></a></li>' for chapter in chapters)
    cover_html = ""
    cover_value = project.config.get("capa_ebook")
    if cover_value:
        cover = safe_relative_file(project.root, str(cover_value))
        if cover.is_file():
            relative = _asset(project, cover, destination, "capa")
            cover_html = f'<img class="front-cover" src="{relative}" alt="Capa de {html.escape(title, quote=True)}" width="500" height="800">'
    if not cover_html:
        cover_html = f'<div class="cover cover-placeholder" role="img" aria-label="Capa de {html.escape(title, quote=True)}"><span>Romance</span><strong>{html.escape(title)}</strong><span>{html.escape(project.author)}</span></div>'
    opening = re.sub(r"\A\s*#\s+[^\n]+\n", "", project.source("ABERTURA.md"), count=1).strip()
    opening_html = f'<section class="opening" aria-label="Antes da história">{render_html(opening)}</section>' if opening else ""
    first_link = f'<a class="button" href="capitulos/capitulo-{chapters[0].number:02d}.html?inicio=1">Começar o capítulo 1</a>'
    content = f'''{_top(title)}<main id="principal" class="reader-shell"><p class="eyebrow">Leitura online</p>{cover_html}<h1>{html.escape(title)}</h1><p>{html.escape(project.author)}</p>{opening_html}
<div class="actions reader-actions"><a class="button secondary" data-continue-reading href="capitulos/capitulo-{chapters[0].number:02d}.html" hidden>Continuar de onde parei</a>{first_link}</div>
<h2>Índice</h2><ol class="toc">{items}</ol></main><footer class="footer">{html.escape(project.author)} · {len(chapters)} capítulos disponíveis</footer>'''
    body_attrs = f'data-book-id="{html.escape(str(project.config.get("id", "livro")), quote=True)}" data-max-chapter="{len(chapters)}" data-root="./"'
    (destination / "ler.html").write_text(_html_document(f"Ler {title}", synopsis, content, robots="noindex,nofollow" if private else "index,follow", pwa=not private, body_attrs=body_attrs), encoding="utf-8")
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
        if not next_link and mode == "full" and (project.source("AGRADECIMENTOS.md") or project.source("SOBRE_AUTORIA.md")):
            next_link = '<a href="../pos-texto.html">Depois da história →</a>'
        elif not next_link and mode == "full" and project.source("ULTIMA_PALAVRA.md"):
            next_link = '<a href="../ultima-palavra.html">Uma última palavra →</a>'
        article = f'''<div class="progress" aria-hidden="true"></div>{_top(title, True)}<main id="principal" class="reader-shell">
<p class="eyebrow">Capítulo {chapter.number} de {len(project.chapters)}</p><h1>{html.escape(chapter.title)}</h1>
<div class="toolbar" role="group" aria-label="Preferências de leitura"><button type="button" data-font-minus aria-label="Diminuir texto">A−</button><button type="button" data-font-plus aria-label="Aumentar texto">A+</button><button type="button" data-theme>Alternar contraste</button></div>
<article class="chapter">{art_html}{render_html(chapter.body)}</article><nav class="chapter-nav" aria-label="Capítulos">{previous}{next_link}</nav></main>
<footer class="footer">{html.escape(project.author)} · <a href="../ler.html">Voltar ao índice</a></footer>'''
        body_attrs = f'data-book-id="{html.escape(str(project.config.get("id", "livro")), quote=True)}" data-max-chapter="{len(chapters)}" data-chapter="{chapter.number}" data-root="../"'
        (chapters_dir / f"capitulo-{chapter.number:02d}.html").write_text(_html_document(f"{chapter.title} — {title}", synopsis, article, robots="noindex,nofollow" if private else "index,follow", asset_prefix="../", pwa=not private, body_attrs=body_attrs), encoding="utf-8")

    if mode == "full":
        back = [project.source(name).strip() for name in ("AGRADECIMENTOS.md", "SOBRE_AUTORIA.md")]
        back = [part for part in back if part]
        final = project.source("ULTIMA_PALAVRA.md").strip()
        if back:
            following = '<a class="button" href="ultima-palavra.html">Uma última palavra →</a>' if final else ""
            back_content = f'{_top(title)}<main id="principal" class="reader-shell"><article class="chapter">{"".join(render_html(part) for part in back)}</article>{following}</main>'
            (destination / "pos-texto.html").write_text(_html_document(f"Depois da história — {title}", synopsis, back_content, robots="noindex,nofollow" if private else "index,follow", pwa=not private), encoding="utf-8")
        if final:
            final_content = f'{_top(title)}<main id="principal" class="reader-shell"><article class="chapter">{render_html(final)}</article><a class="button secondary" href="index.html">Voltar ao livro</a></main>'
            (destination / "ultima-palavra.html").write_text(_html_document(f"Uma última palavra — {title}", synopsis, final_content, robots="noindex,nofollow" if private else "index,follow", pwa=not private), encoding="utf-8")


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
        if not private:
            offline_content = f'{_top(project.title)}<main id="principal" class="reader-shell offline-message"><h1>Sem conexão</h1><p>O leitor pode abrir, mas os capítulos precisam de internet. Quando a conexão voltar, toque em “Continuar de onde parei”.</p><a class="button" href="ler.html?retomar=1">Tentar novamente</a></main>'
            (destination / "offline.html").write_text(_html_document(f"Sem conexão — {project.title}", "Esta leitura precisa de conexão à internet.", offline_content, robots="noindex,nofollow"), encoding="utf-8")
            write_pwa(project, destination)
    return destination
