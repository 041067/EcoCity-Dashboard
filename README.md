# EcoCity Dashboard 🌿

Monitoramento Ambiental Inteligente — coleta, análise e visualização de dados ambientais urbanos em tempo real, com inteligência artificial.

## Sobre o Projeto

O **EcoCity Dashboard** é uma plataforma que monitora indicadores ambientais urbanos (temperatura, umidade, qualidade do ar, vento, índice UV) em múltiplas cidades. Os dados são coletados automaticamente da **[Open-Meteo](https://open-meteo.com)** (fonte pública e gratuita) a cada 15 minutos e processados por um backend FastAPI, que calcula o **Eco Score** (índice de qualidade ambiental 0–100), gera **alertas inteligentes** e produz **relatórios em linguagem natural** via IA (**Groq**).

### Funcionalidades

- **Dashboard em tempo real** — leituras mais recentes por cidade com cards, gráficos históricos (Recharts) e Eco Score
- **Mapa interativo** — visualização das cidades monitoradas com React-Leaflet e marcadores coloridos por qualidade
- **Relatórios IA** — relatório ambiental em português gerado pela API Groq com base nas últimas 24h de dados
- **Alertas inteligentes** — avaliação automática das leituras com severidades (informativo, atenção, crítico)
- **Comparador de cidades** — compare indicadores ambientais entre municípios
- **Chat ambiental** — assistente virtual que responde perguntas usando os dados monitorados
- **Eco Score** — índice ponderado (AQI, temperatura, umidade, vento, UV) com classificação 🟢 Excelente / 🟡 Moderado / 🔴 Crítico
- **Tema escuro** — alternância de tema via Context API
- **CI/CD completo** — GitHub Actions com lint, testes, build e deploy automático

## Arquitetura

```
┌────────────────────────────────────────────────────────────┐
│                      Frontend (Vercel)                      │
│  React + Vite + TypeScript + Tailwind + Recharts + Leaflet │
│  React Router + React Query + Context API (tema)           │
└──────────────────────────┬─────────────────────────────────┘
                           │ HTTP (Axios)
┌──────────────────────────▼─────────────────────────────────┐
│                      Backend (Render)                       │
│  FastAPI + SQLAlchemy + Alembic + APScheduler + HTTPX      │
│  ─ Scheduler (coleta a cada 15 min)                        │
│  ─ Eco Score + Alertas                                     │
│  ─ Relatórios e chat via Groq API                          │
└──────────────────────────┬─────────────────────────────────┘
                           │ SQLAlchemy
┌──────────────────────────▼─────────────────────────────────┐
│                      Database (Supabase)                    │
│  PostgreSQL — cities, sensor_readings, alerts, ai_reports  │
└────────────────────────────────────────────────────────────┘
                    ┌──────────────┐    ┌──────────────┐
                    │  Open-Meteo  │    │     Groq     │
                    │ (dados clima)│    │   (IA/LLM)   │
                    └──────────────┘    └──────────────┘
```

## Stack

### Backend (`backend/`)
| Componente | Tecnologia |
|---|---|
| Runtime | Python 3.12 |
| Framework | FastAPI 0.115 |
| Servidor | Uvicorn |
| ORM / Migrações | SQLAlchemy 2.0 + Alembic |
| Agendamento | APScheduler (coleta a cada 15 min) |
| Cliente HTTP | HTTPX |
| Validação | Pydantic v2 + pydantic-settings |
| Banco | PostgreSQL (Supabase) / SQLite (dev) |
| Qualidade | Ruff + Pytest |

### Frontend (`frontend/`)
| Componente | Tecnologia |
|---|---|
| UI | React 18 + TypeScript |
| Build | Vite |
| Estilos | Tailwind CSS |
| Dados | @tanstack/react-query + Axios |
| Gráficos | Recharts |
| Mapas | React-Leaflet |
| Roteamento | React Router DOM |
| Testes | Vitest + Testing Library |

### Infraestrutura
- **Supabase** — banco PostgreSQL
- **Render** — deploy do backend
- **Vercel** — deploy do frontend
- **GitHub Actions** — CI/CD (backend-ci, frontend-ci, deploy-production, CodeQL, Dependabot)

## API (prefixo `/api/v1`)

| Método | Rota | Descrição |
|---|---|---|
| GET | `/health` | Status da API e conexão com o banco |
| GET | `/health/database` | Health check do banco |
| GET | `/health/external-services` | Status Open-Meteo e Groq |
| GET | `/cities` | Lista cidades monitoradas |
| GET | `/readings/latest` | Última leitura por cidade |
| GET | `/readings/history` | Histórico (filtros: `city`, `start_date`, `end_date`) |
| POST | `/readings/collect` | Dispara coleta manual Open-Meteo |
| GET | `/scores` | Eco Score calculado por cidade |
| GET | `/alerts` | Lista alertas (filtro: `city`) |
| POST | `/alerts/evaluate` | Reavalia alertas das leituras atuais |
| POST | `/ai/report?city=` | Gera relatório ambiental via Groq |
| GET | `/ai/reports?city=` | Último relatório gerado |
| POST | `/ai/chat` | Chat ambiental com os dados monitorados |

Documentação interativa disponível em `/docs` (Swagger UI).

## Executando Localmente

### Pré-requisitos
- Python 3.12+
- Node.js 20+
- PostgreSQL (ou SQLite para desenvolvimento rápido)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
# .venv\Scripts\Activate.ps1     # Windows

pip install -r requirements.txt
cp .env.example .env             # configure DATABASE_URL e GROQ_API_KEY

alembic upgrade head             # aplicar migrações
uvicorn app.main:app --reload
```

Acesse `http://localhost:8000/docs` (Swagger UI).

**Variáveis de ambiente** (`.env`):

| Variável | Obrigatória | Descrição |
|---|---|---|
| `DATABASE_URL` | Sim (prod) | Connection string PostgreSQL (Supabase). Default: SQLite local |
| `GROQ_API_KEY` | Para IA | Chave da API Groq (relatórios e chat) |
| `OPEN_METEO_URL` | Não | URL base da Open-Meteo (default: `https://api.open-meteo.com/v1`) |
| `ENVIRONMENT` | Não | `development` ou `production` |

### Frontend

```bash
cd frontend
npm install
cp .env.example .env             # configure VITE_API_URL se necessário

npm run dev
```

Acesse `http://localhost:5173`. Configure `VITE_API_URL` com a URL do backend (ex.: `https://ecocity-dashboard.onrender.com`).

### Testes e Qualidade

```bash
# Backend
cd backend
ruff check .                      # lint
ruff check . --fix                # autocorreção
pytest -q                         # testes (conftest, cities, health, readings)

# Frontend
cd frontend
npm run lint                      # ESLint
npm test                          # Vitest
npm run build                     # build de produção (tsc + vite)
```

## Sprint 6 — ESG Foundation

O EcoCity ESG adiciona contexto organizacional ao monitoramento ambiental existente, sem remover ou migrar os dados de `cities`, `sensor_readings`, `alerts` ou `ai_reports`.

```
Organization
├── Sites ──> City ──> Environmental Data
├── Stakeholders
├── ESG Profile
└── ESG Topics (E / S / G)
```

### API ESG (`/api/v1/esg`)

| Método | Rota | Descrição |
|---|---|---|
| POST / GET | `/organizations` | Cria e lista organizações |
| GET / PUT | `/organizations/{id}` | Consulta e atualiza uma organização |
| POST / GET | `/organizations/{id}/sites` | Unidades operacionais com vínculo opcional a City |
| GET / PUT | `/organizations/{id}/profile` | Perfil ESG da organização |
| POST / GET | `/organizations/{id}/stakeholders` | Stakeholders e níveis de influência/impacto |
| GET | `/topics` | Catálogo ESG ativo (E/S/G) |
| POST / GET | `/organizations/{id}/topics` | Temas ESG acompanhados pela organização |
| GET | `/organizations/{id}/overview` | Totais de sites, stakeholders e temas por pilar |

O catálogo inicial contém temas ambientais, sociais e de governança. Os endpoints aparecem automaticamente no Swagger em `/docs`.

### Migração e seed de desenvolvimento

```bash
cd backend
alembic upgrade head
python -m app.database.seed_esg
```

O seed é idempotente e cria a organização demonstrativa **Eco Industries S.A.**, três unidades vinculadas a cidades monitoradas, seis stakeholders e temas ESG selecionados. Não é executado automaticamente em produção.

O frontend fornece `/onboarding` para iniciar a estrutura ESG e `/esg` para o primeiro ESG Overview.

## Sprint 7 — Materiality Engine

A Sprint 7 transforma os temas ESG em avaliações anuais, com trilha de auditoria e cálculo determinístico no backend:

```
Organization → ESG topic + stakeholders → assessment inputs
                                      ↓
             impact + financial + stakeholder materiality
                                      ↓
                  score, priority, evidence and matrix
```

O frontend fornece o wizard em `/esg/materiality`, a matriz interativa de dupla materialidade e o ranking executivo. A matriz usa `Y = impacto`, `X = financeiro` e tamanho da bolha = relevância consolidada dos stakeholders.

O cálculo, escalas, pesos configuráveis, limites, classificação e garantias de histórico estão documentados em [docs/materiality-engine.md](docs/materiality-engine.md).

### API de materialidade (`/api/v1/esg`)

| Método | Rota | Descrição |
|---|---|---|
| POST / GET | `/organizations/{id}/materiality` | Cria ou lista avaliações anuais |
| GET / PUT | `/organizations/{id}/materiality/{assessment_id}` | Consulta ou atualiza uma avaliação não concluída |
| POST / GET | `/materiality/{assessment_id}/stakeholders` | Registra ou lista avaliações de stakeholders |
| GET | `/organizations/{id}/materiality/matrix` | Matriz de dupla materialidade para o ano solicitado ou mais recente |
| GET | `/organizations/{id}/materiality/priorities` | Ranking executivo para o ano solicitado ou mais recente |
| GET | `/organizations/{id}/materiality/{assessment_id}/explanation` | Decompõe score, critérios, evidências e pesos |

Avaliações concluídas são imutáveis. Para preservar o histórico, uma organização cria uma nova avaliação para cada tema e ano de reporte.

## Deploy

### Banco (Supabase)
1. Crie um projeto no [Supabase](https://supabase.com)
2. Copie a `DATABASE_URL` (Connection String do pooler)
3. Defina como variável `DATABASE_URL` no backend

### Backend (Render)
1. Crie um Web Service conectado ao repositório
2. **Build Command:** `pip install -r requirements.txt`
3. **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Configure as variáveis de ambiente no painel (`DATABASE_URL`, `GROQ_API_KEY`, `ENVIRONMENT=production`)

### Frontend (Vercel)
1. Importe o repositório na Vercel
2. **Root Directory:** `frontend`
3. **Build Command:** `npm run build`
4. **Output Directory:** `dist`
5. Configure `VITE_API_URL` com a URL do backend no Render

### CI/CD (GitHub Actions)

O pipeline em `.github/workflows/` executa automaticamente:

- **`backend-ci.yml` / `frontend-ci.yml`** — lint, testes e build em push/PR para `main` e `develop`
- **`deploy-production.yml`** — ao fazer push para `main`: 1) migra o banco (Alembic), 2) dispara deploy hook do Render, 3) dispara deploy hook da Vercel (secrets: `DATABASE_URL`, `RENDER_DEPLOY_HOOK_URL`, `VERCEL_DEPLOY_HOOK_URL`)
- **`codeql.yml`** — análise de segurança
- **`dependabot-auto-merge.yml`** — merge automático de dependências seguras

