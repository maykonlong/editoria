# Leitor instalável sem livro offline

Para livros com leitura pública autorizada (`preview` ou `full` explicitamente liberado), o site gerado deve oferecer um webapp instalável. O ícone abre o **início da leitura** na primeira visita e retoma o capítulo e a posição salvos nas visitas seguintes. A capa e a abertura vêm antes do índice e do capítulo 1. Uma ação separada permite recomeçar.

O progresso fica no armazenamento local do navegador ou app, identificado pelo `id` do livro. Não há conta nem sincronização entre aparelhos. Limpar os dados do site pode apagar o marcador. Um link direto para capítulo deve continuar abrindo aquele capítulo; o botão “Começar” abre a capa, enquanto “Continuar” usa o ponto salvo.

O service worker pode guardar **somente a estrutura**: landing, leitor/índice, estilos, JavaScript, manifesto, ícones e aviso de falta de conexão. Não pré-carregue nem salve capítulos, imagens narrativas, manuscrito, EPUB ou PDF para uso offline. Os capítulos precisam de rede. Se a conexão cair, mostre uma mensagem clara e preserve o marcador. O armazenamento normal do navegador não é uma licença para publicar o texto integral.

No modo `landing`, não há PWA de leitura: sem capítulos, o ícone de “continuar” prometeria algo inexistente. A revisão privada pode guardar o ponto localmente, mas não deve instalar um app público. O modo `preview` expõe apenas o trecho decidido pelo autor; o fim da prévia deve levar ao link real de compra ou dizer claramente que a continuação ainda não está disponível.

Ao republicar, o leitor busca a estrutura atual na rede e atualiza sua reserva offline. Ao voltar de `preview` para `landing`, a página tenta remover o registro e o cache antigos do app neste navegador. Isso não apaga instalações, cópias ou caches de terceiros em outros aparelhos; confira a publicação final e o histórico do repositório.

## Testes de aceitação

1. Num navegador compatível, confirme manifesto, ícones de 192 e 512 px e instalação via menu do navegador. A oferta automática pode depender de regras de uso do navegador.
2. Abra pelo ícone sem marcador: capa, dedicatória/carta (se houver) e índice devem aparecer antes do capítulo 1.
3. Avance, role até o meio de um capítulo, feche e reabra pelo ícone: capítulo **e trecho** devem voltar. Teste também recarregar uma URL direta de capítulo.
4. Volte à landing: “Continuar de onde parei” e “Recomeçar da capa” devem ter destinos distintos.
5. Desconecte a rede. O app pode abrir a estrutura e o aviso; **o texto dos capítulos não pode estar no cache do service worker**. Reconecte e confira o marcador.
6. Troque `preview` por `landing` e gere de novo: capítulos, manifesto e service worker antigos devem desaparecer da saída pública.

Instalar o app não altera direitos nem regras de exclusividade. Se o projeto estiver em programa com restrições digitais, confirme nas fontes oficiais o que pode ficar público antes de habilitar qualquer capítulo, mesmo sem cache offline.
