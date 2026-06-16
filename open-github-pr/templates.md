# Templates de PR por repositório

Leia o template do repositório local quando existir (`docs/pull_request_template.md`). Use os modelos abaixo como fallback.

## liveseo-earth-api (e vue3 sem template)

```markdown
# Descrição

{breve_descrição}

## Tipo de Mudança

- [ ] Bugfix (Correção de um erro, ex: ajuste na lógica de autenticação)
- [ ] Patch (Pequena melhoria ou ajuste, ex: otimização de uma consulta SQL)
- [ ] Minor Change (Alteração menor, ex: adição de um novo endpoint)
- [ ] New Feature (Nova funcionalidade, ex: implementação de um sistema de notificações)
- [ ] Refactor (Refatoração de código existente, ex: reorganização de módulos para melhor legibilidade)
- [ ] Major Change (Mudança significativa, ex: migração para uma nova versão de framework)
- [ ] SQL Change (Movimentação ou alteração em scripts SQL, ex: criação de novas tabelas)

## Checklist

- [ ] O código foi testado localmente
- [ ] Documentação foi atualizada (se aplicável)
- [ ] Nenhum erro ou warning no console

## Tarefa Relacionada

{link_tarefa}
```

## plataforma

```markdown
# Descrição

{breve_descrição}

## Tipo de alteração

- [ ] Correção de bug (mudança que corrige um problema)
- [ ] Novo recurso (mudança que adiciona funcionalidade)
- [ ] Mudança de última hora (correção ou recurso que faria com que a funcionalidade existente não funcionasse conforme o esperado)

## Número da tarefa e link

{link_tarefa}

* **Qual é o comportamento atual?**

{comportamento_atual}

* **Qual é o novo comportamento (se esta for uma mudança de recurso)?**

{comportamento_novo}

* **Esta PR necessita de alterações de banco de dados ou de alterações nas outras aplicações (earth-api, plataforma, jupiter, saturno)**

{impacto_outras_apps}
```

## Mapeamento prefixo da branch → tipo (earth-api)

| Prefixo na branch | Marcar checkbox |
|-------------------|-----------------|
| `fix`, `bugfix` | Bugfix |
| `patch` | Patch |
| `chore`, `minor` | Minor Change |
| `feat`, `feature` | New Feature |
| `refactor` | Refactor |
| `major` | Major Change |
| `sql`, `migration`, `db` | SQL Change |

## Mapeamento prefixo da branch → tipo (plataforma)

| Prefixo na branch | Marcar checkbox |
|-------------------|-----------------|
| `fix`, `bugfix`, `hotfix` | Correção de bug |
| `feat`, `feature` | Novo recurso |
| `hotfix` (urgente) | Mudança de última hora |

## Link da tarefa LiveSEO

Formato padrão:

```
https://app.liveseo.com.br/projeto/{projectCode}/task/{taskId}/{subtaskId}
```

- `projectCode`: padrão `CA999` (pedir ao usuário se a branch não indicar outro projeto).
- `taskId` e `subtaskId`: extraídos da branch (ver SKILL.md).

## Comentário na tarefa (MCP liveseo-earth — Fase B)

Somente **após** Fase A concluída com **≥1 URL real** (`create_pull_request` ou PR já existente).

Usar `post_subtask_comment` (comentário **público**).

### Uma PR

```html
<p>Pull Request aberta: <a href="{pr_url}">{pr_url}</a></p>
```

### Várias PRs (mesma branch / mesma tarefa)

**Um único comentário** com todos os links:

```html
<p>Pull Requests abertas:</p>
<ul>
  <li><strong>liveseo-earth-api:</strong> <a href="{url_api}">{url_api}</a></li>
  <li><strong>liveseo-earth-vue3:</strong> <a href="{url_vue3}">{url_vue3}</a></li>
</ul>
```

- Incluir só repos com URL real confirmada pelo MCP GitHub.
- Mesmo `subtaskId` e `projectCode` para todos (extraídos da branch).
