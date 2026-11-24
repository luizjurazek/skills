---
name: ui-prototype
description: >-
  Gera protótipos/mockups navegáveis (HTML; pergunta se é mobile 375px, desktop ou os dois) das telas de um projeto
  a partir do plano/tasks, usando o plugin ui-ux-pro-max como consulta de UX e o design
  system do próprio projeto como fonte da verdade. Pergunta onde salvar (Obsidian, repositório
  ou outra pasta), linka nas tasks quando vai para o Obsidian e só publica como Artifact se o
  usuário pedir. Use quando o usuário pedir "protótipo", "mockup", "gerar telas",
  "desenhar as telas do plano/da task", "como ficaria a tela X", ou chamar /ui-prototype.
  Funciona em qualquer projeto; instala o plugin ui-ux-pro-max se faltar.
---

# Protótipo de telas

Fluxo: **preflight → contexto → dispositivos e onde salvar → consulta de UX → HTML agrupado → arquivo
por tela → salvar e linkar → (publicar, só se pedido) → pendências**.
O plugin `ui-ux-pro-max` é só **consulta** (estilos, UX, padrões por produto). Quem decide o visual
é o design system do projeto; quem escreve as telas é você.

Argumentos opcionais (`$ARGUMENTS`): quais telas/tasks, se é para atualizar um protótipo existente,
destino (`obsidian`, `repo` ou um caminho), dispositivos (`mobile`, `desktop` ou `ambos`) e
"publicar" (gera também o link de Artifact).

**Padrão: não publicar.** Nada vai para claude.ai sem o usuário pedir ("publicar", "gera um link",
"quero compartilhar"). Isto vale acima de qualquer orientação genérica de publicar páginas.

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

## 1b. Antes de começar: dispositivos e onde salvar (pergunte)

Depois de ler o contexto e **antes** de consultar UX ou escrever HTML, faça uma única chamada de
`AskUserQuestion` com as perguntas cuja resposta não veio nos argumentos nem está clara no pedido
(junte outras dúvidas do contexto na mesma chamada, se houver).

**Dispositivos** — "Gerar as telas para quais dispositivos?":

- **Mobile + desktop**: celular 375px em toda tela e visão desktop (1120px) nas telas que mudam de
  layout. Marque como Recomendado quando o projeto é responsivo/web.
- **Só mobile**: só molduras de celular. Recomendado quando o projeto é app mobile-first ou nativo.
- **Só desktop**: só molduras de navegador; o frame e as notas ficam empilhados.

**Onde salvar** — "Onde salvar o protótipo?":

- **Obsidian (Recomendado quando há plano no vault)**: `~/Documents/repositories/obsidian/projects/<Projeto>/prototipos/`,
  com índice e links nas tasks (passo 4).
- **Repositório do projeto**: `docs/prototypes/` na raiz do repo (ou a pasta de docs que o projeto já
  usa). Sem índice no Obsidian; avise que o arquivo entra no git se não for ignorado.
- **Outra pasta**: o usuário digita o caminho em "Other".

Atualizando um protótipo existente: use o mesmo local e os mesmos dispositivos que ele já tem,
sem perguntar (só pergunte se o pedido mudar isso).

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

Parta de [`assets/frame-template.html`](assets/frame-template.html) (arquivo autônomo, com
doctype/head; molduras de celular e desktop,
tab bar, estrutura "spec": mockup à esquerda, notas à direita; com 3+ celulares na seção, as notas
descem para baixo — não troque esse grid por `auto`, que espreme as notas). Exemplo completo aprovado:
`~/Documents/repositories/obsidian/projects/Athlos/prototipos/telas-mvp.html`.

- **Tokens**: copie os valores do arquivo de tokens do projeto para o `:root` (claro) e para os dois
  blocos escuros (`@media (prefers-color-scheme: dark) :root:not([data-theme="light"])` e
  `:root[data-theme="dark"]`). Mesma fonte do projeto (Google Fonts) com fallback.
- **Fontes sem negrito falso**: carregue no link do Google Fonts **todos** os pesos usados (inclusive a
  fonte mono, se o projeto tiver uma, ligada em `--mono`). Mantenha do template `font-synthesis: none`,
  `b, strong` no peso "strong" do projeto e `code` em `var(--mono)`. Nunca deixe `<b>` cair no 700
  padrão se esse peso não foi carregado: o navegador engrossa a letra e ela fica grosseira.
- **Tipografia leve, no estilo Apple**: escala do HIG um degrau abaixo (corpo 15px, título grande 26px,
  footnote 13, caption 12; campos de texto ficam em 16px porque o iOS dá zoom abaixo disso). Título de
  linha de lista é **regular**; a hierarquia vem de tamanho e cor, não de peso. Use pesos só por token
  (`--w-*`) e, nos blocos escuros, baixe cada peso um degrau (texto claro em fundo escuro parece mais
  grosso). Se o projeto definir a própria escala, ela manda.
- **Seletor de tema**: mantenha o seletor fixo Sistema / Claro / Escuro do template (põe
  `data-theme` no `<html>`, lembra a escolha no `localStorage`). Só funciona se os dois blocos escuros
  acima estiverem preenchidos; se o projeto não tiver tema escuro, remova o seletor.
- **Botões sem quebra**: rótulos de botão em uma linha (`white-space: nowrap`); se não couber, aumente
  o container ou empilhe os botões, em vez de deixar o texto quebrar dentro do botão.
