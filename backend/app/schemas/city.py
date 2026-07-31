from datetime import datetime

from pydantic import BaseModel


class CityResponse(BaseModel):
    id: int
    name: str
    state: str
    latitude: float
    longitude: float
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
