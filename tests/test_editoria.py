from __future__ import annotations

import json
import io
import tempfile
import unittest
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from unittest.mock import patch

from PIL import Image
from pypdf import PdfReader

from editoria.audit import audit, has_errors
from editoria.grammar import check_local_grammar
from editoria.markdown import blocks, render_html
from editoria.project import load_project
from editoria.publication import generate
from editoria.starter import init_project


class LocalLinks(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.targets: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        for key in ("href", "src"):
            if values.get(key):
                self.targets.append(values[key])


class EditorialProjectTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="editoria-test-")
        self.root = Path(self.temporary.name) / "livro"
        init_project(self.root, "Uma Casa Nova", "Nome Literário")
        config = json.loads((self.root / "livro.json").read_text(encoding="utf-8"))
        config.update({
            "publico": "Leitoras adultas que gostam de romances diretos e emocionantes",
            "tom": "Claro, próximo e sem palestra",
            "sinopse": "Uma mulher precisa decidir se reconstrói uma casa ou a vida que queria ter nela.",
            "temas": ["Recomeço", "Família", "Escolhas"],
            "capa_ebook": "artes/capa.png",
            "artes": [{"capitulo": 1, "arquivo": "artes/cap-01.png", "descricao": "Uma casa ao amanhecer."}],
            "site": {"modo": "preview", "capitulos_gratis": 1, "url_compra": "", "url": "https://exemplo.github.io/livro/"},
        })
        (self.root / "livro.json").write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
        Image.new("RGB", (1200, 1800), (31, 51, 44)).save(self.root / "artes" / "capa.png")
        Image.new("RGB", (1200, 800), (175, 106, 79)).save(self.root / "artes" / "cap-01.png")
        (self.root / "manuscrito" / "ABERTURA.md").write_text("# Abertura\n\n## Dedicatória\n\nÀs leitoras que recomeçam.\n", encoding="utf-8")
        (self.root / "manuscrito" / "AGRADECIMENTOS.md").write_text("# Agradecimentos\n\nÀ equipe de leitura.\n", encoding="utf-8")
        (self.root / "manuscrito" / "SOBRE_AUTORIA.md").write_text("# Sobre a autoria\n\nNome Literário escreve ficção.\n", encoding="utf-8")
        (self.root / "manuscrito" / "CAP_01_PRIMEIRO_CAPITULO.md").write_text(
            "# CAPÍTULO 1\n## A Chave\n\nAna encontrou uma chave na mesa.\n\n— Você sabe de quem é?\n\n— Ainda não.\n\n---\n\nEla abriu a porta e viu a casa vazia.\n",
            encoding="utf-8",
        )
        (self.root / "manuscrito" / "CAP_02_A_ESCOLHA.md").write_text(
            "# CAPÍTULO 2\n## A Escolha\n\nAna precisou escolher o que levar. Ela guardou a fotografia e saiu.\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_audit_and_build_keep_public_preview_separate(self) -> None:
        project = load_project(self.root)
        self.assertFalse(has_errors(audit(project)))
        report = generate(project)
        self.assertEqual(report["capitulos"], 2)
        self.assertGreater(report["paginas_miolo"], 3)
        self.assertEqual(len(PdfReader(str(self.root / "dist" / "kdp" / "miolo-5.5x8.5.pdf")).pages), report["paginas_miolo"])
        self.assertTrue((self.root / "dist" / "revisao" / "capitulos" / "capitulo-02.html").is_file())
        self.assertTrue((self.root / "dist" / "publico" / "capitulos" / "capitulo-01.html").is_file())
        self.assertFalse((self.root / "dist" / "publico" / "capitulos" / "capitulo-02.html").exists())
        self.assertFalse((self.root / "dist" / "publico" / "manuscrito_integral.md").exists())
        self.assertTrue((self.root / "dist" / "publico" / "sitemap.xml").is_file())
        epub = self.root / "dist" / "kdp" / "uma-casa-nova.epub"
        with zipfile.ZipFile(epub) as archive:
            self.assertEqual(archive.namelist()[0], "mimetype")
            self.assertIn("OEBPS/nav.xhtml", archive.namelist())
            self.assertIn("OEBPS/chapters/chapter-002.xhtml", archive.namelist())
        self.assertTrue((self.root / "dist" / "kdp" / "materiais-publicacao.zip").is_file())

    def test_public_full_requires_explicit_choice(self) -> None:
        config_file = self.root / "livro.json"
        config = json.loads(config_file.read_text(encoding="utf-8"))
        config["site"]["modo"] = "full"
        config_file.write_text(json.dumps(config, ensure_ascii=False), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "bloqueado"):
            generate(load_project(self.root), only="publico")
        report = generate(load_project(self.root), only="publico", allow_full=True)
        self.assertIn("publico", report["saidas"])
        self.assertTrue((self.root / "dist" / "publico" / "capitulos" / "capitulo-02.html").is_file())

    def test_public_mode_switch_removes_old_chapters(self) -> None:
        generate(load_project(self.root), only="publico")
        self.assertTrue((self.root / "dist" / "publico" / "capitulos" / "capitulo-01.html").is_file())
        config_file = self.root / "livro.json"
        config = json.loads(config_file.read_text(encoding="utf-8"))
        config["site"]["modo"] = "landing"
        config_file.write_text(json.dumps(config, ensure_ascii=False), encoding="utf-8")
        generate(load_project(self.root), only="publico")
        self.assertFalse((self.root / "dist" / "publico" / "capitulos").exists())

    def test_all_generated_local_links_exist(self) -> None:
        generate(load_project(self.root), only="tudo")
        for site in (self.root / "dist" / "publico", self.root / "dist" / "revisao"):
            for page in site.rglob("*.html"):
                parser = LocalLinks()
                parser.feed(page.read_text(encoding="utf-8"))
                for target in parser.targets:
                    parts = urlsplit(target)
                    if parts.scheme or target.startswith("#"):
                        continue
                    self.assertTrue((page.parent / parts.path).is_file(), f"Link quebrado em {page}: {target}")

    def test_local_grammar_is_opt_in_and_reports_location(self) -> None:
        with self.assertRaisesRegex(ValueError, "apenas um servidor HTTP local"):
            check_local_grammar(load_project(self.root), "https://servico-externo.test/v2/check")
        response = {"matches": [{"offset": 0, "length": 3, "message": "Concordância suspeita", "rule": {"id": "CONCORDANCIA"}, "replacements": [{"value": "As"}]}]}
        with patch("editoria.grammar.urlopen", side_effect=lambda *args, **kwargs: io.BytesIO(json.dumps(response).encode("utf-8"))) as opener:
            issues = check_local_grammar(load_project(self.root), "http://127.0.0.1:8081/v2/check")
        self.assertEqual(len(issues), 2)
        self.assertEqual(issues[0].code, "GRAMATICA")
        self.assertIn("caractere-1", issues[0].location)
        self.assertEqual(opener.call_count, 2)

    def test_landing_has_no_broken_reader_link(self) -> None:
        config_file = self.root / "livro.json"
        config = json.loads(config_file.read_text(encoding="utf-8"))
        config["site"]["modo"] = "landing"
        config_file.write_text(json.dumps(config, ensure_ascii=False), encoding="utf-8")
        generate(load_project(self.root), only="publico")
        public = self.root / "dist" / "publico"
        self.assertFalse((public / "ler.html").exists())
        self.assertNotIn('href="ler.html"', (public / "index.html").read_text(encoding="utf-8"))

    def test_markdown_preserves_dialogue_and_escapes_html(self) -> None:
        source = "Uma cena.\n— Fala um.\n— Fala dois.\n\nTexto com <tag> e **negrito**."
        self.assertEqual([block.kind for block in blocks(source)], ["paragraph"] * 4)
        result = render_html(source)
        self.assertIn("<p>— Fala um.</p>\n<p>— Fala dois.</p>", result)
        self.assertIn("&lt;tag&gt;", result)
        self.assertIn("<strong>negrito</strong>", result)

    def test_audit_rejects_missing_chapter_and_placeholders(self) -> None:
        (self.root / "manuscrito" / "CAP_01_PRIMEIRO_CAPITULO.md").unlink()
        (self.root / "manuscrito" / "CAP_02_A_ESCOLHA.md").write_text("# CAPÍTULO 2\n## [PREENCHER]\n\nTODO\n", encoding="utf-8")
        issues = audit(load_project(self.root))
        self.assertTrue(has_errors(issues))
        self.assertIn("SEQUENCIA", {issue.code for issue in issues})
        self.assertIn("RASCUNHO", {issue.code for issue in issues})


if __name__ == "__main__":
    unittest.main()
