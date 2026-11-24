---
name: ui-banner
description: >-
  Cria banners e imagens de divulgação de um projeto (post para redes, capa, hero de site, imagem de
  loja de apps, open graph) no visual do projeto, usando a sub-skill banner-design do plugin
  ui-ux-pro-max (tamanhos, zonas seguras, direção de arte). Use quando o usuário pedir "banner",
  "post", "capa", "imagem para divulgar", "og image", "hero" ou chamar /ui-banner. Funciona em
  qualquer projeto; instala o plugin se faltar.
---

# Banners e imagens de divulgação

Argumentos (`$ARGUMENTS`): plataforma/formato (ex.: `instagram-post`, `linkedin`, `og`, `hero`),
mensagem e campanha (opcionais).

## 0. Preflight

```bash
bash "$HOME/.claude/skills/ui-banner/scripts/ensure-plugin.sh"
```

Guarde `PLUGIN_SKILLS`. Se instalou agora, avise sobre `/reload-plugins`; até lá leia direto
`$PLUGIN_SKILLS/banner-design/SKILL.md` e `references/banner-sizes-and-styles.md` (tamanhos exatos e
zonas seguras por plataforma).

## 1. Contexto

1. Visual do projeto: tokens de cor e fonte, logos, e decisões/paletas recusadas na nota do projeto
   no Obsidian (`_knowledge/INDEX.md` → nota do projeto). O banner usa a identidade do projeto; os
   estilos da sub-skill (gradiente, neon, etc.) só se o usuário pedir.
2. Mensagem: o que divulgar e para quem. Se faltar, pergunte em 1 pergunta.
3. Imagens do produto: protótipos em `projects/<Projeto>/prototipos/` ou telas reais servem como
   visual (mockup de celular em HTML/CSS).

## 2. Produzir

1. 2–3 direções de arte no tamanho exato da plataforma, em HTML/CSS (texto dentro da zona segura,
   contraste ≥ 4.5:1, logo legível). Mostre numa página de prévia com a ferramenta `Artifact`.
2. Depois da escolha, exporte PNG no tamanho exato com a ferramenta de screenshot disponível na
   sessão (ex.: Playwright MCP). Sem ela, entregue o HTML e diga que o PNG ficou pendente.
3. Imagem gerada por IA só com pedido explícito; nunca invente depoimentos, números ou logos de terceiros.

## 3. Entregar

- Arquivos em `~/Documents/repositories/obsidian/projects/<Projeto>/banners/<campanha>/` (HTML + PNG),
  com uma nota `.md` (formato, texto, data, link da prévia). Dentro do repositório só com ok e onde o
  projeto já guarda imagens (ex.: `public/og.png`).
