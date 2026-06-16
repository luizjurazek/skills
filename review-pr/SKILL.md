---
name: review-pr
description: >-
  Revisa pull requests e branches comparando com a base (develop/main), usando
  o styleguide do repositório (.gemini/styleguide.md), boas práticas e MCP
  GitHub/GitKraken. Use quando o usuário pedir revisão de PR, review de branch,
  avaliar commits vs develop, "revisa essa branch", "revisa meu PR", ou enviar
  link do GitHub (branch ou pull request).
disable-model-invocation: true
---

# Revisão de Pull Request / Branch

Revisão técnica completa no estilo Gemini Code Assist da LiveSEO: commits, diff,
conformidade com styleguide, severidades e nota 0–10. **Toda a resposta em PT-BR.**

---

## 1. Entrada do usuário

Aceitar qualquer um destes formatos:

| Formato | Exemplo |
|---------|---------|
| URL de PR | `https://github.com/org/repo/pull/123` |
| URL de branch | `https://github.com/org/repo/tree/feature/xyz` |
| Branch local/remota | `13627/feat-contacts-config-screen` |
| PR implícito | "revisa minha branch atual" |

Extrair: `organization`, `repository`, `branch` ou `pull_request_id`, `base branch` (padrão: `develop`; se não existir, `main`).

---

## 2. Coleta de contexto (obrigatório)

Executar investigação real — **nunca revisar só de memória**.

### 2.1 Identificar repositório local

Mapear `org/repo` → pasta local (ex.: `liveseo-earth-api`, `liveseo-earth-vue3`, `plataforma`).
Se o repo não estiver clonado, usar MCP ou `gh` para obter diff remotamente.

### 2.2 Obter metadados e diff

**Prioridade 1 — MCP GitKraken (provider GitHub)**

Servidor: `user-eamodio.gitlens-extension-GitKraken`

Antes de chamar, ler o schema JSON em:
`mcps/user-eamodio.gitlens-extension-GitKraken/tools/<tool>.json`

| Ferramenta | Quando usar |
|------------|-------------|
| `pull_request_get_detail` | URL de PR — `provider: "github"`, `pull_request_files: true` |
| `pull_request_get_comments` | Comentários/reviews existentes no PR |
| `repository_get_file_content` | Ler arquivos na branch (`ref`) sem checkout |
| `git_log_or_diff` | Log/diff local quando o repo está clonado |

**Prioridade 2 — GitHub CLI (`gh`)**

```bash
gh pr view <num> --json title,body,baseRefName,headRefName,files,commits
gh pr diff <num>
gh api repos/{owner}/{repo}/compare/{base}...{head}
```

**Prioridade 3 — Git local**

```bash
git fetch origin <base-branch> <head-branch>
git log origin/<base>..origin/<head> --oneline --no-decorate
git log origin/<base>..origin/<head> --format='%h %s%n%b---'
git diff origin/<base>...origin/<head> --stat
git diff origin/<base>...origin/<head>
```

Usar `...` (merge-base) para o diff da PR, não `..`.

### 2.3 Ler styleguide e regras do projeto

Buscar **nesta ordem** (parar no primeiro encontrado + complementar com docs do repo):

| Repo | Styleguide principal | Complementos |
|------|---------------------|--------------|
| `liveseo-earth-api` | `.gemini/styleguide.md` | `CLAUDE.md`, `docs/code-rules/RULES.md`, `.cursor/rules/earth-api-*.mdc` |
| `liveseo-earth-vue3` | `.gemini/styleguide.md` | `.claude/skills/liveseo-vue3-best-practices/SKILL.md`, `CLAUDE.md` |
| `plataforma` | `CLAUDE.md` (se existir) | Padrões Vue 2/JS do código adjacente |

Se o styleguide exigir idioma PT-BR, **toda a revisão deve ser em PT-BR**.

---

## 3. Análise (checklist interno)

Revisar **todos os commits** da branch (não só o último) e **todo o diff**.

### 3.1 Commits

- Mensagens seguem Conventional Commits?
- Escopo coerente com as alterações?
- Commits de merge são neutros; focar nos funcionais.
- Há escopo misto (domínios não relacionados)? Sinalizar.

### 3.2 Conformidade com styleguide

Aplicar critérios **critical / important / optional** do styleguide do projeto.

**NestJS (liveseo-earth-api) — verificar sempre:**

- [ ] Estrutura module/controller/service/repository/dto
- [ ] PrismaReader para leitura, PrismaWriter para escrita
- [ ] `handleError(error, logger, context)` nos catch de controllers/services
- [ ] HttpException com mensagem amigável + `cause` técnico
- [ ] DTOs com class-validator + `@ApiProperty`
- [ ] Swagger: `@ApiTags`, `@ApiOperation`, `@ApiResponse`
- [ ] SQL raw apenas com `Prisma.sql` (nunca template string solta)
- [ ] Sem tipo `any`
- [ ] Guards de permissão em rotas sensíveis
- [ ] Interfaces com prefixo `I` (quando o styleguide exige)

**Vue 3 (liveseo-earth-vue3) — verificar sempre:**

- [ ] `<script setup lang="ts">`, Composition API
- [ ] Sem `any`; tipos em `types.ts`
- [ ] Design tokens (`var(--color-*)`, `var(--space-*)`) — sem cores/px hard-coded
- [ ] `earthApi` vs `legacyApi` corretos
- [ ] Store consome service; componente consome store/composable
- [ ] Rotas com `meta.requiresAuth` / `meta.permissions`

### 3.3 Boas práticas gerais

