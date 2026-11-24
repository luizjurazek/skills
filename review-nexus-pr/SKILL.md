---
name: review-nexus-pr
description: >-
  Revisa Pull Requests / Merge Requests do Nexus em busca de problemas reais
  (bugs, regressões, segurança, performance, violações das regras do repositório),
  lendo antes as instruções do projeto (.claude/, .cursor/, .gemini/, CLAUDE.md,
  AGENTS.md etc.) e reportando apenas apontamentos com evidência, classificados em
  Crítico/Alto/Médio/Baixo. Use quando o usuário chamar a skill seguida do link de
  uma PR/MR do Nexus, ou pedir "revisa essa PR/MR", "code review do Nexus",
  "review desse link". Somente revisa; nunca altera arquivos.
---

# Revisão de PR/MR do Nexus

Code review focado em **problemas reais com evidência**. Sem falsos positivos, sem
sugestões estéticas, sem apontamentos especulativos. **Toda a resposta em PT-BR.**

**Somente leitura:** não modifique arquivos, não faça commit/push, não corrija nada,
não comente na PR/MR. A tarefa é revisar e reportar.

---

## 1. Entrada

O usuário envia o **link da PR/MR logo após a chamada da skill**:

| Formato | Exemplo |
|---------|---------|
| MR GitLab | `https://gitlab.com/org/nexus/-/merge_requests/123` |
| PR GitHub | `https://github.com/org/repo/pull/123` |

- Sem link na mensagem: peça o link; não adivinhe a PR/MR nem revise a branch atual por conta própria.
- Link que não seja PR/MR (branch, commit): aceite, mas informe como a base foi determinada.

Extraia: host, `org/repo`, número da PR/MR.

---

## 2. Fluxo (nesta ordem)

### 2.1 Identificar repositório e metadados

Obtenha título, descrição, **branch de origem**, **branch de destino** e lista de arquivos.

```bash
# GitLab (glab instalado; host self-hosted -> GITLAB_HOST)
export GITLAB_HOST=<host>   # ex.: git.copasul.coop.br
glab auth status
glab mr view <num> --repo <org/repo>                 # título, descrição, origem, destino
glab mr view <num> --repo <org/repo> --output json   # source_branch, target_branch, diff_refs
glab mr diff <num> --repo <org/repo>
glab mr view <num> --repo <org/repo> --comments      # discussões já existentes
# GitHub
gh pr view <num> --repo <org/repo> --json title,body,baseRefName,headRefName,files,commits
gh pr diff <num> --repo <org/repo>
```

Para ler a MR como ref local mesmo sem a branch de origem: `git fetch origin refs/merge-requests/<num>/head:refs/remotes/origin/mr-<num>`.

Se `glab auth status` falhar, oriente `glab auth login --hostname <host>` (token com escopo `read_api`). Se a CLI não estiver autenticada/disponível, tente MCP disponível na sessão. Se nada
funcionar, informe o bloqueio e liste o que falta (token, permissão); **não revise de memória**.

### 2.2 Localizar o clone local

O código deve ser lido no **repositório local** (monorepo `nexus/`), não só no diff.

```bash
git -C <repo-local> remote -v
git -C <repo-local> fetch origin <destino> <origem>
```

- Use `git diff origin/<destino>...origin/<origem>` (três pontos, merge-base) como **diff real** da PR/MR; compare com o diff da plataforma.
- **Não faça checkout nem altere a árvore de trabalho** se houver mudanças locais. Leia arquivos da branch de origem com `git show origin/<origem>:<caminho>`, ou use `git worktree add` em diretório temporário do scratchpad (e remova ao final) se precisar navegar pelo código completo.
- Se o clone local não existir ou não tiver a branch, diga isso nas limitações e revise com o que o diff remoto oferecer.

### 2.3 Ler as regras do repositório (obrigatório, antes de analisar)

Inspecione a estrutura **real**; não presuma que algo existe.

