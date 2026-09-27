# Leitor no GitHub Pages

O gerador produz um site estático em `dist/publico/`. Ele funciona sem servidor de aplicação e contém índice, páginas de capítulo, ajustes de texto/contraste, descrição, temas e dados estruturados. A fonte do manuscrito e o pacote de publicação ficam fora dessa pasta.

## Primeiro, escolha o que será público

Em `livro.json`, `site.modo` pode ser:

- `landing` (padrão): apresentação, sem capítulos;
- `preview`: somente os primeiros `site.capitulos_gratis` capítulos;
- `full`: livro inteiro, permitido apenas com `--permitir-publico-completo`.

Preencha `site.url` com a URL final, com barra final, por exemplo `https://seuusuario.github.io/seu-livro/`; sem ela não são gerados sitemap, robots nem endereço canônico. `site.url_compra` só deve ser preenchida quando a página de venda já existir. Edite título, sinopse e temas para refletir o texto real: dados estruturados não substituem conteúdo verdadeiro.

Rode `editoria gerar . --somente publico` e confira `dist/publico/index.html`, `ler.html` (se houver prévia), cada página de capítulo e o último link da prévia em celular, tablet e leitor com navegador. O comando **recria** essa pasta, removendo capítulos de uma configuração pública anterior. Confira o conteúdo antes de enviar.

## Publicação por GitHub Actions

O arquivo [`exemplos/pages.yml`](../exemplos/pages.yml) é um modelo para o **repositório do livro**, não para este repositório da ferramenta. Copie-o para `.github/workflows/pages.yml` do livro, ajuste a versão da ferramenta e selecione **Settings → Pages → Build and deployment → Source: GitHub Actions**. O fluxo constrói somente `dist/publico/` e usa o artefato de Pages; não envia `dist/kdp/`.

Esse modelo pressupõe que o projeto do livro e o workflow estejam no mesmo repositório e que o código da ferramenta esteja acessível no GitHub. Para produção, fixe a instalação da ferramenta em uma tag ou commit testado, no lugar de `@main`. A página publicada é pública; a privacidade do repositório de origem depende do plano/arranjo GitHub. Um repositório de livro **público com `manuscrito/` versionado já expõe o texto integral**, independentemente do modo da landing. Prefira fonte privada e confirme que seu plano/fluxo permite o Pages desejado, ou publique apenas o artefato estático num repositório separado.

Antes de programas com exclusividade digital, consulte as regras atuais da loja para trechos gratuitos e distribuição fora dela. Excluir um arquivo da página não apaga cópias no histórico do Git, forks ou caches.

Referências oficiais: [workflow de Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) e [fonte de publicação](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).
