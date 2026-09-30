"""Cria um livro independente; nada da obra que inspirou a ferramenta é copiado."""

from __future__ import annotations

import json
import re
import unicodedata
from datetime import date
from pathlib import Path


def slug(value: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-") or "novo-livro"


def init_project(destination: str | Path, title: str, author: str) -> Path:
    root = Path(destination).resolve()
    if root.exists():
        if any(root.iterdir()):
            raise FileExistsError(f"Destino não está vazio: {root}")
    else:
        root.mkdir(parents=True)

    for directory in ("planejamento", "manuscrito", "memoria", "auditorias", "artes", "feedback"):
        (root / directory).mkdir(exist_ok=True)

    config = {
        "versao_esquema": 1,
        "id": slug(title),
        "titulo": title,
        "subtitulo": "",
        "autor": author,
        "idioma": "pt-BR",
        "ano_publicacao": date.today().year,
        "genero": "romance",
        "publico": "[PREENCHER: quem vai ler e o que espera sentir]",
        "tom": "[PREENCHER: voz, simplicidade e limites de linguagem]",
        "sinopse": "[PREENCHER: promessa sem entregar o final]",
        "temas": [],
        "capa_ebook": "",
        "artes": [],
        "site": {"modo": "landing", "capitulos_gratis": 0, "url_compra": ""},
    }
    (root / "livro.json").write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    files = {
        ".gitignore": "dist/\n__pycache__/\n.venv/\n.env\n",
        "AGENTS.md": """# Instruções editoriais deste livro

- Leia `livro.json` e `planejamento/` antes de alterar a história.
- Respeite a hierarquia: decisão explícita do autor, Bíblia, capítulos aprovados, cronologia, personagens, planejamento e sugestões da IA. Uma sugestão não é cânone.
- Confira `memoria/` antes de escrever. Segredos e eventos planejados não podem ser revelados antes do momento aprovado.
- Somente o autor marca um capítulo como `aprovado` em `planejamento/ESTADO.json`; após isso, registre a memória do capítulo.
- `manuscrito/` é a fonte; `dist/` é gerado. Nunca edite a saída gerada à mão.
- Preserve a voz, o público, os fatos canônicos e o fim planejado. Mudança grande de arco exige decisão do autor.
- Mostre uma questão narrativa com capítulo e trecho; separe erro objetivo de preferência de leitura.
- Use palavras comuns quando transmitirem a mesma ideia. Não deixe a prosa genérica ou sem emoção.
- Depois de editar, verifique cronologia, concordância, passagem entre capítulos e versões geradas.
- Não prometa perfeição, vendas ou aceitação de loja. Não publique, envie a terceiros ou faça push sem pedido expresso.
""",
        "planejamento/PREMISSA.md": """# Premissa e promessa

- Público: [PREENCHER]
- Dor ou desejo que abre a história: [PREENCHER]
- O que a protagonista quer no início: [PREENCHER]
- O que ela precisa aprender, sem virar lição de palestra: [PREENCHER]
- Conflito externo e custo da escolha: [PREENCHER]
- Final deste volume: [PREENCHER]
- Pergunta legítima que pode levar ao próximo volume: [PREENCHER ou não se aplica]
""",
        "planejamento/BIBLIA.md": """# Bíblia do livro

Fonte de verdade para identidade, universo e limites da obra. Registre apenas decisões aprovadas pelo autor; ideias abertas ficam em `PONTAS_ABERTAS.md` ou `ESTADO.json`.

## Identidade

- Gênero e subgênero: [PREENCHER]
- Público e tema: [PREENCHER]
- Narrador, ponto de vista e tempo verbal: [PREENCHER]
- Tom e regras de estilo: [PREENCHER]

## Universo

- Época e lugares centrais: [PREENCHER]
- Regras que não podem mudar: [PREENCHER]
- Limites de pesquisa factual: [PREENCHER]

## Estrutura

- Início, viradas, clímax e resolução: [PREENCHER]
- Elementos que devem ser evitados: [PREENCHER]
""",
        "planejamento/PERSONAGENS.md": """# Bíblia de personagens

Para cada personagem, registre nome, idade em cada fase, relações, trabalho, voz, desejo, medo, segredo, limites e mudança observável. Separe fatos canônicos de ideias ainda abertas.

## Protagonista

- Nome: [PREENCHER]
- Idade no início/fim: [PREENCHER]
- Desejo, necessidade e contradição: [PREENCHER]
- Gestos e frases que a tornam reconhecível: [PREENCHER]
""",
        "planejamento/CRONOLOGIA.md": """# Cronologia oficial

| Quando | Capítulo | Evento | Idades | Consequência |
| --- | --- | --- | --- | --- |
| [PREENCHER] | 1 | [PREENCHER] | [PREENCHER] | [PREENCHER] |

Registre aniversários, feriados, intervalo entre cenas, mudança de moradia, trabalho, escola, dinheiro e acordos importantes. Se o tempo é incerto de propósito, marque como incerto.
""",
        "planejamento/MAPA_CAPITULOS.md": """# Mapa de capítulos

| Cap. | Objetivo da personagem | Obstáculo | O que muda | Pergunta/impulso seguinte |
| --- | --- | --- | --- | --- |
| 1 | [PREENCHER] | [PREENCHER] | [PREENCHER] | [PREENCHER] |

Nem todo fim precisa de suspense. Uma escolha, uma consequência ou uma pergunta emocional concreta costuma bastar.
""",
        "planejamento/SEGREDOS.md": """# Segredos e revelações

| ID | Informação | Quem sabe | Quem ainda não sabe | Revelação ao leitor | Revelação aos personagens | Pistas aprovadas |
| --- | --- | --- | --- | --- | --- | --- |
| [PREENCHER] | [PREENCHER] | [PREENCHER] | [PREENCHER] | [PREENCHER] | [PREENCHER] | [PREENCHER] |

Separe fato confirmado, evento planejado e hipótese. Não antecipe uma revelação por inferência da IA.
""",
        "planejamento/OBJETOS.md": """# Objetos importantes

| Objeto | Origem | Proprietário/portador | Local atual | Primeira aparição | Mudanças registradas |
| --- | --- | --- | --- | --- | --- |
| [PREENCHER] | [PREENCHER] | [PREENCHER] | [PREENCHER] | [PREENCHER] | [PREENCHER] |
""",
        "planejamento/LOCAIS.md": """# Locais importantes

| Local | Características e regras | Distâncias/tempo | Eventos ocorridos | Mudanças aprovadas |
| --- | --- | --- | --- | --- |
| [PREENCHER] | [PREENCHER] | [PREENCHER] | [PREENCHER] | [PREENCHER] |
""",
        "planejamento/PONTAS_ABERTAS.md": """# Pontas abertas e hipóteses

| ID | Questão | Onde surgiu | Estado (confirmada/planejada/desconhecida/descartada) | Decisão do autor | Capítulo de resolução |
| --- | --- | --- | --- | --- | --- |
| [PREENCHER] | [PREENCHER] | [PREENCHER] | desconhecida | [PREENCHER] | [PREENCHER] |

Uma hipótese da IA não deve virar fato canônico sem aprovação do autor.
""",
        "planejamento/ESTADO.json": """{
  "capitulos": {"01": "rascunho"},
  "decisoes_pendentes": []
}
""",
        "planejamento/DIREITOS.md": """# Direitos, fontes e privacidade

| Material | Origem | Titular/licença | Permissão de uso | Comprovante |
| --- | --- | --- | --- | --- |
| Capa | [PREENCHER] | [PREENCHER] | [PREENCHER] | [PREENCHER] |

Não inclua relatos reais identificáveis de clientes/leitoras sem tratar privacidade e consentimento. Guarde documentos sensíveis fora de repositórios públicos.
""",
        "manuscrito/ABERTURA.md": """# Abertura

## Dedicatória

[PREENCHER ou remova esta seção]

## Nota à leitora

[PREENCHER: se necessária, breve e sem prometer fatos reais]
""",
        "manuscrito/CAP_01_PRIMEIRO_CAPITULO.md": """# CAPÍTULO 1
## [PREENCHER: título]

[PREENCHER: comece por uma cena concreta, com desejo ou problema presente.]

— [PREENCHER: um diálogo por linha.]
""",
        "manuscrito/AGRADECIMENTOS.md": """# Agradecimentos

[PREENCHER antes da publicação. Atribua colaboração com precisão.]
""",
        "manuscrito/SOBRE_AUTORIA.md": """# Sobre a autoria

[PREENCHER antes da publicação. Pseudônimo não deve receber biografia inventada apresentada como fato.]
""",
        "manuscrito/ULTIMA_PALAVRA.md": """# Uma última palavra

[PREENCHER ou remova este arquivo: convide com cuidado à indicação e a uma avaliação sincera. Não interrompa a última cena para pedir isso.]
""",
        "memoria/CAP_01.md": """# Memória do capítulo 1

Preencha após a aprovação do capítulo. Registre apenas fatos estabelecidos, com referências ao manuscrito.

- Eventos e consequências: [PREENCHER]
- Novos fatos de personagens, locais e objetos: [PREENCHER]
- Revelações e quem passou a saber: [PREENCHER]
- Segredos preservados e pontas abertas: [PREENCHER]
- Alterações na cronologia: [PREENCHER]
""",
        "auditorias/README.md": """# Auditorias do livro

Registre achados com capítulo, trecho, evidência, gravidade, proposta, impacto e decisão do autor. Não corrija silenciosamente contradições que mudem arco, personagem, segredo ou final.

Sugestão: revisão de continuidade a cada cinco capítulos aprovados e revisão ampla a cada dez. Consulte `docs/FLUXO_IA.md` na ferramenta Editoria.
""",
        "feedback/LEITORAS_BETA.md": """# Leitura beta

Registre versão/commit entregue e data. Para cada leitora, pergunte:

1. Em qual capítulo você quis continuar sem parar? Por quê?
2. Onde perdeu vontade de avançar ou precisou reler?
3. Alguma fala, idade, data, dinheiro ou atitude pareceu não fazer sentido?
4. O que pareceu explicado demais? O que ficou sem consequência?
5. O fim pareceu merecido? O que você espera do próximo volume, se houver?
6. Houve palavra ou frase que você não usaria numa conversa comum?

Não altere o livro por uma opinião isolada. Procure padrões e separe gosto de erro verificável.
""",
    }
    for relative, content in files.items():
        (root / relative).write_text(content, encoding="utf-8")
    return root
