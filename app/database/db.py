from sqlmodel import Session, SQLModel, create_engine, select
from models.car import CarStatusDB
from schemas.car import CarStatus
DATABASE_URL = "sqlite:///database.db"

engine = create_engine(DATABASE_URL, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)

def get_car_status(car_id : str ):
    with Session(engine) as session:
        session.exec(select(CarStatusDB))


def save_car_status(car_status: CarStatus):
    with Session(engine) as session:
        db_status = CarStatusDB(**car_status.model_dump())
        session.add(db_status)
        session.commit()