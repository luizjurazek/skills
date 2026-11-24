---
name: mr-message
description: >-
  Gera a mensagem curta de merge request/branch do monorepo Nexus: link da tarefa
  no Eureka, o que foi feito, o que testar e decisões tomadas. Use sempre que o
  usuário pedir "mensagem de merge", "mensagem da MR", "descrição da MR/PR",
  "descreve a branch" ou colar um nome de branch como feat/99637-... pedindo o texto.
  Para o template longo de review com rastreabilidade de CA, use mr-description.
---

# Mensagem de MR (curta)

Texto enxuto para colar na MR do GitLab. Só quatro blocos, sem tabelas de rastreabilidade.

## 1. Coletar

Rode no repositório alvo (cwd `nexus/`):

```bash
git rev-parse --abbrev-ref HEAD
git log --format='%h %s' $(git merge-base HEAD origin/develop)..HEAD
git diff --stat $(git merge-base HEAD origin/develop)..HEAD | tail -30
git status --short
```

- **Número da tarefa:** o primeiro grupo de dígitos do nome da branch (`feat/99637-mds-...` → `99637`). Sempre da branch, nunca de commit, spec ou conversa. Se a branch não tiver número, pergunte; não invente.
- **Base:** `origin/develop`, a menos que a branch esteja empilhada sobre outra story (commits de outra tarefa no log). Nesse caso descreva só o que está acima dela e trate a story de baixo como dependência (ver abaixo).
- **Dependências:** o usuário pode informar tarefas e/ou MRs de que esta depende (links ou números). Use exatamente o que ele passou. Se o log mostrar commits de outra tarefa e ele não informou o link, **pergunte** antes de escrever; nunca monte link de MR por conta própria, e para tarefa só monte o link do Eureka quando o número foi dado.
- Working tree sujo: pergunte se aquelas mudanças entram na mensagem.
- Se existir spec da tarefa (o usuário costuma indicar a pasta), leia só para extrair decisões e o roteiro de teste; não vire rastreabilidade de CA.

## 2. Escrever

Português, direto, sem enfeite. Use exatamente esta estrutura:

```markdown
**Tarefa:** https://portal.eurekalabs.com.br/tarefa/<NUMERO>

**Depende de:**                                          (omitir se não houver)
- Tarefa <NUMERO-OUTRA>: https://portal.eurekalabs.com.br/tarefa/<NUMERO-OUTRA> — <o que precisa estar pronto>
- MR: <link informado pelo usuário> — <precisa entrar antes porque …>

## O que foi feito
- <mudança em uma linha, com o mecanismo central quando importar>
- <…>

**Fora desta MR:** <o que ficou para outra tarefa, e qual>   (omitir se não houver)

## O que testar
- <ação> → <resultado esperado específico: status, estado, texto>
- <…>
- <caminho de erro principal> → <erro esperado>

## Decisões tomadas
- <decisão e o porquê, em uma ou duas linhas>
```

Regras:
- **Link:** `https://portal.eurekalabs.com.br/tarefa/<NUMERO>`, sempre, com o número da branch.
- **Depende de:** uma linha por dependência, com o link e o motivo curto. Número de tarefa informado vira link do Eureka no mesmo formato; link de MR é copiado como veio. Sem dependência, omita o bloco inteiro (não escreva "Nenhuma"). Se existir dependência em outra MR, deixe isso explícito também em "O que testar" (o que subir/mergear antes).
- **O que foi feito:** de 3 a 8 itens. Descreva comportamento e artefatos centrais, não liste arquivo por arquivo.
- **O que testar:** roteiro executável desta MR. Comece por pré-requisito só se for não óbvio (serviço, porta, env). Inclua pelo menos um caminho de erro. Se os testes automatizados cobrem, diga o comando.
- **Decisões tomadas:** só o que não está escrito na spec ou que se desviou dela, com motivo. Sem decisão, escreva `Nenhuma.`; não preencha com o óbvio.
- **Nunca afirme o que não viu:** não diga que um teste passou se não foi rodado nesta sessão ou não consta nos artefatos. Na dúvida, escreva `não executado`.

## 3. Formato Eureka (só quando pedido)

O campo da Eureka rejeita texto com "caracteres que não sejam alfanuméricos e operadores". Quando o usuário disser que vai colar lá, ou que deu esse erro, entregue a versão em texto puro:

- Sem markdown (`#`, `**`, crases, tabelas), sem acentos, vírgulas, parênteses, aspas, setas e underline (`FOO_BAR` vira `FOO BAR`).
- Só letras, números, espaço, quebra de linha e `- + / = : .` (o link e os caminhos precisam de `:` `/` `.`).
- Títulos em caixa alta, itens com `- `, `→` vira `=`. Os links de dependência continuam inteiros.
- Antes de entregar, confira com `grep -nP '[^A-Za-z0-9 \n\-+/=:.]'` no arquivo: a saída tem que ser vazia.
- Se a Eureka recusar algum desses caracteres, pergunte qual e ajuste esta seção.

## 4. Entregar

Mostre o markdown no chat (é curto) e copie para o clipboard:

```bash
if [ -n "$WAYLAND_DISPLAY" ] && command -v wl-copy >/dev/null; then wl-copy
elif command -v xclip >/dev/null; then xclip -selection clipboard
elif command -v pbcopy >/dev/null; then pbcopy
else echo "sem ferramenta de clipboard"; fi < <arquivo>
```

Grave o texto em `/tmp` ou no scratchpad da sessão, não no repositório. Não commite nada.
Feche dizendo a base usada e o que ficou como dúvida.
