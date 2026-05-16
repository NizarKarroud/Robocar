from pydantic import BaseModel, Field
from typing import Optional

from datetime import datetime, timezone
from enum import Enum
from app.state import CLIENT_ID

class ConnectionRequest(BaseModel):
    car_id : str
    car_key : str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
class ConnectionRequestMQTT(BaseModel):
    car_id: str
    client_id : str
    timestamp: datetime

class ConnectionStatus(str, Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    DISCONNECTED = "disconnected"




class ConnectionResponse(BaseModel):
    car_id : str
    status: ConnectionStatus
    timestamp: datetime 


class CameraRequestType(str, Enum):
    CONNECT = "connection"
    DISCONNECT = "disconnection"


class CameraRequestStatus(str, Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    DISCONNECTED = "disconnected"

class CameraRequest(BaseModel):
    request : CameraRequestType
    client_id: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CameraResponse(BaseModel):
    status : CameraRequestStatus
    car_ip: Optional[str] = None
    port : Optional[str] = None
    path: Optional[str] = None
    timestamp: datetime 


class CommandFollowLine(BaseModel):
    action : str
    client_id: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
