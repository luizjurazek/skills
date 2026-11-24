---
name: ui-prototype
description: >-
  Gera protótipos/mockups navegáveis (HTML, mobile 375px + desktop) das telas de um projeto
  a partir do plano/tasks, usando o plugin ui-ux-pro-max como consulta de UX e o design
  system do próprio projeto como fonte da verdade. Salva no Obsidian, linka nas tasks e
  publica como Artifact. Use quando o usuário pedir "protótipo", "mockup", "gerar telas",
  "desenhar as telas do plano/da task", "como ficaria a tela X", ou chamar /ui-prototype.
  Funciona em qualquer projeto; instala o plugin ui-ux-pro-max se faltar.
---

# Protótipo de telas

Fluxo: **preflight → contexto → consulta de UX → HTML → salvar e linkar → publicar → pendências**.
O plugin `ui-ux-pro-max` é só **consulta** (estilos, UX, padrões por produto). Quem decide o visual
é o design system do projeto; quem escreve as telas é você.

Argumentos opcionais (`$ARGUMENTS`): quais telas/tasks, se é para atualizar um protótipo existente,
"sem publicar" (só arquivo).

## 0. Preflight: plugin ui-ux-pro-max

```bash
bash "$HOME/.claude/skills/ui-prototype/scripts/ensure-plugin.sh"
```

- Imprime `SEARCH=<caminho do search.py>` quando está tudo ok. Guarde esse caminho.
- Se o script acabou de instalar o plugin, avise o usuário que `/reload-plugins` ativa as
  sub-skills (`ui-ux-pro-max:*`) nesta sessão — o `search.py` já funciona sem reload.
- Se falhar (sem rede, sem `claude` no PATH), siga sem a consulta e diga que as decisões de UX
  vieram só das regras deste arquivo.

## 1. Contexto (leia antes de desenhar)

1. **Design system do projeto**, nesta ordem: `AGENTS.md`/`CLAUDE.md`, rules (`.claude/rules/*`
   sobre design/estilo/UX), arquivo de tokens (`theme.css`, `tokens.*`, `tailwind.config.*`…),
   e 1–2 componentes existentes (navegação, lista, formulário) para copiar o visual real.
2. **Plano do produto**: leia `~/Documents/repositories/obsidian/_knowledge/INDEX.md`, abra a nota
   do projeto e, por ela, a pasta do projeto no vault (`projects/<Projeto>/`: nota raiz, `analise/`
   com regras de negócio, `tasks/`). Identifique as telas ainda não implementadas e as regras
   (RN/CA) que cada uma precisa mostrar.
3. Se já existir `projects/<Projeto>/prototipos/`, leia o índice: o pedido pode ser uma atualização.
4. Sem design system nem plano encontrados: pergunte ao usuário antes de inventar.

## 2. Consulta de UX

Rode 3–5 buscas curtas (uma intenção cada) com o `SEARCH` do preflight:

```bash
python3 "$SEARCH" "<tipo de produto>" --domain product -n 2
python3 "$SEARCH" "<padrão da tela, ex.: streak calendar>" --domain chart -n 2
python3 "$SEARCH" "<problema de UX, ex.: inline form validation>" --domain ux -n 3
```

Regras:
- **Nunca** `--persist` nem `--design-system` gravando arquivos no projeto: criaria um
  `design-system/MASTER.md` que contradiz o design system existente.
- **Nunca** troque paleta/fonte do projeto pela recomendação da busca. Use a busca para padrões de
  interação, acessibilidade, estados e tipos de visualização.
- Não use a sub-skill `ui-styling` para código se o projeto proíbe Tailwind/shadcn.
- Não mande dados privados do projeto nas queries (use termos genéricos).

## 3. Escrever o HTML

Parta de [`assets/frame-template.html`](assets/frame-template.html) (molduras de celular e desktop,
tab bar, estrutura "spec": mockup à esquerda, notas à direita). Exemplo completo aprovado:
`~/Documents/repositories/obsidian/projects/Athlos/prototipos/telas-mvp.html`.

- **Tokens**: copie os valores do arquivo de tokens do projeto para o `:root` (claro) e para os dois
  blocos escuros (`@media (prefers-color-scheme: dark) :root:not([data-theme="light"])` e
  `:root[data-theme="dark"]`). Mesma fonte do projeto (Google Fonts) com fallback.
- **Uma seção por tela/task**: celular 375px com dados de exemplo **coerentes com as regras de
  negócio** (datas reais, semana certa, limites como janelas de N dias) + notas com:
  tag da task e RNs, título, 1 parágrafo, lista "RN/CA → como a tela atende", "Decisões de UX" e
  "Em aberto". Inclua uma visão desktop quando a tela muda de layout.
- **Interativo só no que ensina algo**: o check que atualiza o resumo, o seletor que habilita o
  botão. JS pequeno, sem libs.
- Padrões que sempre valem (se o projeto não disser o contrário): alvo de toque ≥ 44px; estado nunca
  só por cor; erro junto do campo; opção desabilitada explica o motivo; botão diz a ação; textos na
  língua da interface do projeto.
- Se o projeto tiver uma rule de padrões de UX (ex.: `ux-patterns.md`), ela manda.

## 4. Salvar e linkar no Obsidian

Pasta: `~/Documents/repositories/obsidian/projects/<Projeto>/prototipos/`.

1. `<slug>.html` **autônomo** (com `<!doctype html>`, `<html lang>`, `<head>` com charset e viewport),
   para abrir direto no navegador.
2. `<slug>.md` índice: o que é, link local `[<slug>.html](<slug>.html)`, link publicado, data, e
   **um `##` por tela** com a task linkada (`[[../tasks/<arquivo>|<título>]]`) e os bullets de decisão;
   no fim, `## A confirmar` com checkboxes.
3. Em cada task coberta, adicione no topo de `## Referências`:
   `- [[../prototipos/<slug>#<heading>|Protótipo: <heading>]]` (não duplique se já existir).
4. Nota raiz do projeto: link para o índice na seção de navegação.
5. Registre a pasta/decisão na nota do projeto em `_knowledge/projects/` (em inglês).

Atualizando um protótipo existente: edite o mesmo `<slug>`, preserve headings já linkados.

## 5. Publicar

Salvo pedido de "sem publicar": publique com a ferramenta `Artifact` (carregue as orientações de
design dela antes, se ainda não estiverem no contexto). Para atualizar, republique o mesmo arquivo
ou passe a `url` do índice. O arquivo publicado não leva doctype/html/head (o Artifact embrulha);
gere o `.html` do Obsidian a partir dele com o cabeçalho adicionado.

## 6. Entregar

Resposta curta: link, o que cada tela mostra (1 linha), e as **decisões que precisam de ok** antes de
virar código. Ofereça transformar os padrões aprovados em rule do projeto
(`.claude/rules/ux-patterns.md`) — só crie se o usuário pedir.
