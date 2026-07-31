# EcoCity — Configuração do GitHub (uma única vez)

Guia para ativar proteção de branches, environments, secrets e Deploy Hooks.
Nenhuma credencial deve ser colocada em YAML, `.env` ou `alembic.ini` no repositório.

---

## 1. Branch Protection (main)

GitHub → Settings → Branches → **Add branch protection rule** → branch `main`:

- [x] Require a pull request before merging
- [x] Require approvals (1)
- [x] Require status checks to pass before merging
  - `Backend CI / Lint, Testes e Migrations`
  - `Frontend CI / Lint, Testes e Build`
  - `CodeQL / Analisar (javascript-typescript)`
  - `CodeQL / Analisar (python)`
- [x] Do not allow bypassing the above settings
- [ ] (opcional) Require conversation resolution

Repita para a branch `develop` se quiser mais rigor.

## 2. Environments (staging + production)

GitHub → Settings → Environments → **New environment**:

### production
| Secret | Valor |
|---|---|
| `DATABASE_URL` | Connection string do Supabase (produção) |
| `RENDER_DEPLOY_HOOK_URL` | Deploy Hook do Render (produção) |
| `VERCEL_DEPLOY_HOOK_URL` | Deploy Hook da Vercel (produção) |

### staging (quando criar infra de staging)
| Secret | Valor |
|---|---|
| `DATABASE_URL` | Connection string do Supabase staging |
| `RENDER_DEPLOY_HOOK_URL` | Deploy Hook do Render staging |
| `VERCEL_DEPLOY_HOOK_URL` | Deploy Hook da Vercel staging |

Regras recomendadas para `production`:
- Required reviewers
- Wait timer (ex.: 1 minuto)

Secrets de ambiente ficam disponíveis apenas para workflows com `environment: production`.

## 3. Secrets (nível repositório)

GitHub → Settings → Secrets and variables → Actions → **New repository secret**:

| Secret | Onde encontrar |
|---|---|
| `GROQ_API_KEY` | painel do Groq (usada pelo backend em runtime) |

`OPEN_METEO_URL` não é segredo (URL pública) — pode ficar como variável `Environment` no Render.

## 4. Deploy Hooks

Ordem garantida no fluxo `Deploy Production`: migration → backend → frontend.
Para isso, o GitHub Actions dispara os deploys via hooks (e não auto-deploy):

### Render (backend)
1. Render → seu Web Service → **Settings** → **Deploy Hooks** → **New Deploy Hook** (branch `main`)
2. Copie a URL → salve como secret `RENDER_DEPLOY_HOOK_URL` no environment `production`
3. Em **Auto-Deploy**: selecione **No** (opcional, mas recomendado para evitar duplo deploy)

### Vercel (frontend)
1. Vercel → Projeto → **Settings** → **Git** → **Deploy Hooks** → crie um hook
2. Copie a URL → salve como secret `VERCEL_DEPLOY_HOOK_URL` no environment `production`
3. Desligue a integração de auto-deploy do GitHub ou configure apenas `develop` (ver nota abaixo)

> **Alternativa mais simples:** manter auto-deploy ligado no Render/Vercel.
> Nesse caso o job `migrate` do workflow ainda roda primeiro, mas Render/Vercel
> começam o build em paralelo — a ordem não é 100% garantida. Os hooks são o caminho
> recomendado quando uma migration adiciona colunas/tabelas que o código novo usa.

## 5. Fluxo de trabalho (Git)

```
main            → produção (protegida, nunca commitar direto)
develop         → integração
feature/*       → desenvolvimento
```

```
feature/nova-feature → PR → CI (backend + frontend + codeql) → merge em develop
develop → PR → CI → merge em main → Deploy Production (migrate → Render → Vercel)
```

## 6. Segurança no repositório

- Dependabot (`.github/dependabot.yml`) — PRs automáticos de dependências às segundas
- CodeQL (`.github/workflows/codeql.yml`) — análise de segurança em PR e push
- GitGuardian (opcional) — detecta secrets commitados

## 7. Rollback

- **Render:** Deployments → ⋯ → **Rollback** (histórico de builds)
- **Vercel:** Deployments → ⋯ → **Promote to Production** (versão anterior)
- **Migrations:** adotar **Expand → Migrate → Contract**:
  - Expand: adicionar coluna/tabela sem remover nada
  - Migrate: backfill dos dados
  - Contract: remover coluna antiga em um deploy posterior

## Checklist final

- [ ] Branch protection em `main` com os 4 checks
- [ ] Environments `production` com `DATABASE_URL`, `RENDER_DEPLOY_HOOK_URL`, `VERCEL_DEPLOY_HOOK_URL`
- [ ] Secret `GROQ_API_KEY` no repositório
- [ ] Deploy Hooks criados no Render e Vercel
- [ ] `.env`, `alembic.ini` e YAMLs sem credenciais (verificar com `git grep`)
- [ ] Primeiro deploy de teste: merge de um PR para `main`
