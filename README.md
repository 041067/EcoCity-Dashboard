# EcoCity Dashboard 🌿

Monitoramento Ambiental Inteligente — coleta, análise e visualização de dados ambientais urbanos em tempo real.

## Objetivo

O EcoCity Dashboard é uma plataforma para monitorar indicadores ambientais (qualidade do ar, temperatura, umidade, etc.) utilizando dados públicos da Open-Meteo e inteligência artificial via Groq para gerar relatórios e alertas inteligentes.

## Arquitetura

```
┌────────────────────────────────────────────────────────┐
│                     Frontend (Vercel)                   │
│  React + Vite + TypeScript + Tailwind + Recharts       │
└────────────────────────┬───────────────────────────────┘
                         │ HTTP (Axios)
┌────────────────────────▼───────────────────────────────┐
│                     Backend (Render)                    │
│  FastAPI + SQLAlchemy + APScheduler + HTTPX            │
└────────────────────────┬───────────────────────────────┘
                         │ SQLAlchemy
┌────────────────────────▼───────────────────────────────┐
│                     Database (Supabase)                 │
│  PostgreSQL                                             │
└────────────────────────────────────────────────────────┘
```

## Stack

### Backend
- **Python 3.12** — runtime
- **FastAPI** — framework web
- **Uvicorn** — servidor ASGI
- **SQLAlchemy** — ORM
- **Alembic** — migrações
- **APScheduler** — tarefas agendadas
- **HTTPX** — cliente HTTP assíncrono
- **Pydantic** — validação de dados

### Frontend
- **React 18** — UI
- **Vite** — bundler
- **TypeScript** — tipagem estática
- **Tailwind CSS** — estilos
- **Axios** — requisições HTTP
- **React Router** — roteamento
- **Recharts** — gráficos

### Infraestrutura
- **Supabase** — banco PostgreSQL
- **Render** — deploy do backend
- **Vercel** — deploy do frontend

## Instruções Locais

### Pré-requisitos

- Python 3.12+
- Node.js 20+
- PostgreSQL (ou Supabase)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\Activate.ps1  # Windows

pip install -r requirements.txt
cp .env.example .env
# Edite .env com suas credenciais

uvicorn app.main:app --reload
```

Acesse `http://localhost:8000/docs` (Swagger UI).

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
# Edite .env se necessário

npm run dev
```

Acesse `http://localhost:5173`.

## Deploy

### Backend (Render)

1. Crie um Web Service no Render
2. Conecte ao repositório
3. **Build Command:** `pip install -r requirements.txt`
4. **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Configure as variáveis de ambiente no painel

### Frontend (Vercel)

1. Importe o repositório na Vercel
2. **Root Directory:** `frontend`
3. **Build Command:** `npm run build`
4. **Output Directory:** `dist`
5. Configure `VITE_API_URL` com a URL do backend no Render

### Banco (Supabase)

1. Crie um projeto no [Supabase](https://supabase.com)
2. Copie a `DATABASE_URL` (Connection String) do painel
3. Adicione ao `.env` do backend e às variáveis de ambiente no Render

## Roadmap

### Sprint 1 ✅ — Fundação
- [x] Repositório organizado
- [x] Backend FastAPI funcional
- [x] Frontend React funcional
- [x] Banco PostgreSQL configurado (Supabase)
- [x] Endpoint `/api/health`
- [x] Frontend consumindo backend
- [x] CORS configurado
- [x] Deploy (Render + Vercel + Supabase)

### Sprint 2 — Coleta de Dados
- [ ] Integração Open-Meteo
- [ ] Scheduler para coleta periódica
- [ ] Modelos e tabelas de leituras ambientais
- [ ] Persistência dos dados

### Sprint 3 — Visualização
- [ ] Dashboard com gráficos (Recharts)
- [ ] Filtros e períodos
- [ ] Mapa interativo

### Sprint 4 — Inteligência e Alertas
- [ ] Integração Groq API
- [ ] Relatórios ambientais por IA
- [ ] Sistema de alertas inteligentes
- [ ] Autenticação de usuários

## Licença

MIT
