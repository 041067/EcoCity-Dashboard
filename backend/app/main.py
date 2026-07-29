from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.health import router as health_router
from app.core.config import settings

app = FastAPI(
    title="EcoCity Dashboard API",
    description="API do EcoCity Dashboard - Monitoramento Ambiental Inteligente",
    version="0.1.0",
)

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://ecocity-dashboard.vercel.app",
]

if settings.ENVIRONMENT == "development":
    origins.extend([
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
