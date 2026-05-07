from pydantic import BaseModel, Field
from datetime import datetime, timezone
from enum import Enum

class ConnectionRequest(BaseModel):
    car_id : str
    car_key : str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

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

class CameraRequest(BaseModel):
    request : CameraRequestType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CameraResponse(BaseModel):
    status : CameraRequestStatus
    timestamp: datetime 
