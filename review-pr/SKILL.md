---
name: review-pr
description: >-
  Reviews GitHub pull requests and GitLab merge requests against their base
  branch, fetching real commits and diffs via MCP (GitKraken extension for
  GitHub, mcp-gitlab for GitLab) with gh/glab CLI and local git fallbacks.
  Applies a baked-in, framework-agnostic code-quality checklist (rules.md)
  plus any repo-specific conventions discovered in the target repo (CLAUDE.md,
  .cursor/rules, styleguide docs, CONTRIBUTING.md, linter configs). Produces a
  structured, severity-tagged findings report (pt-BR) with a final verdict.
  Nexus MRs (git.copasul.coop.br/copasul/nexus) are additionally checked
  against the matching spec and business rules in the nexus-analysis repo.
  Use when the user asks to review a PR, review a MR, review a branch, paste a
  github.com or gitlab.com pull/merge request URL, a
  git.copasul.coop.br/copasul/nexus MR/branch URL, or asks to compare a
  branch against its base.
disable-model-invocation: true
---

# Pull Request / Merge Request Review

Technical review of a GitHub PR or GitLab MR: commits, full diff, rule
compliance, severity-tagged findings, and an explicit verdict. The report is
written in Brazilian Portuguese (pt-BR) using the fixed structure in §4; code
comments or snippets suggested in it stay in English.

---

## 1. Input Parsing

Accept any of these:

| Format | Example |
|---|---|
| GitHub PR URL | `https://github.com/org/repo/pull/123` |
| GitHub branch/tree URL | `https://github.com/org/repo/tree/feature/xyz` |
| GitLab MR URL (gitlab.com) | `https://gitlab.com/group/project/-/merge_requests/45` |
| GitLab MR URL (self-managed) | `https://gitlab.company.com/group/subgroup/project/-/merge_requests/45` |
| **Nexus** MR URL | `https://git.copasul.coop.br/copasul/nexus/-/merge_requests/45` |
| **Nexus** branch URL | `https://git.copasul.coop.br/copasul/nexus/-/tree/feat/99961-slug` |
| Local/remote branch name | `feature/xyz` |
| Implicit PR/MR | "review my current branch", "review this PR" |

Extract: `owner/namespace`, `repo/project`, `PR number` or `MR IID` (if a URL
was given), `head branch`, `base branch`.

**Provider detection:**

- URL host is `github.com` → GitHub.
- URL path contains `/-/merge_requests/` (any host — self-managed GitLab uses
  arbitrary domains) → GitLab.
- Only a branch name given → run `git remote -v` in the local repo and infer
  the provider from the remote URL.
- Still ambiguous → ask the user, or fall back to the local-git-only path
  (§2.2/§2.3 priority 3), which doesn't need to know the provider.

**Nexus detection:** the target is a Nexus review when the URL host/path is
`git.copasul.coop.br/copasul/nexus`, or (branch-name-only input) the local
`origin` remote points to that project. Nexus reviews run the extra spec step
in §2.5.

**Base branch:** prefer the value returned in the PR/MR metadata once
fetched. If only a branch name was given and no metadata is available yet,
use the repo's actual default branch (`git remote show origin`) — do not
assume `main`, `master`, or `develop`.

---

## 2. Context & Diff Collection (mandatory)

Run real investigation — **never review from memory.**

### 2.1 Identify local repo

If the target repo is cloned locally (matched by remote URL), prefer it for
the local-git fallback and for reading rule files (§2.4) without extra
network calls. Otherwise fetch everything remotely via MCP/CLI.

### 2.2 GitHub — metadata & diff

**Priority 1 — MCP GitKraken extension**

Server: `user-eamodio.gitlens-extension-GitKraken`

Before calling, read the tool's JSON schema at
`mcps/<server>/tools/<tool>.json`.

| Tool | When to use |
|---|---|
| `pull_request_get_detail` | PR URL — `provider: "github"`, `pull_request_files: true` |
| `pull_request_get_comments` | Existing PR comments/reviews |
| `repository_get_file_content` | Read files at a ref without checkout |
| `git_log_or_diff` | Local log/diff when the repo is cloned |

**Priority 2 — GitHub CLI (`gh`)**

```bash
gh pr view <num> --json title,body,baseRefName,headRefName,files,commits
gh pr diff <num>
gh api repos/{owner}/{repo}/compare/{base}...{head}
```

