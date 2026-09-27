"""Interface em português, com saídas explícitas e sem publicação automática."""

from __future__ import annotations

import argparse
import json
import sys

from .audit import audit, has_errors
from .grammar import check_local_grammar
from .project import load_project
from .publication import counts, generate
from .starter import init_project


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="editoria", description="Planejamento, revisão e produção de livros")
    commands = root.add_subparsers(dest="comando", required=True)
    begin = commands.add_parser("iniciar", help="cria um livro novo, sem sobrescrever arquivos")
    begin.add_argument("destino")
    begin.add_argument("--titulo", required=True)
    begin.add_argument("--autor", required=True)

    verify = commands.add_parser("verificar", help="audita estrutura, metadados e sinais de revisão")
    verify.add_argument("projeto")
    verify.add_argument("--json", action="store_true", help="relatório legível por máquina")
    verify.add_argument("--languagetool-url", help="opcional: servidor gramatical local, por exemplo http://127.0.0.1:8081/v2/check")

    build = commands.add_parser("gerar", help="gera leitura, site e/ou materiais de publicação")
    build.add_argument("projeto")
    build.add_argument("--somente", choices=("leitura", "publico", "kdp", "tudo"), default="tudo")
    build.add_argument("--permitir-publico-completo", action="store_true", help="confirma conscientemente a exposição de todos os capítulos")
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.comando == "iniciar":
            created = init_project(args.destino, args.titulo, args.autor)
            print(f"Projeto criado: {created}\nPreencha livro.json e manuscrito/ antes de gerar.")
            return 0
        project = load_project(args.projeto)
        if args.comando == "verificar":
            issues = audit(project)
            if args.languagetool_url:
                issues.extend(check_local_grammar(project, args.languagetool_url))
            report = {**counts(project), "status": "ERROS" if has_errors(issues) else "OK_COM_AVISOS" if issues else "OK", "achados": [issue.to_dict() for issue in issues]}
            if args.json:
                print(json.dumps(report, ensure_ascii=False, indent=2))
            else:
                print(f"{report['status']}: {report['capitulos']} capítulos; {report['palavras_historia']} palavras de história.")
                for issue in issues:
                    print(f"[{issue.severity.upper()}] {issue.location}: {issue.message}")
                print("Concordância fina, emoção, cronologia implícita e plausibilidade exigem leitura humana (docs/REVISAO.md).")
            return 1 if has_errors(issues) else 0
        if args.comando == "gerar":
            report = generate(project, only=args.somente, allow_full=args.permitir_publico_completo)
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0
    except (FileNotFoundError, FileExistsError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 2
    return 2
