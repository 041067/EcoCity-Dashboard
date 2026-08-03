from datetime import datetime

from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: int
    city_id: int
    city_name: str | None = None
    severity: str
    title: str
    description: str
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class ScoreResponse(BaseModel):
    city_id: int
    city_name: str
    state: str
    score: float
    classification: str
    symbol: str
    aqi: int
    temperature: float
    humidity: float
    wind_speed: float
    uv_index: float
    created_at: datetime | None = None


class AIReportResponse(BaseModel):
    city: str
    summary: str
    recommendation: str
    created_at: str | None = None


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    message: str
    answer: str