**Priority 3 — local git**

```bash
git fetch origin <base-branch> <head-branch>
git log origin/<base>..origin/<head> --oneline --no-decorate
git log origin/<base>..origin/<head> --format='%h %s%n%b---'
git diff origin/<base>...origin/<head> --stat
git diff origin/<base>...origin/<head>
```

Use `...` (merge-base diff), not `..`.

### 2.3 GitLab — metadata & diff

**Priority 1 — MCP `zereight/mcp-gitlab`**

Open-source MCP server, typically run via `npx @zereight/mcp-gitlab`,
authenticated with a personal access token, working against gitlab.com or a
self-managed instance (`GITLAB_API_URL`).

> **Caveat:** the server's registered id (commonly `gitlab` or `mcp-gitlab`)
> and its exact tool names vary by install/version. Confirm the real server
> id and tool schemas in your MCP client config before relying on the names
> below — if a named tool doesn't exist, find its closest equivalent among
> that server's actually-registered tools before falling back to priority 2.

Before calling, read the tool's JSON schema at
`mcps/<server>/tools/<tool>.json`.

| Tool (best-guess name — verify) | When to use |
|---|---|
| `get_merge_request` | MR URL/IID — title, description, state, base/head refs |
| `get_merge_request_diffs` | Full diff of the MR |
| `list_merge_request_notes` | Existing comments/discussions |
| `get_file_contents` | Read files at a ref without checkout |
| `get_project` | Resolve project id from namespace/path |

**Priority 2 — GitLab CLI (`glab`)**

```bash
glab mr view <iid>
glab mr diff <iid>
glab api projects/:id/merge_requests/:iid/changes
```

**Priority 3 — local git**

Same mechanics as §2.2 priority 3 — provider-agnostic once you have a remote
and branch names.

### 2.4 Rules & repo-specific conventions

1. Always load the baked-in [rules.md](rules.md).
2. Using whichever fetch mechanism is already active (MCP file-content tool,
   `gh api`, `glab api`, or local `git show`), look at the **head ref** for,
   collecting all that exist:
   1. `CLAUDE.md`
   2. `.cursor/rules/*.mdc`
   3. `.gemini/styleguide.md`
   4. `CONTRIBUTING.md`
   5. `docs/**/style*guide*`, `docs/**/*conventions*`
   6. Linter/formatter configs as a **weaker signal only**
      (`.eslintrc*`, `.prettierrc*`, `ruff.toml`/`pyproject.toml [tool.ruff]`,
      `.rubocop.yml`, etc.) — used to infer style expectations, not enforced
      rule-by-rule.
3. Anything found **supplements / takes precedence over** `rules.md` on
   topics it covers; where the repo is silent, `rules.md` still applies.
