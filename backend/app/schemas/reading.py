from pydantic import BaseModel
from datetime import datetime


class ReadingResponse(BaseModel):
    id: int
    city_id: int
    city_name: str | None = None
    temperature: float
    humidity: float
    pm25: float
    pm10: float
    ozone: float
    carbon_monoxide: float
    wind_speed: float
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class CollectResponse(BaseModel):
    city: str
    state: str
    reading_id: int
    temperature: float
    humidity: float
    pm25: float
    pm10: float
    ozone: float
    carbon_monoxide: float
    wind_speed: float
    created_at: str | None = None
