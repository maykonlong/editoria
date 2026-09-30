# Escrita com IA: memória, decisões e aprovação

O autor decide o que é canônico. A IA pode sugerir, planejar, escrever e auditar, mas uma sugestão só entra na Bíblia ou no estado aprovado depois de decisão explícita do autor. Não envie o manuscrito a serviços externos sem autorização.

## Ordem de trabalho por capítulo

1. Leia `livro.json`, `planejamento/BIBLIA.md`, `PERSONAGENS.md`, `CRONOLOGIA.md` e os registros pertinentes de segredos, objetos e locais. Consulte as memórias dos capítulos anteriores.
2. Registre em `MAPA_CAPITULOS.md` objetivo, obstáculo, revelações e consequência. Marque o capítulo como `planejado` em `planejamento/ESTADO.json`.
3. Após a decisão do autor, escreva em `manuscrito/`. Marque `rascunho`.
4. Audite fatos, conhecimento de personagens, segredos e estilo com trechos como evidência. Use `em_revisao` enquanto houver correções.
5. Só o autor muda para `aprovado`. Então preencha `memoria/CAP_NN.md` com fatos novos, consequências, segredos preservados e pontas abertas. Atualize os registros canônicos e rode `editoria verificar` e `editoria status`.

`ESTADO.json` é um registro editorial manual. As chaves em `capitulos` são números com dois ou três dígitos; os valores aceitos são `planejado`, `rascunho`, `em_revisao` e `aprovado`. `decisoes_pendentes` contém perguntas em aberto. Nenhum comando aprova capítulos automaticamente. O arquivo não é incluído no site nem no EPUB/PDF.

```json
{
  "capitulos": {"01": "aprovado", "02": "em_revisao", "03": "planejado"},
  "decisoes_pendentes": ["Quando a protagonista descobre a carta?"]
}
```

`editoria status projeto --json` conta arquivos escritos, capítulos planejados e aprovados, capítulos sem estado e memórias pendentes. Um capítulo aprovado sem memória recebe aviso em `editoria verificar`. Projetos antigos sem `ESTADO.json` são aceitos: todos os capítulos aparecem como sem estado até que o autor crie o registro.

Não converta automaticamente um segredo ou evento planejado em revelação. Ao encontrar lacuna ou contradição, registre capítulo e trecho em `auditorias/`, acrescente a decisão necessária ao estado e aguarde o autor. A cada cinco capítulos aprovados, faça uma auditoria de continuidade; a cada dez, uma leitura mais ampla de estrutura e estilo. Essas cadências são sugestões, não validações automáticas.

## Site do livro

O projeto também pode gerar uma apresentação pública. O modo inicial é `landing`, sem capítulos. Para publicar uma prévia, configure `site.modo` como `preview` e escolha `capitulos_gratis` em `livro.json`; gere com `editoria gerar projeto --somente publico` e confira `dist/publico/` antes da hospedagem. Siga [GITHUB_PAGES.md](GITHUB_PAGES.md) para hospedar a pasta pública. O manuscrito, as memórias, as auditorias e `dist/kdp/` devem ficar fora da hospedagem. Publicar o texto completo exige a opção explícita documentada em [PUBLICACAO.md](PUBLICACAO.md).
