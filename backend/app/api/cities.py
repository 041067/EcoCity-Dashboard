from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.repositories.city_repository import CityRepository
from app.schemas.city import CityResponse

router = APIRouter(prefix="/cities", tags=["Cities"])


@router.get("", response_model=list[CityResponse])
def list_cities(db: Session = Depends(get_db)):
    repo = CityRepository(db)
    return repo.get_all()
