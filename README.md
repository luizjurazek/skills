# Skills pessoais

Skills do Claude Code. Cada pasta com `SKILL.md` é uma skill; o `install.sh` da raiz cria um symlink
em `~/.claude/skills/<nome>` (vale para qualquer projeto, e editar aqui já atualiza) e roda o
`install.sh` da própria skill quando ela tem dependências externas.

## Instalar

```bash
cd ~/Documents/personal/skills
./install.sh                 # todas as skills
./install.sh ui-prototype    # só as escolhidas
```

- Idempotente: rodar de novo não duplica nada.
- Não sobrescreve um link que aponta para outra cópia da skill (avisa e pula).
- Depois de instalar, rode `/reload-plugins` (ou abra uma nova sessão) no Claude Code.

## Skills

| Skill | Para quê | Dependências |
| --- | --- | --- |
| `mr-message` | Mensagem curta de MR do Nexus (copia para o clipboard) | `wl-copy` ou `xclip` (opcional) |
| `open-pr` | Abrir MR no GitLab do Nexus contra `develop`, com descrição da `mr-message` | `glab` autenticado em `git.copasul.coop.br`; skill `mr-message` |
| `open-github-pr` | Abrir PR(s) no GitHub contra `develop` em um ou vários repos e comentar na tarefa LiveSEO | MCP `user-github` (sem fallback) |
| `review-nexus-pr` | Review de PR/MR do Nexus (só reporta, não altera arquivos) | `glab` (ou `gh` para GitHub) |
| `review-pr` | Review de PR do GitHub / MR do GitLab com checklist próprio (`rules.md`) | MCP GitKraken ou `mcp-gitlab`; fallback `gh`/`glab`/git |
| `sync-resultados` | Sincronizar resultados em planilha | ver `sync-resultados/README.md` |
| `ui-prototype` | Protótipos de telas (HTML mobile + desktop) a partir do plano no Obsidian | plugin `ui-ux-pro-max`, `python3` |
| `ui-design-system` | Auditar/estender os tokens e specs de componentes do projeto | plugin `ui-ux-pro-max`, `node` (validador) |
| `ui-assets` | Ícones SVG, logo, mascote, favicon no estilo do projeto | plugin `ui-ux-pro-max`; IA opcional: `scripts/setup-ai.sh` + `GEMINI_API_KEY` em `ui-assets/.env` |
| `ui-brand` | Voz, tom e guia de marca (salvo no Obsidian) e revisão de textos | plugin `ui-ux-pro-max` |
| `ui-slides` | Apresentações com o visual do projeto | plugin `ui-ux-pro-max` |
| `ui-banner` | Banners, posts, og image, hero | plugin `ui-ux-pro-max`; PNG via screenshot (Playwright) |

As skills `ui-*` são independentes: cada uma tem o próprio `scripts/ensure-plugin.sh`, que instala o
plugin `ui-ux-pro-max` se faltar. Elas usam o plugin como referência e mantêm o design system do
projeto como fonte da verdade; saídas que não são código vão para `projects/<Projeto>/` no Obsidian.

## ui-prototype

Uso, em qualquer projeto:

```text
/ui-prototype telas da task 05
```

ou só peça "gera o protótipo da tela X". A skill confere o plugin `ui-ux-pro-max` (instala se faltar),
lê o design system do projeto e o plano no Obsidian, pergunta onde salvar (Obsidian em
`projects/<Projeto>/prototipos/`, `docs/prototypes/` do repo ou outra pasta), gera o HTML autônomo e
abre no navegador. No Obsidian, também linka nas tasks. Só publica como Artifact se você pedir
(`/ui-prototype ... publicar`).
