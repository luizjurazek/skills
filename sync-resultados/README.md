# sync-resultados

Skill do Claude Code que lê notas do Obsidian, gera os campos de resultado e
acrescenta na planilha Google via `scripts/append_rows.py` (sem API paga: a
geração acontece na sessão do Claude Code; o script só fala com o Google Sheets).

## Setup (uma vez)

1. Google Cloud Console: criar projeto, ativar **Google Sheets API**.
2. IAM → Service Accounts: criar conta e baixar a chave JSON.
3. Salvar a chave em `credentials/service-account.json` (ignorada pelo git).
4. Compartilhar a planilha com o e-mail da service account (`client_email` do
   JSON) como **Editor**.
5. `cp .env.example .env` e preencher `SPREADSHEET_ID` e `SHEET_NAME`.
6. Pré-requisito (Debian/Ubuntu): `sudo apt install python3-venv`
7. `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`

## Uso

No Claude Code: `/sync-resultados G10`

Manual: `.venv/bin/python scripts/append_rows.py rows.json [--dry-run]`

## Segurança

`.env`, `credentials/*` e `.venv/` estão no `.gitignore` da raiz do repo.
Confira com `git status` antes de qualquer commit.
