from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database.db import init_db

@asynccontextmanager
def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

