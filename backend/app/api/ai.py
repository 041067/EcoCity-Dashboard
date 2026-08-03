from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.ai_report_repository import AIReportRepository
from app.repositories.alert_repository import AlertRepository
from app.repositories.city_repository import CityRepository
from app.repositories.reading_repository import ReadingRepository
from app.schemas.alert import AIReportResponse, ChatRequest, ChatResponse
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["AI"])


def _build_service(db: Session) -> AIService:
    return AIService(
        report_repo=AIReportRepository(db),
        reading_repo=ReadingRepository(db),
        alert_repo=AlertRepository(db),
    )


def _resolve_city(db: Session, city: str) -> tuple[int, str]:
    city_repo = CityRepository(db)
    match = next((c for c in city_repo.get_all() if c.name.lower() == city.lower()), None)
    if not match:
        raise HTTPException(status_code=404, detail=f"Cidade não encontrada: {city}")
    return match.id, match.name


@router.post("/report", response_model=AIReportResponse)
def generate_report(city: str = Query(..., description="Nome da cidade"), db: Session = Depends(get_db)):
    city_id, city_name = _resolve_city(db, city)
    result = _build_service(db).generate_report(city_id, city_name)
    if result.get("created_at") is None and result.get("summary", "").startswith("Sem dados"):
        raise HTTPException(status_code=404, detail="Sem dados nas últimas 24 horas para esta cidade")
    return AIReportResponse(**result)


@router.get("/reports", response_model=AIReportResponse)
def get_latest_report(city: str = Query(..., description="Nome da cidade"), db: Session = Depends(get_db)):
    city_id, city_name = _resolve_city(db, city)
    result = _build_service(db).get_latest_report(city_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Nenhum relatório gerado para {city}")
    result["city"] = city_name
    return AIReportResponse(**result)


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    answer = _build_service(db).chat(request.message)
    return ChatResponse(message=request.message, answer=answer)