4. If nothing is found, proceed with `rules.md` alone and say so explicitly
   in the output header (e.g. "Rules applied: rules.md (baked-in); no
   repo-specific conventions found").

### 2.5 Nexus only — spec & business rules (nexus-analysis)

Skip this section for non-Nexus targets.

1. **Extract the task number** from the head branch name (e.g.
   `feat/99961-some-slug` → `99961`). If the input was an MR URL, take the
   branch name from the MR metadata. If there is no number in the branch,
   try the MR title/description (Eureka link) before giving up.
2. **Locate the spec** in the local `nexus-analysis` repo
   (`/home/jurazek/Documents/repositories/nexus-analysis`; if the path
   doesn't exist, ask the user for it). Specs live at
   `<area>/<analysis-id>-<slug>/3-specs/<task-id>-<slug>.md`, and many only
   exist on `docs/<id>-*` branches, so search in this order:
   1. Working tree: `find . -path ./.git -prune -o -name '<task-id>-*' -path '*3-specs*' -print`
   2. Other branches (no checkout, read-only):
      `git branch -a | grep <task-id>`, then
      `git ls-tree -r --name-only <branch> | grep '3-specs/<task-id>-'` and
      `git show <branch>:<path>`
   3. Parent analysis: if the number is the analysis id rather than the story
      id, read the `3-specs/` folder and `*.requirements.md` of that analysis
      and pick the spec(s) matching the MR scope.
   Never `git checkout`/`switch` in nexus-analysis — use `git show`.
3. **Read the spec fully**: acceptance criteria (CA), business rules,
   formulas, edge cases, API contract, permissions. Also read the sibling
   `*.requirements.md` when a rule references it.
4. **Business-rule conformance** becomes part of the review: for each CA/rule,
   check the diff implements it; report deviations, missing CAs, behavior the
   spec doesn't ask for, and contradictions between spec and code. Business-rule
   violations are rated by user/data impact (§4 levels), not by code style.
5. **No spec found** → say so in the header ("Spec: not found — searched
   working tree and branches for `<task-id>`") and continue with the generic
   review. Never invent spec content.
6. Also load the Nexus repo conventions per §2.4 (`CLAUDE.md`,
   `.cursor/rules/*.mdc`, `.claude/`, `AGENTS.md`) from the head ref.

---

## 3. Analysis Checklist

- Review **all commits** in the branch, not just the last one, and the
  **full diff**, not a sample.
- Apply [rules.md](rules.md) systematically, category by category.
- Before flagging something, read adjacent files and existing patterns in the
  module — distinguish a real defect from an already-established repo
  convention.
- Nexus: also trace every acceptance criterion / business rule of the spec to
  the diff (§2.5) and review tests against those criteria.
- Flag mixed/unrelated scope, but don't propose refactors outside the PR/MR's
  stated scope unless there's direct correctness or security impact.

---

## 4. Output Format

The report is always structured, in pt-BR, with the fields below. Do not add
free-form prose findings outside this structure.

### Header

```markdown
# Code Review — <repo/project> <PR #N | MR !N | branch>

**Provider:** GitHub | GitLab (Nexus)
**Link:** <url>
**Base → Head:** <base> ← <head>
**Commits revisados:** N
**Arquivos alterados:** +X / −Y linhas
**Regras aplicadas:** rules.md (baked-in) + <repo-specific files found, or "nenhuma encontrada">
**Spec (Nexus):** <path/branch of the spec in nexus-analysis | "não encontrada" | "n/a">
```

### Resumo do que foi feito

Right after the header and before any finding, add a short summary so the
reader has context to evaluate the findings:

```markdown
## Resumo da mudança

**Objetivo:** 1–2 sentences — what the PR/MR/branch delivers and why (from
title, description, commits and, for Nexus, the spec).
**O que foi feito:** 3–6 bullets grouped by area (backend, frontend,
migrations, tests, config...), each naming the main files/modules touched.
**Fora do escopo / observações:** only if relevant (unrelated changes mixed
in, stacked branch, partial delivery of the spec).
```

Base it on what was actually read in the diff and commits — never on the
title alone. Keep it neutral (describe, don't judge); judgments belong in
the findings.

### Findings

Ranked from highest to lowest level. One block per finding, all fields
mandatory except **Sugestão**. Findings are **numbered sequentially** (1, 2,
3...) in the order they appear, and each heading starts with the severity icon
(🔴 Alto, 🟡 Médio, 🟢 Baixo — see the levels table). The numbering is global
across levels (do not restart per level), so the reader can reference a
finding as "problema #3".

````markdown
### <icon> #<N> — <short title>

**Nível:** 🔴 Alto | 🟡 Médio | 🟢 Baixo
**Arquivo e linha:** `path/to/file.ts:123` (or `:123-130`)
**Por quê:** the rule, spec criterion (cite CA / section of the spec) or
principle being violated — one line.
**Explicação básica:** 2–4 sentences, plain language: what happens, in which
scenario, and the impact.

**Onde está o problema:**
```ts
// real excerpt from the diff, with the problematic line(s) visible
```

**Sugestão de melhoria:** (only when cheap — see below)
```ts
// proposed code
```
````

Rules for the fields:

- **Arquivo e linha** must come from the real diff/file read; never guess.
- **Onde está o problema** must be a real excerpt (trim to the relevant
  lines, keep enough context to be recognizable).
- **Sugestão de melhoria**: include it whenever the fix is local and obvious
  (a few lines, no cross-file investigation). If a good fix would require
  heavy analysis (broad refactor, multiple files, design decision, extra
  investigation), omit the field entirely — do not write a vague or
  speculative suggestion.
- For spec/business-rule findings, "Por quê" must quote or reference the
  spec criterion and say how the code diverges.

Levels:

| Ícone | Nível | Meaning |
|---|---|---|
| 🔴 | Alto | Bug, security hole, data-loss risk, or business-rule/CA violation — blocks merge |
| 🟡 | Médio | Should be fixed or explicitly justified before merge (regression risk, missing test for a CA, perf, convention violation) |
| 🟢 | Baixo | Non-blocking improvement or style suggestion |

Right before the findings, add a short numbered index so the reader can scan
everything at a glance:

```markdown
## Índice de problemas

1. 🔴 <short title> — `path/file.ts:123`
2. 🟡 <short title> — `path/file.ts:45`
3. 🟢 <short title> — `path/file.ts:9`
```

### Closing

```markdown
---
**Resumo:** 🔴 N alto · 🟡 N médio · 🟢 N baixo.
**Cobertura da spec (Nexus):** CAs atendidos / divergentes / não encontrados no diff (only for Nexus with spec)
**Veredito:** Aprovar | Aprovar com ressalvas | Solicitar mudanças — one-sentence justification.
```

If there are no findings, state "Nenhum problema encontrado" explicitly and
still give a verdict (Aprovar) — never omit the verdict line.

---

## 5. Conduct Rules

- Report in pt-BR (code comments in suggested snippets stay in English), professional and constructive tone — explain the *why*.
- Never review `node_modules/`, `dist/`, generated artifacts, or files
  containing secrets (e.g. `.env`).
- Cite real code in the **Onde está o problema** block; the line reference goes in **Arquivo e linha**.
- Never invent findings or line numbers — only report what was actually read.
- Don't propose out-of-scope refactors unless directly relevant to
  correctness or safety.
- Never silently auto-approve — always emit an explicit verdict.
- If access is blocked (auth, private repo, MCP unavailable), state the
  blocker explicitly and list exactly what's missing (token, MCP server,
  checkout, permission) instead of guessing or fabricating a review.

---

## 6. Summarized Flow

```
1. Parse URL/branch → provider, owner/repo, head, base
2. Detect provider (URL host/path shape, or git remote)
3. Fetch diff+metadata: MCP (GitKraken for GitHub / mcp-gitlab for GitLab) → CLI (gh/glab) → git fetch+diff
4. Load rules.md + discover repo-specific conventions (§2.4)
5. Nexus only: task number from branch → find spec in nexus-analysis → read CAs/business rules (§2.5)
6. Analyze all commits + full diff against the checklist (+ spec for Nexus)
7. Write the change summary, then rank findings 🔴 Alto / 🟡 Médio / 🟢 Baixo, numbered sequentially, using the structured block (§4)
8. Emit header + change summary + numbered index + findings + closing summary + verdict
```

---

## 7. Invocation Examples

**User:** `Review this PR: https://github.com/org/repo/pull/123`

**User:** `Review this MR: https://gitlab.com/group/project/-/merge_requests/45`

**User:** `Review this MR: https://gitlab.company.com/group/subgroup/project/-/merge_requests/45`

**User:** `Review this MR: https://git.copasul.coop.br/copasul/nexus/-/merge_requests/45` (Nexus → also checks the spec in nexus-analysis)

**User:** `Review my current branch against main`

**User:** `Review feature/xyz` (infer provider from `git remote -v`)

---

## 8. Installation & Usage

**Personal (all projects):**

```bash
mkdir -p ~/.cursor/skills/review-pr
# This file: ~/.cursor/skills/review-pr/SKILL.md
# Plus: ~/.cursor/skills/review-pr/rules.md
```

**In-repo (shared with the team):**

```bash
mkdir -p .cursor/skills/review-pr
# Copy this SKILL.md and rules.md into .cursor/skills/review-pr/
```

**Invoke in chat:**

```
@review-pr review https://github.com/org/repo/pull/123
```

or:

```
Using review-pr, review this branch vs main: <link>
```

---

## 9. Caveats & Assumptions

- The GitLab MCP server's exact registered id and tool names
  (`get_merge_request_diffs` vs `list_merge_request_diffs`,
  `list_merge_request_notes` vs `get_merge_request_notes`, etc.) vary by
  install/version of `zereight/mcp-gitlab`. Confirm them in your MCP client
  config rather than assuming the names in §2.3 are exact.
- Self-managed GitLab detection via the `/-/merge_requests/` URL path is a
  best-effort heuristic, not a guarantee — ask the user if the provider is
  unclear.
