"""Estrutura instalável do leitor; conteúdo do livro permanece somente na rede."""

from __future__ import annotations

import json
import re
from hashlib import sha256
from pathlib import Path

from PIL import Image, ImageDraw

from .project import Project


SHELL_FILES = (
    "./index.html",
    "./ler.html",
    "./offline.html",
    "./style.css",
    "./reader.js",
    "./manifest.webmanifest",
    "./assets/app-icon-180.png",
    "./assets/app-icon-192.png",
    "./assets/app-icon-512.png",
)


def _icon(size: int) -> Image.Image:
    image = Image.new("RGB", (1024, 1024), "#20332c")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((205, 205, 819, 819), radius=112, fill="#a44d39")
    draw.polygon(
        [(292, 335), (480, 377), (512, 408), (544, 377), (732, 335),
         (732, 700), (544, 680), (512, 705), (480, 680), (292, 700)],
        fill="#fff7e9",
    )
    draw.line([(512, 408), (512, 705)], fill="#a44d39", width=22)
    return image.resize((size, size), Image.Resampling.LANCZOS)


def write_pwa(project: Project, destination: Path) -> None:
    assets = destination / "assets"
    assets.mkdir(exist_ok=True)
    for size in (180, 192, 512):
        _icon(size).save(assets / f"app-icon-{size}.png", optimize=True)

    manifest = {
        "id": "./",
        "name": project.title,
        "short_name": project.title[:20],
        "description": str(project.config.get("sinopse", ""))[:155],
        "start_url": "./ler.html?retomar=1",
        "scope": "./",
        "display": "standalone",
        "background_color": "#f8f5ed",
        "theme_color": "#20332c",
        "lang": project.language,
        "icons": [
            {"src": f"assets/app-icon-{size}.png", "sizes": f"{size}x{size}", "type": "image/png", "purpose": "any maskable"}
            for size in (192, 512)
        ],
    }
    (destination / "manifest.webmanifest").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    cache_slug = re.sub(r"[^a-z0-9-]", "-", str(project.config.get("id", "livro")).lower())
    shell_version = sha256((destination / "reader.js").read_bytes() + (destination / "style.css").read_bytes()).hexdigest()[:12]
    shell = json.dumps(SHELL_FILES, ensure_ascii=False)
    worker = f'''const CACHE_NAME = 'editoria-shell-{cache_slug}-{shell_version}';
const SHELL_FILES = {shell};
const ROOT = self.registration.scope;
const homeURL = new URL('./index.html', ROOT);
const readerURL = new URL('./ler.html', ROOT);
const offlineURL = new URL('./offline.html', ROOT);
const pagePaths = new Set([new URL('./', ROOT).pathname, homeURL.pathname, readerURL.pathname]);
const shellPaths = new Set(SHELL_FILES.slice(2).map(path => new URL(path, ROOT).pathname));

self.addEventListener('install', event => {{
  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(SHELL_FILES)).then(() => self.skipWaiting()));
}});

self.addEventListener('activate', event => {{
  event.waitUntil(caches.keys().then(names => Promise.all(names.filter(name => name.startsWith('editoria-shell-{cache_slug}-') && name !== CACHE_NAME).map(name => caches.delete(name)))).then(() => self.clients.claim()));
}});

self.addEventListener('fetch', event => {{
  const request = event.request;
  const url = new URL(request.url);
  if (request.method !== 'GET' || url.origin !== self.location.origin) return;
  if (request.mode === 'navigate' && pagePaths.has(url.pathname)) {{
    const key = url.pathname === readerURL.pathname ? readerURL : homeURL;
    event.respondWith((async () => {{
      try {{
        const response = await fetch(request);
        if (response.ok) await (await caches.open(CACHE_NAME)).put(key, response.clone());
        return response;
      }} catch (_) {{
        return (await caches.match(key)) || (await caches.match(offlineURL)) || Response.error();
      }}
    }})());
    return;
  }}
  if (request.mode === 'navigate') {{
    event.respondWith(fetch(request).catch(() => caches.match(offlineURL)));
    return;
  }}
  if (shellPaths.has(url.pathname)) {{
    event.respondWith((async () => {{
      try {{
        const response = await fetch(request);
        if (response.ok) await (await caches.open(CACHE_NAME)).put(request, response.clone());
        return response;
      }} catch (_) {{
        return (await caches.match(request)) || Response.error();
      }}
    }})());
  }}
}});
'''
    (destination / "sw.js").write_text(worker, encoding="utf-8")
