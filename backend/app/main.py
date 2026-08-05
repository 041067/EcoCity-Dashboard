from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.health import router as health_router
from app.api.router import api_router
from app.core.config import settings
from app.exceptions.database_exception import DatabaseException
from app.exceptions.external_api_exception import ExternalApiException
from app.logs.logger import logger
from app.scheduler.collector import collector


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting EcoCity scheduler")
    collector.start()
    yield
    collector.shutdown()


app = FastAPI(
    title="EcoCity Dashboard API",
    description="API do EcoCity Dashboard - Monitoramento Ambiental Inteligente",
    version="0.3.0",
    lifespan=lifespan,
)


@app.exception_handler(DatabaseException)
async def database_exception_handler(request: Request, exc: DatabaseException):
    logger.error("Database error: %s", exc)
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.exception_handler(ExternalApiException)
async def external_api_exception_handler(request: Request, exc: ExternalApiException):
    logger.error("External API error: %s", exc)
    return JSONResponse(status_code=502, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error: %s", exc)
    return JSONResponse(status_code=500, content={"detail": str(exc)})

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://eco-city-dashboard.vercel.app",
    "https://ecocity-dashboard.onrender.com",
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

app.include_router(health_router)
app.include_router(api_router)

logger.info("EcoCity Dashboard API started")
