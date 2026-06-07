# app/models.py
from sqlmodel import SQLModel, Field
from typing import Optional

class RobotSession(SQLModel, table=True):
    __tablename__ = "session"
    id         : Optional[int] = Field(default=None, primary_key=True)
    mode       : str
    started_at : str
    stopped_at : Optional[str] = None

class Telemetry(SQLModel, table=True):
    id         : Optional[int] = Field(default=None, primary_key=True)
    session_id : int            = Field(foreign_key="session.id")
    timestamp  : str
    mode       : str
    d_front    : Optional[float] = None
    d_left     : Optional[float] = None
    d_right    : Optional[float] = None
    d_back     : Optional[float] = None
    left_pwm   : Optional[int]   = None
    right_pwm  : Optional[int]   = None


class Command(SQLModel, table=True):
    id         : Optional[int] = Field(default=None, primary_key=True)
    session_id : int            = Field(foreign_key="session.id")
    timestamp  : str
    mode       : str
    action     : str            # "start" ou "stop"