```bash
ls -la <repo>/.claude <repo>/.cursor <repo>/.gemini 2>/dev/null
find <repo> -maxdepth 2 \( -name 'CLAUDE.md' -o -name 'AGENTS.md' -o -name 'GEMINI.md' -o -name 'README.md' -o -name 'CONTRIBUTING.md' \) -not -path '*/node_modules/*'
```

Leia, no mínimo, o que existir de:

- `.claude/` (CLAUDE.md, rules, skills, settings, agents)
- `.cursor/` (rules `*.mdc`, `*.md`; respeite `globs`/`alwaysApply` do frontmatter)
- `.gemini/` (styleguide.md, config)
- Raiz: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `README.md`, `CONTRIBUTING.md`, docs de arquitetura/testes/code-rules
- **Ancestrais e vizinhos dos arquivos alterados:** `CLAUDE.md`/`AGENTS.md`/README em cada diretório do caminho até a raiz, e rules cujo `globs` casa com os arquivos modificados

Regras de uso:

- Priorize as instruções **aplicáveis** aos arquivos revisados (por glob/pasta).
- Conflito entre regras: registre o conflito e siga a precedência declarada pelas próprias instruções (mais específico vence o mais geral, salvo indicação contrária).
- Convenção explícita do projeto **vale mais** que preferência genérica. Só a contradiga se houver problema concreto de segurança, correção ou funcionamento.
- Liste, para o resumo, quais arquivos de regra foram efetivamente lidos.

### 2.4 Analisar o diff com contexto

1. Veja `--stat` e leia o diff completo; ignore `node_modules/`, `dist/`, lockfiles, gerados e `.env`.
2. Para cada arquivo relevante, **leia o arquivo inteiro** (versão da origem) e o código relacionado: chamadores, implementações de interfaces, DTOs/tipos, testes, migrations, consumidores de contratos. Não julgue linhas isoladas.
3. Compare com o estado anterior (`git show origin/<destino>:<caminho>`) para separar o que a PR **introduz/agrava** do que já existia.
4. Verifique o impacto, conforme aplicável, em: chamadas e contratos (API, tipos, DTOs, eventos), integrações, persistência/migrations, autenticação, autorização, tratamento de erros, estado e fluxos afetados.
5. Avalie testes existentes/alterados e identifique cenários relevantes sem cobertura **quando houver risco concreto de regressão**.

### 2.5 Validar cada candidato antes de reportar

Para cada possível problema, confirme:

- [ ] Está no código **alterado ou afetado** pela PR (introduzido ou agravado por ela)?
- [ ] Consigo apontar arquivo e linhas exatos, e o fluxo que leva à falha?
- [ ] Há algo no código/regras (guard, validação upstream, convenção do projeto, teste) que já o neutraliza?
- [ ] As condições para ocorrer são realistas?

Se algum item falhar, **descarte** ou, se for risco condicionado a algo não verificável, reporte como risco condicional deixando isso explícito. Comportamento preexistente não é problema da PR, salvo se ela o agravar ou o tornar relevante de novo modo.

---

## 3. O que procurar

Conforme contexto e regras do projeto:

- Bugs lógicos e comportamento incorreto
- Condições de corrida, concorrência, assincronia (promises sem await, ordem de operações)
- Validação, tratamento de erros, gerenciamento de estado
- Autenticação, autorização, exposição de dados sensíveis
- Queries, transações, persistência, migrations, integridade de dados
- Quebra de contrato: APIs, tipos, DTOs, integrações
- Performance com impacto demonstrável (N+1, loops com I/O, queries sem índice em tabela grande)
- Violação de regras arquiteturais/convenções **escritas** no repositório
- Teste ausente/inadequado **só com risco concreto de regressão**
- Casos de borda que produzam falha real

**Não reporte:** estilo/formatação (lint/biome cuidam), preferência pessoal, oportunidade de refatoração, duplicação, falta de abstração, "falta teste" genérico, nomes, ou padrão que o projeto já usa em código adjacente.

**Nunca:** invente requisitos ou regras de negócio; afirme que testes/comandos rodaram sem ter rodado. Se executar algo (ex.: type-check), diga exatamente o quê e o resultado; caso contrário, registre como não executado.

---

## 4. Severidade (obrigatória em todo apontamento)

