from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.city_repository import CityRepository
from app.repositories.reading_repository import ReadingRepository
from app.schemas.reading import CollectResponse, ReadingResponse
from app.services.weather_service import WeatherService
from app.utils.air_quality import compute_aqi

router = APIRouter(prefix="/readings", tags=["Readings"])


def _to_response(r, city_name: str | None) -> ReadingResponse:
    return ReadingResponse(
        id=r.id,
        city_id=r.city_id,
        city_name=city_name,
        temperature=r.temperature,
        humidity=r.humidity,
        pm25=r.pm25,
        pm10=r.pm10,
        ozone=r.ozone,
        carbon_monoxide=r.carbon_monoxide,
        wind_speed=r.wind_speed,
        uv_index=r.uv_index,
        aqi=compute_aqi(r.pm25),
        created_at=r.created_at,
    )


@router.get("/latest", response_model=list[ReadingResponse])
def get_latest_readings(db: Session = Depends(get_db)):
    reading_repo = ReadingRepository(db)
    readings = reading_repo.get_latest_per_city()

    city_repo = CityRepository(db)
    result = []
    for r in readings:
        city = city_repo.get_by_id(r.city_id)
        result.append(_to_response(r, city.name if city else None))
    return result


@router.get("/history", response_model=list[ReadingResponse])
def get_reading_history(
    city: str | None = Query(None, description="Filter by city name"),
    start_date: date | None = Query(None, alias="start_date"),
    end_date: date | None = Query(None, alias="end_date"),
    db: Session = Depends(get_db),
):
    reading_repo = ReadingRepository(db)
    city_repo = CityRepository(db)

    city_id = None
    if city:
        cities = city_repo.get_all()
        match = next((c for c in cities if c.name.lower() == city.lower()), None)
        if match:
            city_id = match.id

    readings = reading_repo.get_history(city_id=city_id, start_date=start_date, end_date=end_date)

    result = []
    for r in readings:
        c = city_repo.get_by_id(r.city_id)
        result.append(_to_response(r, c.name if c else None))
    return result


@router.post("/collect", response_model=list[CollectResponse])
def collect_readings(db: Session = Depends(get_db)):
    city_repo = CityRepository(db)
    reading_repo = ReadingRepository(db)
    service = WeatherService(city_repo, reading_repo)
    return service.collect_all()