## Estrutura do Repositório

```
├── .github/workflows/        # CI/CD
├── backend/
│   ├── alembic/              # Migrações do banco
│   ├── app/
│   │   ├── api/              # Rotas (cities, readings, alerts, ai, health)
│   │   ├── clients/          # Clientes externos (Open-Meteo, Groq)
│   │   ├── core/             # Configurações (pydantic-settings)
│   │   ├── database/         # Sessão e Base SQLAlchemy
│   │   ├── exceptions/       # Tratamento de erros
│   │   ├── models/           # Modelos ORM (City, SensorReading, Alert, AIReport)
│   │   ├── repositories/     # Camada de acesso a dados
│   │   ├── scheduler/        # Coletor automático (APScheduler)
│   │   ├── schemas/          # Schemas Pydantic
│   │   ├── services/         # Regras de negócio (weather, score, alert, ai)
│   │   └── utils/            # AQI (faixas EPA)
│   └── tests/                # Testes (pytest)
├── docs/                     # Guias (GitHub setup, Git workflow)
└── frontend/
    └── src/
        ├── components/       # Cards, gráficos, mapa, estado assíncrono
        ├── contexts/         # Tema (dark/light)
        ├── hooks/            # React Query tipado
        ├── layouts/          # Layout da aplicação
        ├── pages/            # Dashboard, Mapa, Relatórios, Alertas, Comparar, Chat
        ├── services/         # Cliente Axios da API
        └── types/            # Tipos TypeScript
```

## Status do Projeto

| Sprint | Escopo | Status |
|---|---|---|
| 1 — Fundação | Repositório, backend FastAPI, frontend React, banco, health check, deploy | ✅ Concluída |
| 2 — Coleta de Dados | Integração Open-Meteo, scheduler periódico, modelos de leituras, persistência | ✅ Concluída |
| 3 — Visualização | Dashboard com gráficos, filtros e períodos, mapa interativo | ✅ Concluída |
| 4 — Inteligência e Alertas | Integração Groq, relatórios IA, sistema de alertas, comparador, chat | ✅ Concluída |
| 5 — Experiência | Páginas completas com tema escuro, React Query, hooks tipados, CI/CD | ✅ Concluída |
| 6 — Fundação ESG | Organizações, unidades, stakeholders, temas e onboarding ESG | ✅ Concluída |
| 7 — Materiality Engine | Avaliação de impacto, financeiro e stakeholders, matriz e ranking | ✅ Concluída |

### Próximos passos
- [ ] Autenticação de usuários
- [ ] Mais fontes de dados (poluição sonora, radiação)
- [ ] Notificações push de alertas
- [ ] Previsão de qualidade do ar com ML

## Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.
