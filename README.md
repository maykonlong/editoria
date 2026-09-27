# Editoria

Uma base reutilizável para planejar, escrever, revisar e preparar **novos livros** com ajuda de IA e decisão editorial humana. Nasceu de um processo real de produção editorial, mas não contém o manuscrito, personagens, artes nem a identidade visual de qualquer obra.

O objetivo é manter quatro coisas em acordo: **história**, **experiência de leitura**, **site** e **arquivos de publicação**. O programa detecta problemas verificáveis; os roteiros de revisão ajudam pessoas e IAs a discutir ritmo, emoção e clareza sem chamar opinião de erro.

## Comece em cinco minutos

```bash
python -m pip install -e .
editoria iniciar meu-romance --titulo "Meu Romance" --autor "Nome Literário"
editoria verificar meu-romance
editoria gerar meu-romance
```

Também funciona sem instalação: `python -m editoria iniciar ...`.

O primeiro comando cria um projeto separado. Preencha `livro.json`, `planejamento/` e `manuscrito/`; mantenha nomes sequenciais como `CAP_01_NOME.md`. Depois:

```bash
editoria verificar meu-romance --json
editoria gerar meu-romance --somente leitura
editoria gerar meu-romance --somente tudo
```

`gerar` escreve somente dentro de `dist/` do projeto: `dist/revisao/` para leitura privada, `dist/publico/` para o site e `dist/kdp/` para EPUB e miolo PDF. `dist/` fica fora do Git por padrão. A pasta pública contém **apenas a landing page** até que você configure uma prévia; o livro completo nunca é enviado ao site por padrão. Consulte [PUBLICACAO.md](docs/PUBLICACAO.md) antes de expor capítulos ou entrar em programas de exclusividade digital.

Para colocar a apresentação ou a prévia no GitHub Pages, siga [GITHUB_PAGES.md](docs/GITHUB_PAGES.md). Há um [workflow de exemplo](exemplos/pages.yml) para o repositório de cada livro; este repositório é a ferramenta e não hospeda um livro.

## Como o fluxo funciona

| Etapa | O que fazer | O que a ferramenta confere |
| --- | --- | --- |
| Ideia | promessa, público, tema, limite de cada volume | campos básicos do projeto |
| Arquitetura | personagens, linha do tempo, mapa de capítulos | capítulos ausentes/fora de ordem |
| Escrita | cenas com ação, escolha e consequência | arquivos, títulos e marcadores de rascunho |
| Revisões | continuidade, ritmo, voz, linguagem simples | termos sinalizados e frases longas repetidas |
| Leitoras beta | anotar onde avançam, param e se confundem | formulário e registro de decisões |
| Produção | arte, abertura, sumário, EPUB, PDF e site | metadados, artes e saídas sincronizadas |
| Lançamento | prova digital/física, links reais e direitos | checklist humano, não aprovação automática |

Os [13 roteiros de revisão](docs/REVISAO.md) e os [prompts para IA](prompts/README.md) são independentes do gênero. A ferramenta **não garante best-seller, ausência absoluta de erros, elegibilidade no KDP ou qualidade literária**. Ela deixa os pontos verificáveis explícitos e registra o que precisa de julgamento humano.

As [métricas editoriais](docs/METRICAS.md) explicam exatamente o que as contagens incluem e como usá-las sem forçar capítulos a um tamanho artificial.

## Estrutura de um livro

```text
meu-romance/
  livro.json                 metadados, público, site e artes
  planejamento/              premissa, personagens, cronologia, mapa
  manuscrito/                abertura, capítulos, agradecimentos, autora
  artes/                     capa e ilustrações próprias ou licenciadas
  feedback/                  retorno de leitoras e decisões
  dist/                      gerado; não versionar nem publicar inteiro
```

Cada capítulo usa:

```markdown
# CAPÍTULO 1
## O título do capítulo

Texto em parágrafos. Falas começam com travessão.

— Um diálogo por linha.

---

Uma mudança de cena.
```

O conversor aceita parágrafos, ênfase `*assim*`, negrito `**assim**`, listas e quebras de cena. Não aceita HTML arbitrário dentro do manuscrito; isso evita divergências entre web, EPUB e PDF. O arquivo `livro.json` pode associar ilustrações a capítulos, sempre com descrição alternativa.

## Verificação e publicação

`editoria verificar` produz diagnósticos com severidade e localização. Ele **não reescreve automaticamente a história**. `editoria gerar` recusa campos obrigatórios vazios e marcadores de rascunho. O EPUB tem sumário navegável; o PDF tem página de rosto, créditos, índice e paginação. A capa completa do impresso **não é gerada automaticamente**: depende da arte final, formato, papel, número final de páginas e especificações atuais da gráfica/KDP.

Para uma checagem adicional de ortografia e concordância, é possível apontar um **LanguageTool instalado e executado localmente**: `editoria verificar meu-romance --languagetool-url http://127.0.0.1:8081/v2/check`. Sem essa opção, nenhum texto sai do computador. Os resultados são avisos para conferência contextual, não alterações automáticas nem garantia de concordância perfeita. O relatório de geração inclui contagem exata de capítulos e palavras por capítulo; o número de páginas é o do PDF gerado naquele formato e muda com diagramação, fonte e revisão.

Para usar um repositório como este com obras inéditas, copie o projeto criado para um **repositório privado**. Um repositório público com o manuscrito ou os arquivos KDP expõe o texto integral, mesmo que o site mostre só a prévia. Não trate esconder um botão ou alterar JavaScript como proteção dos arquivos. Antes de publicar, verifique as regras atuais das lojas diretamente com elas.

## Desenvolvimento

```bash
python -m unittest discover -s tests -v
```

O código é intencionalmente pequeno e auditável. Novas regras entram como avisos com testes; não como correções silenciosas de conteúdo.
