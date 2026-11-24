---
name: ui-design-system
description: >-
  Audita, organiza e estende o design system (tokens de cor, espaço, raio, tipografia, movimento e
  specs de componentes) de um projeto que já tem o seu, usando a sub-skill design-system do plugin
  ui-ux-pro-max como referência. Use quando o usuário pedir "revisar os tokens", "auditar o
  theme.css", "criar token novo", "spec do componente X", "tem cor fixa no código?", "organizar o
  design system" ou chamar /ui-design-system. Funciona em qualquer projeto; instala o plugin se faltar.
---

# Design system do projeto

O design system **que já existe no projeto é a fonte da verdade**. A sub-skill `design-system` do
plugin entra como referência de método (arquitetura em 3 camadas: primitivo → semântico → componente,
validação de valores fixos), nunca para gerar um sistema paralelo.

Argumentos (`$ARGUMENTS`): `audit` (padrão), `token <nome/necessidade>`, `spec <componente>`.

## 0. Preflight

```bash
bash "$HOME/.claude/skills/ui-design-system/scripts/ensure-plugin.sh"
```

Guarde `PLUGIN_SKILLS` da saída. Se instalou agora, avise que `/reload-plugins` ativa as sub-skills;
enquanto isso, leia direto `$PLUGIN_SKILLS/design-system/SKILL.md` e as `references/` dela.
Os validadores do plugin são `.cjs` e precisam de `node`; sem ele, faça a auditoria com `grep`.

## 1. Contexto

1. `AGENTS.md`/`CLAUDE.md` e rules de design/estilo (`.claude/rules/*`).
2. O arquivo de tokens real (`theme.css`, `tokens.*`, `tailwind.config.*`, `globals.css`…).
3. Nota do projeto no Obsidian (`~/Documents/repositories/obsidian/_knowledge/INDEX.md` → nota do
   projeto): histórico de decisões visuais e paletas já recusadas. **Nunca reproponha o que foi recusado.**

## 2. Modos

### audit
- Rode o validador do plugin sobre o código de UI, com o cwd na raiz do projeto:
  `node "$PLUGIN_SKILLS/design-system/scripts/validate-tokens.cjs" --dir <pasta de UI>`
  (ou `grep -rnE '#[0-9a-fA-F]{3,8}\b|rgba?\(|[0-9]+px' --include=*.css --include=*.tsx`).
- Classifique: valor fixo que já tem token (trocar), valor recorrente sem token (criar), camada errada
  (componente usando primitivo `--palette-*` direto), tokens órfãos, contraste < 4.5:1 em algum tema.
- Entregue um relatório curto: tabela `arquivo:linha → problema → correção sugerida`, priorizado.

### token
- Encaixe o token novo na camada certa e com o mesmo padrão de nome do arquivo existente; defina os
  dois temas se o projeto tiver light/dark; confira contraste.
- Mostre o diff proposto antes de aplicar.

### spec
- Spec do componente: anatomia, estados (default, hover, active, focus, disabled, erro, loading),
  tokens usados por parte, tamanhos/alvos de toque, comportamento responsivo, acessibilidade.
- Baseie-se nos componentes que já existem no projeto.

## Regras

- **Nunca** rode `--persist`, `generate-tokens.cjs` gravando no projeto, nem crie `design-system/`,
  `tokens.json` ou `assets/design-tokens.*` paralelos ao arquivo de tokens existente.
- Mudanças no arquivo de tokens só depois do ok do usuário, com diff mostrado.
- Comentários de código em inglês; textos para o usuário na língua do projeto.
- Validação depois de alterar: type-check/build do projeto; sem navegador salvo pedido.
- Decisões duráveis (token novo, convenção nova) vão para a rule de estilo do projeto se o usuário
  pedir, e para a nota do projeto em `_knowledge/projects/` (em inglês).
