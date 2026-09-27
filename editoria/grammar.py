"""Revisão gramatical opt-in em servidor LanguageTool local.

Não envia manuscritos a serviços externos. Os achados são sugestões, não
correções automáticas: concordância e fala coloquial exigem contexto.
"""

from __future__ import annotations

import json
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen

from .audit import Issue
from .project import Project


def check_local_grammar(project: Project, endpoint: str) -> list[Issue]:
    parsed = urlsplit(endpoint)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"} or parsed.username or parsed.password:
        raise ValueError("A revisão gramatical aceita apenas um servidor HTTP local (localhost/127.0.0.1).")
    if not parsed.path.endswith("/v2/check"):
        raise ValueError("A URL local do LanguageTool deve terminar em /v2/check.")

    issues: list[Issue] = []
    for chapter in project.chapters:
        payload = urlencode({"language": project.language, "text": chapter.body}).encode("utf-8")
        request = Request(endpoint, data=payload, headers={"Content-Type": "application/x-www-form-urlencoded; charset=utf-8"}, method="POST")
        try:
            with urlopen(request, timeout=30) as response:
                data = json.load(response)
        except (OSError, ValueError) as exc:
            raise ValueError(f"LanguageTool local indisponível ao verificar o capítulo {chapter.number}: {exc}") from exc
        if not isinstance(data, dict) or not isinstance(data.get("matches"), list):
            raise ValueError(f"Resposta inválida do LanguageTool no capítulo {chapter.number}.")
        for match in data["matches"]:
            offset = int(match.get("offset", 0))
            length = int(match.get("length", 0))
            if offset < 0 or length < 0 or offset > len(chapter.body):
                continue
            excerpt = chapter.body[offset:offset + length].replace("\n", " ")[:65]
            rule = match.get("rule", {})
            rule_id = str(rule.get("id", "regra")) if isinstance(rule, dict) else "regra"
            suggestions = ", ".join(str(item.get("value", "")) for item in match.get("replacements", [])[:3] if isinstance(item, dict))
            message = str(match.get("message", "Verifique este trecho."))
            if suggestions:
                message += f" Sugestões: {suggestions}."
            issues.append(Issue("warning", "GRAMATICA", f"manuscrito/{chapter.path.name}:caractere-{offset + 1}", f"{rule_id}: {excerpt!r} — {message}"))
    return issues
