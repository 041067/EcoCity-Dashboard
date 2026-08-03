
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.sensor_reading import SensorReading
from app.repositories.alert_repository import AlertRepository
from app.repositories.city_repository import CityRepository
from app.repositories.reading_repository import ReadingRepository
from app.schemas.alert import AlertResponse, ScoreResponse
from app.services.alert_service import AlertService
from app.services.score_service import ScoreService
from app.utils.air_quality import compute_aqi

router = APIRouter(tags=["Alerts"])


def _as_score_data(r: SensorReading, aqi: int) -> dict:
    return {
        "temperature": r.temperature,
        "humidity": r.humidity,
        "pm25": r.pm25,
        "wind_speed": r.wind_speed,
        "uv_index": r.uv_index,
        "aqi": aqi,
    }


@router.get("/alerts", response_model=list[AlertResponse])
def list_alerts(city: str | None = Query(None), db: Session = Depends(get_db)):
    alert_repo = AlertRepository(db)
    city_repo = CityRepository(db)

    if city:
        match = next((c for c in city_repo.get_all() if c.name.lower() == city.lower()), None)
        if not match:
            raise HTTPException(status_code=404, detail=f"Cidade não encontrada: {city}")
        alerts = alert_repo.list_by_city(match.id)
    else:
        alerts = alert_repo.list_all()

    result = []
    for a in alerts:
        c = city_repo.get_by_id(a.city_id)
        result.append(AlertResponse(
            id=a.id,
            city_id=a.city_id,
            city_name=c.name if c else None,
            severity=a.severity,
            title=a.title,
            description=a.description,
            created_at=a.created_at,
        ))
    return result


@router.post("/alerts/evaluate")
def evaluate_alerts(city: str | None = Query(None), db: Session = Depends(get_db)):
    reading_repo = ReadingRepository(db)
    alert_repo = AlertRepository(db)
    city_repo = CityRepository(db)
    alert_service = AlertService(alert_repo)

    readings = reading_repo.get_latest_per_city()
    city_match = None
    if city:
        city_match = next((c for c in city_repo.get_all() if c.name.lower() == city.lower()), None)
        if not city_match:
            raise HTTPException(status_code=404, detail=f"Cidade não encontrada: {city}")

    created = []
    for r in readings:
        if city_match and r.city_id != city_match.id:
            continue
        aqi = compute_aqi(r.pm25)
        new_alerts = alert_service.evaluate_reading(r.city_id, _as_score_data(r, aqi))
        created.append({"city_id": r.city_id, "alerts": len(new_alerts)})
    return {"evaluated": len(readings), "created": created}


@router.get("/scores", response_model=list[ScoreResponse])
def list_scores(db: Session = Depends(get_db)):
    reading_repo = ReadingRepository(db)
    city_repo = CityRepository(db)
    score_service = ScoreService()

    readings = reading_repo.get_latest_per_city()
    result = []
    for r in readings:
        city = city_repo.get_by_id(r.city_id)
        aqi = score_service.aqi_from_readings(r.pm25)
        score = score_service.compute_score(
            temperature=r.temperature,
            humidity=r.humidity,
            wind_speed=r.wind_speed,
            aqi=aqi,
            uv_index=r.uv_index,
        )
        classification = score_service.classify(score)
        result.append(ScoreResponse(
            city_id=r.city_id,
            city_name=city.name if city else None,
            state=city.state if city else None,
            score=score,
            classification=classification["classification"],
            symbol=classification["symbol"],
            aqi=aqi,
            temperature=r.temperature,
            humidity=r.humidity,
            wind_speed=r.wind_speed,
            uv_index=r.uv_index,
            created_at=r.created_at,
        ))
    return result
