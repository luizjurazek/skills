---
name: ui-slides
description: >-
  Monta apresentações de um projeto (pitch, demo, status, plano) com a estratégia de narrativa e
  copywriting da sub-skill slides do plugin ui-ux-pro-max e o visual do próprio projeto. Use quando o
  usuário pedir "apresentação", "slides", "deck", "pitch", "apresentar o projeto/plano/resultado" ou
  chamar /ui-slides. Funciona em qualquer projeto; instala o plugin se faltar.
---

# Apresentações

Argumentos (`$ARGUMENTS`): tema/objetivo, público e quantidade de slides (opcional).

## 0. Preflight

```bash
bash "$HOME/.claude/skills/ui-slides/scripts/ensure-plugin.sh"
```

Guarde `PLUGIN_SKILLS`. Se instalou agora, avise sobre `/reload-plugins`; até lá leia direto
`$PLUGIN_SKILLS/slides/SKILL.md` e as `references/` (estratégias por tipo de deck, fórmulas de copy,
layouts).

## 1. Contexto

1. Objetivo e público: se não estiverem claros, pergunte (1 pergunta, opções curtas).
2. Conteúdo real do projeto: nota no Obsidian (`_knowledge/INDEX.md` → nota do projeto → pasta
   `projects/<Projeto>/`: requisitos, regras, tasks, protótipos em `prototipos/`), README, números
   reais. **Nunca invente métricas**; marque como exemplo o que for ilustrativo.
3. Visual: tokens de cor/fonte do projeto e logos (`public/`, etc.).

## 2. Montar

1. Escolha a estratégia de narrativa da sub-skill que combina com o objetivo (ex.: problema →
   solução → demo → próximos passos) e escreva o roteiro: título + 1 mensagem por slide.
   Mostre o roteiro em texto antes de produzir se o deck tiver mais de 8 slides.
2. Produza o deck pelo tipo **Slides** da ferramenta `Artifact` (`action: "quickstart"`,
   `intent: "slides"`), aplicando cor, fonte e logo do projeto. Se o tipo não existir, faça HTML
   próprio seguindo os layouts da sub-skill, com Chart.js só onde houver dado real.
3. Protótipos de tela existentes (`prototipos/*.html`) podem virar slides de demo — reaproveite.

## 3. Entregar

- Link do deck + 1 linha por slide.
- Salve uma nota `~/Documents/repositories/obsidian/projects/<Projeto>/apresentacoes/<slug>.md` com
  objetivo, público, data, link e o roteiro; linke na nota raiz do projeto.
- Textos dos slides na língua do público; sem jargão interno não explicado.
