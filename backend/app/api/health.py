import logging

import httpx
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import get_db

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "disconnected"

    return {
        "status": "online",
        "database": db_status,
    }


@router.get("/health/database")
def health_database(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception:
        logger.exception("Database health check failed")
        return {
            "status": "error",
            "database": "disconnected",
            "detail": "Unable to verify database connectivity.",
        }


@router.get("/health/external-services")
def health_external_services():
    services = {
        "open_meteo": {
            "status": "not_checked",
        },
        "groq": {
            "status": "configured" if settings.GROQ_API_KEY else "not_configured",
        },
    }

    try:
        response = httpx.get(
            f"{settings.OPEN_METEO_URL}/forecast",
            params={"latitude": -23.55, "longitude": -46.63, "current": "temperature_2m"},
            timeout=5,
        )
        response.raise_for_status()
        services["open_meteo"] = {"status": "ok"}
    except Exception as e:
        services["open_meteo"] = {"status": "error", "detail": str(e)}

    return {"status": "ok", "services": services}
