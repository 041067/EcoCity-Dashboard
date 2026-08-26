"""Optional, grounded AI endpoints. Core ESG endpoints remain independent of this router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.exceptions.ai_exception import AIRateLimitError, AIUnavailableError
from app.repositories.organization_repository import OrganizationRepository
from app.schemas.ai_copilot import (
    AIRecommendationResponse,
    ApproveRecommendationRequest,
    CopilotChatRequest,
    CopilotChatResponse,
    CreateAIReportRequest,
    ESGReportResponse,
    RecommendationActionResponse,
    RecommendationsResponse,
)
from app.services.ai.copilot_service import ESGCopilotService

router = APIRouter(prefix="/esg/ai", tags=["ESG AI Copilot"])


def _service(db: Session) -> ESGCopilotService:
    return ESGCopilotService(db)


def _organization_or_404(db: Session, organization_id: int) -> None:
    if OrganizationRepository(db).get_by_id(organization_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organização não encontrada")


def _raise_ai_error(error: AIUnavailableError) -> None:
    if isinstance(error, AIRateLimitError):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Limite temporário do Copilot atingido. Tente novamente em instantes.",
        ) from error
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Copilot ESG temporariamente indisponível. Os dados e motores ESG continuam disponíveis.",
    ) from error


@router.post(
    "/organizations/{organization_id}/executive-summary", response_model=ESGReportResponse
)
def generate_executive_summary(organization_id: int, db: Session = Depends(get_db)):
    _organization_or_404(db, organization_id)
    try:
        return _service(db).executive_summary(organization_id)
    except AIUnavailableError as error:
        _raise_ai_error(error)


@router.post("/organizations/{organization_id}/reports", response_model=ESGReportResponse)
def generate_esg_report(
    organization_id: int, payload: CreateAIReportRequest, db: Session = Depends(get_db)
):
    _organization_or_404(db, organization_id)
    try:
        return _service(db).generate_report(organization_id, payload.report_type, payload.reporting_year)
    except AIUnavailableError as error:
        _raise_ai_error(error)


@router.get("/organizations/{organization_id}/reports", response_model=list[ESGReportResponse])
def list_esg_reports(organization_id: int, db: Session = Depends(get_db)):
    _organization_or_404(db, organization_id)
    service = _service(db)
    return [service._report_response(report) for report in service.repository.list_reports(organization_id)]


@router.get("/organizations/{organization_id}/reports/{report_id}", response_model=ESGReportResponse)
def get_esg_report(organization_id: int, report_id: int, db: Session = Depends(get_db)):
    _organization_or_404(db, organization_id)
    service = _service(db)
    report = service.repository.get_report(organization_id, report_id)
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relatório ESG não encontrado")
    return service._report_response(report)


@router.post("/organizations/{organization_id}/recommendations/generate", response_model=RecommendationsResponse)
def generate_recommendations(organization_id: int, db: Session = Depends(get_db)):
    _organization_or_404(db, organization_id)
    try:
        return _service(db).generate_recommendations(organization_id)
    except AIUnavailableError as error:
        _raise_ai_error(error)


@router.get("/organizations/{organization_id}/recommendations", response_model=list[AIRecommendationResponse])
def list_recommendations(organization_id: int, db: Session = Depends(get_db)):
    _organization_or_404(db, organization_id)
    return _service(db).list_recommendations(organization_id)


@router.post(
    "/organizations/{organization_id}/recommendations/{recommendation_id}/dismiss",
    response_model=AIRecommendationResponse,
)
def dismiss_recommendation(organization_id: int, recommendation_id: int, db: Session = Depends(get_db)):
    _organization_or_404(db, organization_id)
    result = _service(db).dismiss_recommendation(organization_id, recommendation_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recomendação pendente não encontrada")
    return result


@router.post(
    "/organizations/{organization_id}/recommendations/{recommendation_id}/create-action",
    response_model=RecommendationActionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_action_from_recommendation(
    organization_id: int,
    recommendation_id: int,
    payload: ApproveRecommendationRequest,
    db: Session = Depends(get_db),
):
    _organization_or_404(db, organization_id)
    result = _service(db).approve_recommendation_as_action(organization_id, recommendation_id, payload)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A recomendação não está disponível para conversão em ação",
        )
    recommendation, action = result
    return {"recommendation": recommendation, "action": action}


@router.post("/organizations/{organization_id}/chat", response_model=CopilotChatResponse)
def copilot_chat(
    organization_id: int, payload: CopilotChatRequest, db: Session = Depends(get_db)
):
    _organization_or_404(db, organization_id)
    try:
        return _service(db).chat(organization_id, payload.question)
    except AIUnavailableError as error:
        _raise_ai_error(error)
