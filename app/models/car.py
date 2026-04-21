from sqlmodel import Field, SQLModel
from datetime import datetime, timezone
from schemas.car import CarStatus


class CarStatusDB(CarStatus, table=True):  
    __tablename__ = "car_status"
    id: int | None = Field(default=None, primary_key=True)
    timestamp: datetime 