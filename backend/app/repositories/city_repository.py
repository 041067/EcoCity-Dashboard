from sqlalchemy.orm import Session
from app.models.city import City
from app.exceptions.database_exception import DatabaseException
from app.logs.logger import logger


class CityRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_all(self) -> list[City]:
        try:
            return self.db.query(City).order_by(City.name).all()
        except Exception as e:
            logger.error("Failed to fetch cities: %s", e)
            raise DatabaseException("Failed to fetch cities", e)

    def get_by_id(self, city_id: int) -> City | None:
        try:
            return self.db.query(City).filter(City.id == city_id).first()
        except Exception as e:
            logger.error("Failed to fetch city %s: %s", city_id, e)
            raise DatabaseException(f"Failed to fetch city {city_id}", e)

    def get_or_create(self, name: str, state: str, latitude: float, longitude: float) -> City:
        try:
            city = self.db.query(City).filter(City.name == name, City.state == state).first()
            if city:
                return city
            city = City(name=name, state=state, latitude=latitude, longitude=longitude)
            self.db.add(city)
            self.db.commit()
            self.db.refresh(city)
            logger.info("City created: %s/%s", name, state)
            return city
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to create city %s: %s", name, e)
            raise DatabaseException(f"Failed to create city {name}", e)