- Correção lógica e edge cases
- Segurança (input validation, SQL injection, auth, dados sensíveis em logs)
- Performance (N+1, queries desnecessárias, paralelismo)
- Semântica HTTP (status codes corretos)
- Testes ausentes em lógica complexa
- Regressões em código fora do escopo declarado
- Race conditions, acoplamento use case → use case

### 3.4 Profundidade

Para cada achado relevante, ler arquivos adjacentes e padrões existentes no módulo antes de criticar — distinguir bug real de convenção já usada no projeto.

---

## 4. Formato de saída (obrigatório)

### Cabeçalho

```markdown
# Revisão de código — [branch ou PR #N]

**Repositório:** org/repo
**Base:** develop (ou branch informada)
**Commits:** N funcionais (+ merges)
**Arquivos:** +X / −Y linhas
```

### Resumo dos commits

Tabela: hash | escopo | avaliação breve.

### Pontos positivos

Lista objetiva do que está bem feito.

### Problemas encontrados

Para **cada** problema:

```markdown
### [🔴|🟡|🟢] [Severidade]: Título breve

**Localização:** `caminho/arquivo.ts` (~linha N)

**Problema:** O que está errado.

**Por que importa:** Impacto (bug, segurança, manutenção, padrão).

**Solução:** Como corrigir, com exemplo de código se útil.

**Referência:** styleguide, RULES.md ou doc do módulo (se aplicável).
```

Severidades (do styleguide):

| Emoji | Nível | Ação |
|-------|-------|------|
| 🔴 | Crítico | Bloqueia merge |
| 🟡 | Importante | Corrigir ou justificar antes do merge |
| 🟢 | Opcional | Sugestão de melhoria |

### Tabela de conformidade

Resumo sim/não/parcial dos critérios principais do styleguide.

### Pontuação final (obrigatório)

```markdown
---

## 📊 Pontuação de Qualidade do Código

### Nota Geral: X/10 [emoji da escala]

**Classificação:** [Excelente|Bom|Adequado|Precisa de Trabalho|Crítico] — [descrição]

| Categoria | Nota | Peso | Comentário |
|-----------|------|------|------------|
| 🏗️ Arquitetura & Padrões | X/10 | 20% | … |
| 💎 Qualidade de Código | X/10 | 25% | … |
| ⚡ Performance | X/10 | 20% | … |
| 🔒 Segurança | X/10 | 20% | … |
| 🔧 Manutenibilidade | X/10 | 15% | … |

### Pontos fortes
- ✅ …

### Áreas para melhoria
- 🔴 …
- 🟡 …
- 🟢 …

### Recomendações priorizadas
1. **[Prioridade Máxima]** — …
2. **[Prioridade Média]** — …
3. **[Prioridade Baixa]** — …

### Próximos passos
…

### Veredito
[Aprovar | Aprovar com ressalvas | Solicitar alterações] — …
```

Escala de notas:

| Faixa | Label | Emoji |
|-------|-------|-------|
| 9–10 | Excelente | 🌟 |
| 7–8 | Bom | ✅ |
| 5–6 | Adequado | ⚠️ |
| 3–4 | Precisa de Trabalho | ❌ |
| 0–2 | Crítico | 🚫 |

---

## 5. Regras de conduta da revisão

- Escrever **tudo em PT-BR** (títulos, explicações, tabela, veredito).
- Tom profissional, colaborativo e educativo — explicar o **porquê**.
- Ser construtivo; perguntar quando a intenção não estiver clara.
- Citar código existente com formato: ` ```startLine:endLine:filepath ` `
- Não revisar: `node_modules/`, `dist/`, artefatos gerados, `.env` com secrets.
- Não propor refactors fora do escopo da PR salvo impacto direto.
- Não aprovar automaticamente — veredito explícito no final.
- Se não conseguir acessar PR/branch (auth, repo privado), informar o bloqueio e listar o que falta (token, checkout, permissão MCP).

---

## 6. Fluxo resumido

```
1. Parse URL/branch → org, repo, head, base
2. MCP GitHub (pull_request_get_detail) OU gh OU git fetch + diff
3. Ler .gemini/styleguide.md (+ docs complementares do repo)
4. Analisar commits + diff completo vs base
5. Classificar achados (🔴/🟡/🟢) com localização e solução
6. Pontuação 0–10 + veredito
```

---

## 7. Exemplos de invocação

**Usuário:** `Revisa essa branch: https://github.com/agencialiveseo/liveseo-earth-api/tree/13627/feat-contacts`

**Usuário:** `Review PR https://github.com/agencialiveseo/liveseo-earth-vue3/pull/42`

**Usuário:** `Revisa minha PR comparando com develop` (inferir branch/PR do contexto ou perguntar o link)

---

## 8. Instalação e uso

**Local pessoal (todos os projetos):**

```bash
mkdir -p ~/.cursor/skills/review-pr
# Este arquivo: ~/.cursor/skills/review-pr/SKILL.md
```

**No repositório (compartilhado com o time):**

```bash
mkdir -p .cursor/skills/review-pr
# Copiar este SKILL.md para .cursor/skills/review-pr/SKILL.md
```

**Invocar no chat:**

```
@review-pr revisa https://github.com/agencialiveseo/liveseo-earth-api/pull/123
```

ou:

```
Usando review-pr, revisa essa branch vs develop: <link>
```

**Complementos por stack:**

- Frontend Vue 3: também consultar `@liveseo-vue3-best-practices` quando aplicável.
- Backend NestJS: complementar com `docs/code-rules/RULES.md` se o styleguide não cobrir um caso.
