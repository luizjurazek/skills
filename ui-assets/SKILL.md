---
name: ui-assets
description: >-
  Cria ícones SVG, logos, mascotes e outros assets visuais de um projeto no estilo dele, usando a
  sub-skill design do plugin ui-ux-pro-max (ícones SVG feitos à mão; logos/mockups com Gemini quando
  houver chave). Use quando o usuário pedir "cria um ícone", "set de ícones", "logo", "favicon",
  "mascote", "ilustração", "mockup de identidade" ou chamar /ui-assets. Funciona em qualquer projeto;
  instala o plugin e as dependências se faltarem.
---

# Assets visuais

Ordem de preferência: **SVG feito à mão** (sem API, combina com os ícones existentes) → geração por
IA só quando o usuário quiser e houver chave.

Argumentos (`$ARGUMENTS`): `icon <nome(s)>`, `logo`, `mascot`, `favicon`, `mockup`.

## 0. Preflight

```bash
bash "$HOME/.claude/skills/ui-assets/scripts/ensure-plugin.sh"
```

Guarde `PLUGIN_SKILLS`. Se instalou agora, avise sobre `/reload-plugins`; até lá leia direto
`$PLUGIN_SKILLS/design/SKILL.md` e a `references/` do tipo pedido (ex.: `icon-design.md`).

Geração por IA (logo, mockup, ícone via Gemini) precisa de:
- `bash "$HOME/.claude/skills/ui-assets/scripts/setup-ai.sh"` → cria `.venv` na skill com
  `google-genai` e `pillow` e imprime `PY=<python da venv>`. Rode os scripts do plugin com esse `PY`.
- `GEMINI_API_KEY` no ambiente ou em `~/.claude/skills/ui-assets/.env` (ver `.env.example`).
  Sem chave: diga isso e ofereça a versão SVG/HTML. **Nunca peça para colar a chave no chat.**
- **Peça ok antes de cada chamada paga** e diga quantas imagens vai gerar.

## 1. Contexto

1. Ícones existentes no projeto (ex.: componente de ícones, `public/*.svg`, `app/icon.svg`): extraia
   o estilo — `viewBox`, `stroke-width`, `linecap/linejoin`, preenchido ou linear, cantos.
2. Tokens de cor e regras de design do projeto; logos atuais.
3. Nota do projeto no Obsidian (`_knowledge/INDEX.md` → nota do projeto, e a pasta do projeto em
   `projects/<Projeto>/`): épicos ou tasks que descrevem o asset (ex.: mascote).

## 2. Por tipo

- **icon**: SVG no mesmo grid e traço dos existentes, `currentColor`, sem cor fixa, legível a 20–24px.
  Se o projeto tem um mapa de ícones em código, entregue o trecho no mesmo formato para encaixar.
- **favicon**: SVG com fundo/cantos coerentes com a marca + instruções para gerar `.ico`; confira em 16px.
- **logo / mascot / mockup**: comece por 2–3 direções em SVG ou HTML (rápido, editável); só gere por
  IA se o usuário quiser. Mascote: defina poses/estados necessários pelo produto (ex.: feliz,
  triste, comemorando) e mantenha proporções entre eles.

## 3. Entregar

- Mostre o resultado publicando uma página de prévia com a ferramenta `Artifact` (claro e escuro, em
  tamanhos reais), salvo se o usuário pedir só os arquivos.
- Arquivos: dentro do projeto só onde ele já guarda assets (ex.: `public/`, componente de ícones) e
  só com ok; propostas/variações vão para `~/Documents/repositories/obsidian/projects/<Projeto>/assets/`
  com uma nota `.md` listando o que é cada arquivo, linkada na task/épico relacionado.
- Não mande dados privados do projeto para APIs externas além do prompt necessário ao asset.
