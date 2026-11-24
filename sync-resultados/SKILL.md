---
name: sync-resultados
description: >-
  Lê as notas do Obsidian de uma empresa/feature, gera os insumos de resultado
  (Problema, Projeto, Solução, Objetivo, Antes, Depois, Impacto) em tom de
  entrevista, grava em resultado.md e acrescenta na planilha Google "Resultados".
  Use quando o usuário pedir para atualizar a planilha de resultados, registrar
  uma entrega ou rodar /sync-resultados <pasta>.
disable-model-invocation: true
---

# Sync de resultados (Obsidian → Google Sheets)

Toda a resposta em PT-BR. Argumento: nome da pasta em `OBSIDIAN_PROJECTS_DIR`
(ex.: `G10`). Sem argumento, listar as pastas e perguntar.

## 1. Configuração

Ler `.env` desta skill (`OBSIDIAN_PROJECTS_DIR`). Se `.env`, `credentials/` ou
`.venv` não existirem, parar e orientar o setup do `README.md`. Nunca abrir nem
exibir o conteúdo do JSON de credenciais.

## 2. Descobrir as entregas e o que falta

Estrutura esperada:

```
<pasta>/features/<feature>/{analise, fontes, tasks, resultado.md}
```

Cada `features/<feature>/` é uma entrega. O estado de sincronização mora no
`resultado.md` da feature (frontmatter `sincronizado`):

| Situação | Ação |
|---|---|
| Sem `resultado.md` | **Pendente**: gerar rascunho (passo 3) |
| `sincronizado: false` ou ausente | Texto já escrito: **enviar** (pular a geração; usar o texto do arquivo) |
| `sincronizado: true` | **Pular**, só informar |

Listar as entregas com a situação de cada uma antes de continuar.

## 3. Gerar o rascunho (só entregas pendentes)

Ler `analise/*requirements*`, regras de negócio, `tasks/README.md` e o índice da
pasta (`<pasta>.md`, `mapa-mental.md`). Criar `resultado.md` a partir de
`_templates/projeto-base/resultado.md` do vault, preenchendo o frontmatter
(`empresa`, `projeto`, `status`) e uma seção por campo.

Tom: **vendável para entrevista**, técnico mas acessível. Começar pelo
resultado/dor de negócio, poucos termos técnicos (sem nomes de procs, tabelas,
endpoints), tecnologia só como apoio. Primeira pessoa na solução ("Projetei…",
"Implementei…") apenas se as notas indicarem que o usuário fez.

Regras de honestidade:
- **Nunca inventar números.** `Economia Mensal (h)`, percentuais e tempos só
  entram se estiverem nas notas ou o usuário informar. Caso contrário, vazio.
- `Antes`/`Depois` vêm só do que as notas descrevem; sem base, vazio.
- `status`: `Concluido` se já entregue/em produção; `Em andamento` caso
  contrário (specs prontas ≠ concluído). Na dúvida, perguntar.
- `empresa` = valor da coluna Empresa da planilha; se ambíguo, perguntar.

## 4. Prévia e aprovação

Mostrar as linhas em tabela legível e **aguardar aprovação/ajustes**. O
usuário pode editar o `resultado.md` à mão; reler o arquivo antes de enviar.
Só avançar com um "ok" explícito.

## 5. Gravar na planilha

Montar o JSON (lista de objetos) a partir do `resultado.md` — chaves exatamente:
`Empresa`, `Problema`, `Projeto`, `Solução Implementada`, `Objetivo`, `Antes`,
`Depois`, `Economia Mensal (h)`, `Impacto para o Negócio`, `Status` — salvar no
scratchpad e rodar a partir da pasta desta skill:

```bash
.venv/bin/python scripts/append_rows.py /caminho/rows.json --dry-run
.venv/bin/python scripts/append_rows.py /caminho/rows.json
```

O script só acrescenta ao fim e pula duplicatas por `Empresa` + `Projeto`; nunca
edita linhas existentes. Ele imprime `ADD (row N): ...` com a linha gravada.
Reportar o resultado fielmente (adicionadas/puladas/erro).

## 6. Registrar no resultado.md

**Somente após o script terminar com sucesso** (nunca em `--dry-run` ou erro),
para cada linha adicionada:

- Frontmatter: `sincronizado: true`, `sincronizado_em: <data de hoje>`,
  `planilha_linha: <N do ADD (row N)>`, `status: <Status enviado>`.
- Acrescentar uma linha na tabela "Registro de sincronização":
  `| <data> | Adicionada | <N> | <Status enviado> |`.

Se o script pular por duplicata, **não** marcar como sincronizado: avisar o
usuário que já existe uma linha com esse Empresa + Projeto e perguntar se é a
mesma entrega (então marcar manualmente com o número da linha informado).

Ao final, mostrar um resumo: entregas adicionadas, puladas e pendentes.
