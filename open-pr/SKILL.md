---
name: open-pr
description: >-
  Abre uma merge request no GitLab do Nexus (git.copasul.coop.br/copasul/nexus),
  sempre contra develop, a partir da branch informada. Gera a descrição com a
  skill mr-message, usa o nome da tarefa como título (ex.: "102475: [Melhoria] -
  Melhorar ...") e devolve apenas o link da MR. Use quando o usuário pedir
  "abrir MR", "abre a MR", "open pr", "open mr" ou passar uma branch do Nexus
  como feat/99637-... pedindo para abrir a MR.
disable-model-invocation: true
---

# Abrir MR no Nexus

Repositório fixo: `https://git.copasul.coop.br/copasul/nexus/` (path `copasul/nexus`).
Base fixa: **`develop`**. Nunca outra.

## 1. Entrada

| Dado | Obrigatório | Observação |
|------|-------------|------------|
| Branch | sim | Nome exato, ex.: `feat/102475-melhoria-menus-app`. Se não vier, pergunte. |
| Título | não | Nome da tarefa, ex.: `102475: [Melhoria] - Melhorar a forma que é mostrado o nome dos menus do Aplicativo Copasul`. Usar exatamente como veio. |
| Dependências | não | Tarefas/MRs de que a branch depende; repassar para a mr-message. |

**Título ausente:** gerar a partir da branch, seguindo o padrão do nome das tarefas: `<NUMERO>: [<Tipo>] - <Descrição em português>`.

- `NUMERO`: primeiro grupo de dígitos da branch. Se não houver número, perguntar.
- `Tipo` (pelo prefixo da branch): `feat` → `[Melhoria]` ou `[Funcionalidade]` (usar `[Melhoria]` se a slug indicar ajuste/melhoria de algo existente, `[Funcionalidade]` se for algo novo); `fix` → `[Correção]`; `refactor` → `[Refatoração]`; `chore`/outros → `[Melhoria]`. Prefixo desconhecido: `[Melhoria]`.
- `Descrição`: a slug da branch (sem número, prefixo e siglas de projeto como `mds`) transformada em frase legível em português, primeira letra maiúscula, começando por verbo no infinitivo quando possível (ex.: `menus-app-nome` → `Melhorar a exibição do nome dos menus do Aplicativo`). Pode usar os commits (`git log origin/develop..origin/<branch>`) para deixar a frase mais fiel ao que foi feito.
- Exemplo: `feat/102475-melhoria-nome-menus-app` → `102475: [Melhoria] - Melhorar a forma que é mostrado o nome dos menus do Aplicativo Copasul`.
- Avisar na resposta que o título foi inferido (ver seção 5).

## 2. Pré-checagens (abortar com mensagem curta se falhar)

1. `glab auth status --hostname git.copasul.coop.br` está logado.
2. A branch existe no remoto: `git ls-remote --exit-code --heads origin <branch>`. Se não existir, avisar que falta `git push` e **encerrar**; não fazer push por conta própria.
3. MR duplicada: `glab mr list --repo copasul/nexus --source-branch <branch> --target-branch develop` (ou API). Se já existir MR aberta, **não criar outra**: devolver o link existente.

Rodar os comandos a partir do clone local do nexus (cwd) ou usar sempre `--repo copasul/nexus` / `-R` e a API, para não depender do cwd.

## 3. Descrição (skill mr-message)

Antes de criar a MR, **invocar a skill `mr-message`** com a branch informada (e dependências, se houver) e usar o markdown gerado como descrição.

**Aprovação obrigatória:** depois de gerar a descrição, **mostre o texto completo ao usuário no chat e pare**, aguardando aprovação ou edição. Só siga para a seção 4 (criar a MR) depois de um OK explícito. Se o usuário pedir ajustes, aplique, mostre a versão nova e peça aprovação de novo. A descrição aprovada (com as edições dele) é a que vai para o `glab`. Nunca crie a MR sem essa confirmação.

- A mr-message coleta o diff contra `origin/develop` no repo local. Se o cwd não for o clone do nexus ou a branch não estiver checada, rode a coleta com a branch explícita (`git log origin/develop..origin/<branch>`, `git diff --stat origin/develop...origin/<branch>`) em vez de depender do HEAD.
- Se a mr-message precisar perguntar algo (dependência, working tree sujo, número da tarefa), repasse a pergunta ao usuário antes de abrir a MR.
- Formato Eureka (texto puro) **não** se aplica aqui: o GitLab aceita markdown.
- Não copiar para o clipboard (ignorar a etapa 4 da mr-message); gravar o texto em arquivo no scratchpad da sessão para passar ao `glab`.

## 4. Criar a MR

Só execute após a aprovação da descrição (seção 3).

```bash
glab mr create \
  --repo copasul/nexus \
  --source-branch "<branch>" \
  --target-branch develop \
  --title "<titulo>" \
  --description "$(cat <arquivo-da-descricao>)" \
  --yes
```

Regras:
- `--target-branch develop` sempre.
- Não usar `--squash-before-merge`, `--remove-source-branch`, assignee, labels ou reviewers a menos que o usuário peça.
- Não usar `--fill`: título e descrição vêm desta skill.
- Se `glab mr create` falhar, mostrar o erro real; não tentar de outra forma que mude o alvo (nada de abrir contra outra base).

## 5. Resposta

Devolver **somente o link da MR** (a URL real retornada pelo `glab`), nada de resumo da descrição.

```
https://git.copasul.coop.br/copasul/nexus/-/merge_requests/1234
```

Exceções em que acrescentar uma linha curta antes do link:
- MR já existia → "MR já existente:".
- Título inferido → avisar que não foi informado.

Nunca montar a URL por conta própria nem afirmar sucesso sem a resposta do `glab`.

## Invocação

```
/open-pr feat/102475-melhoria-menus-app
/open-pr feat/102475-melhoria-menus-app título: 102475: [Melhoria] - Melhorar a forma que é mostrado o nome dos menus do Aplicativo Copasul
```
