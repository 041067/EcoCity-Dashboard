# EcoCity — Estratégia de Branches

## Modelo

```
main            → produção (protegida)
develop         → integração
feature/*       → desenvolvimento
```

Regra: **nunca desenvolver diretamente na `main`** — push direto bloqueado pela
branch protection (ver `docs/github-setup.md`).

## Fluxo

```
feature/nova-funcionalidade
        │
        ▼
     Pull Request (feature → develop)
        │
        ▼
   GitHub Actions (CI)
        │
   ┌────┴────┐
   │         │
 PASSOU    FALHOU
   │         │
   ▼         ▼
 Merge    Corrigir
   │
   ▼
   develop
   │
   ▼
Pull Request (develop → main)
   │
   ▼
  CI + Review
   │
   ▼
   main
   │
   ▼
Deploy Production (migrate → Render → Vercel)
```

## Comandos

```bash
# Iniciar feature a partir da develop
git checkout develop
git pull
git checkout -b feature/minha-nova-feature

# Ao terminar, abrir PR para develop
git push -u origin feature/minha-nova-feature
```

## O que dispara os pipelines

| Evento | Workflow | Ação |
|---|---|---|
| Push/PR em `develop` ou `main` (backend) | `backend-ci.yml` | lint, testes, migrations |
| Push/PR em `develop` ou `main` (frontend) | `frontend-ci.yml` | lint, testes, build |
| Push/PR em `main` | `codeql.yml` | análise de segurança |
| Merge/push em `main` | `deploy-production.yml` | migration Supabase → Render → Vercel |
| Semanal | Dependabot | PRs de dependências |
