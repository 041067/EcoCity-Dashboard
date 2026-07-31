from fastapi import APIRouter

from app.api.cities import router as cities_router
from app.api.health import router as health_router
from app.api.readings import router as readings_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
api_router.include_router(cities_router)
api_router.include_router(readings_router)
