---
name: open-github-pr
description: >-
  Abre pull request(s) no GitHub via MCP user-github (única fonte para GitHub),
  sempre contra develop, em um ou vários repositórios com a mesma branch. Relaciona
  a branch entre projetos, abre PR em cada repo e publica comentário público na
  tarefa LiveSEO. Se user-github indisponível, encerra sem fazer nada. Use quando
  pedir abrir PR, PRs em múltiplos repos, "open pr", ou branch 13627/220698-feat-...
disable-model-invocation: true
---

# Abrir Pull Request no GitHub

## Regra zero — MCP GitHub obrigatório

Servidor: **`user-github`**

**Antes de qualquer ação**, chamar `get_me` (ou equivalente) para confirmar que o MCP responde.

| Situação | Ação |
|----------|------|
| MCP `user-github` **indisponível** | **Encerrar imediatamente.** Nenhuma PR, nenhum comentário, **nenhum fallback** (`gh`, GitKraken, shell git). |
| MCP `user-github` **disponível** | Seguir o fluxo abaixo. |

**Antes de cada chamada MCP:** ler o schema em `mcps/user-github/tools/<tool>.json`.

---

## Duas fases (sequenciais)

| Fase | MCP | Escopo |
|------|-----|--------|
| **A — GitHub** | `user-github` | descobrir repos, diff, template, PR por repositório |
| **B — Tarefa** | `user-liveseo-earth` | **um** comentário público com todos os links (**só no final**) |

**Proibido:** inventar URL, afirmar sucesso sem resposta real do `create_pull_request`.

---

## Fluxo resumido

```
0. [user-github] get_me → indisponível? PARAR
1. Parse branch + lista de repositórios (seção 1–2)
2. Para CADA repositório (Fase A em loop):
   a. list_commits → branch existe no remoto?
   b. list_commits + get_commit → contexto do diff
   c. get_file_contents → template (ou templates.md)
   d. list_pull_requests → duplicata? usar URL existente
   e. create_pull_request → guardar URL real (ou pular se já existir)
3. [liveseo-earth] post_subtask_comment com TODAS as URLs reais
4. Responder ao usuário com tabela por repositório
```

---

## 1. Entrada

### Branch (obrigatória)

Nome exato, ex.: `13627/220698-feat-contacts-config-screen`.

### Repositórios (um ou vários)

| Formato | Exemplo | Comportamento |
|---------|---------|---------------|
| **Vários repos explícitos** | `earth-api e vue3, branch 13627/220698-feat-...` | Abrir PR **só** nos repos informados |
| **Lista separada por vírgula/e** | `earth-api, vue3, plataforma — branch X` | Idem |
| **Um repo** | `vue3 branch X` | Um repositório |
| **Só branch** | `13627/220698-feat-contacts-config-screen` | Descobrir **todos** os repos conhecidos onde a branch existir no remoto (seção 2.3) |

**Base:** sempre `develop`.

**Pré-requisito:** a branch deve existir no **remoto** de cada repo processado. Sem push → pular aquele repo e reportar (não abortar os demais).

---

## 2. Identificar repositórios

### 2.1 Alias → GitHub

| Alias / pasta | `owner` / `repo` |
|---------------|------------------|
| `earth-api`, `api` | `agencialiveseo` / `liveseo-earth-api` |
| `vue3`, `earth-vue3` | `agencialiveseo` / `liveseo-earth-vue3` |
| `plataforma` | `agencialiveseo` / `plataforma` |

Repos conhecidos para **descoberta automática** (só branch informada):

`liveseo-earth-api`, `liveseo-earth-vue3`, `plataforma`

### 2.2 Usuário informou repos

Montar lista `{ owner, repo, alias }` a partir dos aliases. Processar **todos** os informados.

### 2.3 Só branch informada — descoberta multi-repo

Para **cada** repo conhecido, via `user-github`:

```
list_commits → owner, repo, sha: "<branch>"
```

| Resultado | Ação |
|-----------|------|
| Commits retornados | Incluir repo na lista |
| Erro / branch inexistente | Excluir repo |
| **0 repos** com a branch | Informar e **encerrar** (sem Fase B) |
| **1+ repos** | Processar todos encontrados |

**Mesma branch, projetos diferentes:** o nome da branch é o **vínculo** entre repos (mesma tarefa LiveSEO, mesmo escopo). Cada repo recebe PR independente com body baseado no **diff daquele repo**.

### 2.4 Ambiguidade

Se o usuário disse "abrir PR" sem branch → **AskQuestion**.

Se descoberta automática retornar muitos repos e o usuário provavelmente queria subset → preferir repos explícitos na invocação; se dúvida, confirmar com AskQuestion.

---

## 3. Parse da branch (comum a todos os repos)

Padrão: `{taskId}/{subtaskId}-{prefixo}-{slug}`

Ex.: `13627/220698-feat-contacts-config-screen`

| Campo | Valor |
|-------|-------|
| `taskId` | `13627` |
| `subtaskId` | `220698` |
| `prefixo` | `feat` |
| `projectCode` | `CA999` (padrão) |

Link da tarefa (único para todos os repos da mesma branch):

