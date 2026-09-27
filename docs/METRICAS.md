# Métricas sem transformar literatura em meta cega

`editoria verificar . --json` e `dist/relatorio.json` registram quantidade de capítulos e palavras por capítulo, da história, da abertura, do fechamento e do texto total. A contagem é feita no **corpo** dos capítulos; não inclui seus títulos nem marcas de formatação. O EPUB refluível não tem número fixo de páginas: fonte, aparelho e preferências mudam a paginação. `paginas_miolo` é a quantidade real do PDF gerado em 5,5 × 8,5 polegadas, incluindo páginas de rosto, direitos, abertura, índice e fechamento.

Não existe quantidade universal de capítulos, palavras ou páginas para um romance envolvente. Use números para achar outliers e depois leia a função de cada trecho. Um capítulo curto pode ser a pausa certa; um longo pode conter várias viradas; um final apressado se revela pela falta de decisão, consequência e tempo emocional, não por um limite matemático.

## Painel de revisão capítulo a capítulo

Copie a linha do relatório para uma tabela de trabalho e anote:

| Campo | Pergunta editorial |
| --- | --- |
| Capítulo e palavras | Ele difere muito dos vizinhos? Há uma razão dramática? |
| Objetivo e obstáculo | O que a personagem tenta nesta parte e o que a impede? |
| Mudança | O que passou a ser verdade que não era antes? |
| Próximo impulso | Que consequência, escolha ou pergunta faz avançar? |
| Marcadores de tempo | Idade, dia, estação, dinheiro e trajetos concordam? |
| Linguagem | Há palavra fora da voz/público ou frase que exige releitura? |
| Leitoras beta | Onde quiseram parar ou pular adiante? Houve padrão? |

Para avaliar a passagem entre capítulos, leia o **último parágrafo** do anterior junto dos **dois primeiros** do seguinte, sem o meio. A ligação deve ser compreensível ou a ruptura deve ser intencional. Depois volte ao capítulo inteiro para verificar se o meio construiu essa passagem.

O relatório automático não mede emoção, clareza social nem potencial comercial. Registre essas decisões em `planejamento/MAPA_CAPITULOS.md` e `feedback/LEITORAS_BETA.md`. Depois de cada mudança no manuscrito, gere site, EPUB e PDF de novo: páginas e prévia podem mudar.
