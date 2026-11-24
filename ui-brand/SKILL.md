---
name: ui-brand
description: >-
  Define e revisa a identidade de um projeto: voz e tom, vocabulário, mensagens-chave, uso de cor e
  logo, usando a sub-skill brand do plugin ui-ux-pro-max como método. Guarda o guia no Obsidian, não
  no repositório. Use quando o usuário pedir "tom de voz", "guia de marca", "como o app fala",
  "revisar os textos da interface", "mensagens de erro/vazio", "identidade do projeto" ou chamar
  /ui-brand. Funciona em qualquer projeto; instala o plugin se faltar.
---

# Marca e voz

Argumentos (`$ARGUMENTS`): `create` (guia novo), `review <tela/arquivos>` (revisar textos ou assets
contra o guia), `update` (ajustar o guia).

## 0. Preflight

```bash
bash "$HOME/.claude/skills/ui-brand/scripts/ensure-plugin.sh"
```

Guarde `PLUGIN_SKILLS`. Se instalou agora, avise sobre `/reload-plugins`; até lá leia direto
`$PLUGIN_SKILLS/brand/SKILL.md`, as `references/` e o template de guia em `templates/`.

## 1. Contexto

1. Nota do projeto no Obsidian (`~/Documents/repositories/obsidian/_knowledge/INDEX.md` → nota do
   projeto → pasta `projects/<Projeto>/`): o que é o produto, público, decisões visuais já tomadas e
   recusadas, glossário.
2. No repositório: textos reais da interface (labels, erros, estados vazios), rules de idioma e de
   design, tokens de cor, logos.
3. Se já existe `projects/<Projeto>/marca.md`, ele é o guia vigente.

## 2. Modos

- **create**: siga o método da sub-skill (personalidade, voz, tom por situação, vocabulário sim/não,
  mensagens-chave, uso de cor/logo) com **exemplos reais do produto** em cada seção (antes/depois
  de textos da própria interface). Faça 3–5 perguntas curtas antes se o público/personalidade não
  estiver claro no contexto.
- **review**: tabela `onde → texto atual → problema → sugestão`, priorizada; não edite o código sem ok.
- **update**: edite o guia preservando decisões anteriores; registre a data da mudança.

## Regras

- O guia mora em `~/Documents/repositories/obsidian/projects/<Projeto>/marca.md` (na língua do
  projeto), linkado na nota raiz do projeto. **Não** crie `docs/brand-guidelines.md` nem rode
  `sync-brand-to-tokens.cjs`/`inject-brand-context.cjs` no repositório: o projeto já tem tokens e
  rules próprios.
- Cores/logos do guia descrevem o que já existe no arquivo de tokens; proposta de mudança visual vai
  como sugestão separada, nunca aplicada direto.
- Se o usuário quiser o guia valendo para o Claude no código, ofereça condensá-lo numa rule do
  projeto (ex.: `.claude/rules/voice.md`) — só crie com ok.
- Registre decisões duráveis na nota do projeto em `_knowledge/projects/` (em inglês).