```
https://app.liveseo.com.br/projeto/CA999/task/13627/220698
```

---

## Fase A — user-github (loop por repositório)

Repetir **A.1 → A.5** para cada `{ owner, repo }` da lista.

Manter acumulador:

```typescript
interface PrResult {
  repo: string;           // ex.: liveseo-earth-vue3
  status: 'created' | 'existing' | 'skipped' | 'failed';
  url?: string;           // só se created ou existing
  title?: string;
  error?: string;
}
```

### A.1 Branch no remoto

`list_commits` — `sha`: branch.

- Falhou → `status: skipped`, `error: branch não encontrada no remoto`, **próximo repo**.

### A.2 Contexto (por repo)

1. `list_commits` — `sha`: branch.
2. `get_commit` — tip da branch, `detail: "stats"`.

Descrição da PR = diff **deste** repositório. Nunca copiar descrição de outro repo.

### A.3 Template (por repo)

1. `get_file_contents` — `docs/pull_request_template.md`, `ref: develop`.
2. Fallback: [templates.md](templates.md) (vue3 → template earth-api; plataforma → template plataforma).

Preencher: descrição, tipo (prefixo da branch), checklist `[x]`, link da tarefa.

**Omitir:** Passos para Testar, Notas Adicionais, Outras informações.

**Multi-repo no body:** opcional mencionar repos relacionados, ex.: *"Parte de alterações em earth-api + vue3 (mesma branch)."*

### A.4 PR duplicada (por repo)

`list_pull_requests` — `head: agencialiveseo:<branch>`, `base: develop`, `state: open`.

- PR existente → `pull_request_read` (`get`) → `status: existing`, guardar URL, **não** criar outra.
- Nenhuma → seguir A.5.

### A.5 Criar PR (por repo)

`create_pull_request`:

```json
{
  "owner": "agencialiveseo",
  "repo": "liveseo-earth-vue3",
  "title": "feat: contacts config screen",
  "head": "13627/220698-feat-contacts-config-screen",
  "base": "develop",
  "body": "<markdown específico deste repo>"
}
```

- Sucesso → `status: created`, URL da resposta.
- Falha → `status: failed`, `error` da resposta, **próximo repo**.

---

## Fase B — liveseo-earth (uma vez, após Fase A)

Executar **somente se** existir **≥1** URL real (`created` ou `existing`).

Servidor: **`user-liveseo-earth`**

Ferramenta: `post_subtask_comment`

**Um único comentário** listando todas as PRs (mesma tarefa = mesmo `subtaskId`):

```html
<p>Pull Requests abertas:</p>
<ul>
  <li><strong>liveseo-earth-api:</strong> <a href="{url1}">{url1}</a></li>
  <li><strong>liveseo-earth-vue3:</strong> <a href="{url2}">{url2}</a></li>
</ul>
```

Se apenas **1** PR: usar formato simples (ver [templates.md](templates.md)).

- URLs **exatas** do MCP GitHub — nunca inventadas.
- **Não** usar `post_subtask_internal_note`.
- Se liveseo-earth indisponível → informar; PRs já criadas permanecem válidas.
- Se **nenhuma** PR foi criada/encontrada → **não** postar comentário.

---

## Resposta ao usuário

### MCP GitHub indisponível

```markdown
## PRs não criadas

O MCP **user-github** está indisponível. Nenhuma ação foi executada.
```

### Resultado (single ou multi-repo)

```markdown
## PRs — branch `{branch}`

| Repositório | Status | URL |
|-------------|--------|-----|
| liveseo-earth-api | ✅ criada | https://github.com/.../pull/1 |
| liveseo-earth-vue3 | ✅ criada | https://github.com/.../pull/2 |
| plataforma | ⏭️ branch ausente no remoto | — |

**Tarefa:** https://app.liveseo.com.br/projeto/CA999/task/13627/220698
**Comentário na tarefa:** ✅ postado | ⚠️ MCP indisponível | ❌ falhou
```

Status possíveis por repo: ✅ criada | 🔗 já existia | ⏭️ ignorada (branch/erro) | ❌ falhou

Incluir resumo de 1 linha do diff **por repo** processado com sucesso.

---

## Ferramentas user-github

| Etapa | Ferramenta |
|-------|------------|
| Verificar MCP | `get_me` |
| Descobrir branch multi-repo | `list_commits` (por repo) |
| Commits / arquivos | `list_commits`, `get_commit` |
| Template | `get_file_contents` |
| PR duplicada | `list_pull_requests`, `pull_request_read` |
| Criar PR | `create_pull_request` |

---

## Invocação

**Multi-repo explícito:**

```
@open-github-pr abrir PR no earth-api e vue3, branch 13627/220698-feat-contacts-config-screen
```

**Descoberta automática (todos os repos com a branch):**

```
@open-github-pr abrir PRs da branch 13627/220698-feat-contacts-config-screen
```

**Single repo:**

```
@open-github-pr abrir PR no vue3, branch 13627/220698-feat-contacts-config-screen
```

---

## Referência

- Templates, tipos e HTML do comentário: [templates.md](templates.md)