| Nível | Critério |
|-------|----------|
| **Crítico** | Comprometimento grave de segurança, exposição significativa de dados, corrupção de dados críticos, indisponibilidade ampla ou falha grave em fluxo essencial |
| **Alto** | Bug/falha com impacto significativo em funcionalidade importante, integridade dos dados, segurança ou operação, sem comprometer o sistema inteiro |
| **Médio** | Impacto funcional limitado, falha em cenários específicos, comportamento incorreto recuperável ou risco relevante em parte do sistema |
| **Baixo** | Impacto reduzido, situações pouco frequentes, consequências limitadas, mas ainda um defeito concreto |

A severidade reflete **impacto real, abrangência e condições necessárias**. Não eleve por envolver tecnologia sensível (auth, banco) e não use severidade para estética ou refatoração.

---

## 5. Formato do apontamento (obrigatório, exatamente)

```markdown
**Classificação:** Crítico | Alto | Médio | Baixo

**Arquivo:** `/caminho/absoluto/arquivo.ts:42-48`

**Trecho:**
```ts
// trecho mínimo do código da branch de origem que demonstra o problema
```

**Por que:** causa técnica, condições para ocorrer e consequência prática no sistema.
```

Quando envolver mais de um arquivo (mesma causa raiz = **um único** apontamento):

```markdown
**Classificação:** Alto

**Arquivo:**
- **Origem do problema:** `/caminho/absoluto/arquivo-principal.ts:42-48`
- **Complementares:**
  - `/caminho/absoluto/outro.ts:15-20` — consome o resultado incorretamente.
  - `/caminho/absoluto/servico.ts:70-75` — propaga o comportamento para outra operação.

**Trecho:**
```ts
// /caminho/absoluto/arquivo-principal.ts:42-48 (origem)
// trecho mínimo; inclua trechos dos complementares só se necessários para entender
```

**Por que:** causa raiz, cenário em que ocorre e consequência observável.
```

Regras:

- Caminhos **absolutos reais** do clone local; linhas precisas e restritas ao trecho mínimo que demonstra o problema.
- Linhas devem ser da **versão da branch de origem**. Se não for possível determinar o caminho absoluto ou confirmar as linhas, **não invente**: diga a limitação no próprio apontamento.
- **Trecho:** cite o código real da branch de origem (copiado, não parafraseado), no bloco com a linguagem correta, restrito ao mínimo (em geral 1–10 linhas) que demonstra o problema. Com mais de um arquivo, cite a origem e, só se necessário, os complementares, indicando `arquivo:linhas` em comentário na primeira linha do bloco. Para SQL/migrations, use ```sql.
- O arquivo onde o problema **se origina** vem primeiro, como **Origem do problema**.
- **Por que** diferencia **fato confirmado** de **risco condicional** ("só ocorre se X"), sem rodeios e sem recomendação genérica. Pode citar a regra do repositório violada (arquivo da regra).
- Sem seção de "solução" obrigatória; não reescreva o código da PR. Uma frase de direção só se ela for necessária para entender o problema.

---

## 6. Resposta final

Ordem: **Crítico → Alto → Médio → Baixo**, cada apontamento no formato da seção 5.

Sem apontamentos relevantes: diga diretamente que **nenhum problema foi identificado na revisão**. Não invente apontamentos para preencher.

Feche com:

```markdown
## Resumo da revisão

- **Apontamentos:** Crítico N · Alto N · Médio N · Baixo N
- **PR/MR:** <link> — `<origem>` → `<destino>`
- **Áreas/fluxos afetados:** …
- **Regras do repositório consultadas:** <arquivos lidos>
- **Limitações:** testes/comandos não executados, contexto indisponível, clone local ausente, regras conflitantes, etc.
```

Não declare a PR aprovada, segura ou livre de bugs por não ter encontrado problemas;
a ausência de apontamentos reflete apenas o que foi verificado.

---

## 7. Uso

```
/review-nexus-pr https://gitlab.com/org/nexus/-/merge_requests/123
```

O link vem sempre **depois** da chamada da skill.