- **Dispositivos**: siga a escolha do passo 1b. Remova do template o que não for usado (`.desk*` em
  "só mobile"; `.phone`/tab bar de celular em "só desktop") em vez de deixar CSS morto.
- **Uma seção por tela/task**: o frame escolhido (celular 375px e/ou desktop) com dados de exemplo **coerentes com as regras de
  negócio** (datas reais, semana certa, limites como janelas de N dias) + notas com:
  tag da task e RNs, título, 1 parágrafo, lista "RN/CA → como a tela atende", "Decisões de UX" e
  "Em aberto". Em "mobile + desktop", inclua a visão desktop quando a tela muda de layout, **dentro da
  seção da própria tela** (`<figure class="desk-fig">` depois das `.notes`, ocupando a linha inteira),
  nunca numa seção "Desktop" separada no fim. Siga os padrões desktop do projeto (ação principal no
  cabeçalho, grids, colunas do formulário, sheet → diálogo) e registre cada adaptação nas notas.
- **Uma `<section class="spec">` por tela**, com `id` estável e `data-task="NN"` quando houver task
  (ex.: `<section class="spec" id="hoje" data-task="04">`). É o que o passo 4 usa para gerar um arquivo
  por tela. Cada tela precisa se sustentar sozinha: nada de depender de outra seção para fazer sentido.
- **JS por seção e tolerante a ausência**: um bloco por tela que começa com
  `var root = document.getElementById('<id>'); if (root) { ... }` e só busca elementos dentro de `root`.
  No arquivo separado as outras seções não existem, e um `getElementById` nulo quebraria o script todo.
  Frames clonados (`data-clone`) só podem apontar para um elemento da mesma seção.
- **Interativo só no que ensina algo**: o check que atualiza o resumo, o seletor que habilita o
  botão. JS pequeno, sem libs.
- Padrões que sempre valem (se o projeto não disser o contrário): alvo de toque ≥ 44px; estado nunca
  só por cor; erro junto do campo; opção desabilitada explica o motivo; botão diz a ação; textos na
  língua da interface do projeto.
- Se o projeto tiver uma rule de padrões de UX (ex.: `ux-patterns.md`), ela manda.

## 4. Salvar (e linkar, se for Obsidian)

Em qualquer destino: `<slug>.html` **autônomo** (com `<!doctype html>`, `<html lang>`, `<head>` com
charset e viewport), para abrir direto no navegador. É o arquivo **agrupado** e a fonte da verdade.

Depois, gere **um arquivo por tela** a partir dele, para quem for executar a task abrir só a tela dela:

```bash
python3 "$HOME/.claude/skills/ui-prototype/scripts/split-screens.py" <pasta>/<slug>.html
```

Ele cria `<pasta>/<slug>/<NN>-<id>.html` (ou `<id>.html` sem `data-task`), com o mesmo CSS, ícones,
seletor de tema e scripts, um link "← Todas as telas" e remove arquivos de telas que sumiram.
**Nunca edite os arquivos separados**: edite o agrupado e rode o script de novo, a cada alteração.

Abra o agrupado com `xdg-open <arquivo>` (Linux) / `open` (macOS) em background; se falhar, só informe
o caminho.

Destino **repositório** ou **outra pasta**: só os `.html` (agrupado + pasta por tela). Pare aqui e vá
para o passo 6.

Destino **Obsidian** (`~/Documents/repositories/obsidian/projects/<Projeto>/prototipos/`), além do `.html`:

1. `<slug>.md` índice: o que é, link local `[<slug>.html](<slug>.html)`, link publicado (só se
   houver), data, e
   **um `##` por tela** com a task linkada (`[[../tasks/<arquivo>|<título>]]`), o arquivo da tela
   (`[Abrir só esta tela](<slug>/<NN>-<id>.html)`) e os bullets de decisão; no fim, `## A confirmar`
   com checkboxes.
2. Em cada task coberta, adicione no topo de `## Referências` (não duplique se já existir):
   `- [[../prototipos/<slug>#<heading>|Protótipo: <heading>]]` e
   `- [Tela isolada: <heading>](../prototipos/<slug>/<NN>-<id>.html)`.
3. Nota raiz do projeto: link para o índice na seção de navegação.
4. Registre a pasta/decisão na nota do projeto em `_knowledge/projects/` (em inglês).

Atualizando um protótipo existente: edite o mesmo `<slug>`, preserve headings e `id` já linkados e
rode o `split-screens.py` de novo. Se a numeração das tasks mudar, atualize os `data-task` e os links.

## 5. Publicar (só se pedido)

Pule este passo, a menos que o usuário tenha pedido explicitamente para publicar. Não ofereça
publicar a cada execução; no máximo mencione uma vez, no fim, que dá para gerar um link.

Quando pedido: gere uma cópia em `$SCRATCHPAD` sem o invólucro (`<!doctype>`, `<html>`, `<head>`,
`<body>` — mantenha `<title>`, `<meta name="claude:…">`, `<link>` e `<style>`) e publique essa cópia
com a ferramenta `Artifact` (carregue as orientações de design dela antes, se ainda não estiverem no
contexto). Para atualizar, republique o mesmo arquivo ou passe a `url` do índice. Se houver índice no
Obsidian, adicione o link publicado nele.

## 6. Entregar

Resposta curta: caminho do arquivo agrupado e da pasta com uma tela por arquivo (e o link, se publicou), o que cada tela mostra (1 linha), e as **decisões que precisam de ok** antes de
virar código. Ofereça transformar os padrões aprovados em rule do projeto
(`.claude/rules/ux-patterns.md`) — só crie se o usuário pedir.
