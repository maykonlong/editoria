# Publicação sem surpresas

Este é um checklist editorial, não aconselhamento jurídico nem garantia de aceitação por uma loja.

## Antes de divulgar

1. Feche texto, nome de autoria, títulos, sumário e direitos de cada imagem e fonte.
2. Peça a leitoras do público-alvo que anotem o capítulo em que quiseram seguir, onde pararam, o que não entenderam e se o final pareceu conquistado. Corrija erros comprovados; para gosto pessoal, procure padrões.
3. Gere EPUB e PDF a partir da **mesma** versão do manuscrito. Rode `editoria verificar` e, se possível, o EPUBCheck oficial.
4. Confira o EPUB num leitor Kindle/Previewer e o PDF no Previewer do impresso. Peça uma prova física antes de aprovar a capa completa.
5. Confira os requisitos atuais de ficha catalográfica, ISBN, depósito legal, direitos autorais e metadados para o país e formato escolhidos. Documente a fonte e a data dessa conferência.
6. Coloque links reais de compra no site somente depois que existirem. Não prometa leitura grátis, formato, preço ou disponibilidade que ainda não estejam ativos.
7. Leia capa, dedicatória/carta e encerramento em cada formato. A abertura deve convidar, não entregar a conclusão; o convite para avaliar e indicar pode ficar em uma última página, sem misturar marketing com a cena final.

## Site e exclusividade digital

O modo padrão é `landing`: só apresentação, sem capítulos. `preview` exporta apenas a quantidade configurada e nunca deve ser ativado sem uma decisão comercial. `full` requer a opção explícita `--permitir-publico-completo` na geração; não é recomendado para um lançamento ainda indefinido.

Se você cogita um programa com exclusividade digital, **confira as regras oficiais atuais antes de hospedar ou vender o texto digital em outro lugar**. O código não presume que uma porcentagem, um número de capítulos ou um prazo seja sempre permitido. Apagar a página visível pode não remover cópias do Git, arquivos de download ou caches. Nesses casos, consulte a plataforma antes da inscrição.

O [PWA do leitor](LEITOR_PWA.md) não guarda capítulos offline, mas isso **não torna permitida** a publicação de um texto que já está disponível online. O modo de site e o conteúdo versionado continuam determinando o que foi distribuído.

## Pacote impresso

O PDF do miolo não basta para publicar um impresso. A capa completa deve ser calculada **depois** da paginação final, com dimensões e perfil exigidos pelo fornecedor escolhido. Mudou a ficha catalográfica, o texto, o tamanho de página ou o papel? Gere o miolo novamente e refaça a lombada/capa. A inspeção automática não substitui o Previewer nem a prova física.

## Dados e ética

- Não transforme histórias identificáveis de clientes, familiares ou leitoras em ficção sem tratar privacidade e consentimento.
- Use apenas artes, fotos, fontes e trechos para os quais exista direito de uso. Registre origem/licença em `planejamento/DIREITOS.md`.
- Um pseudônimo pode assinar a obra; biografia e marketing não devem atribuir experiências profissionais que essa pessoa não teve.
- Se a IA sugerir uma mudança de protagonista, final, tema sensível ou promessa comercial, leve a decisão ao autor. O revisor deve apontar evidência, não impor um enredo.
