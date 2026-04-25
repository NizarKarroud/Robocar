from sqlmodel import Session, SQLModel, create_engine, select
DATABASE_URL = "sqlite:///database.db"

engine = create_engine(DATABASE_URL, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)

def get_db():
    with Session(engine) as db:
        yield db 
        
