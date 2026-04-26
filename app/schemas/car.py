from pydantic import BaseModel, Field
from datetime import datetime, timezone
from enum import Enum

class CarStatus(BaseModel):
    car_id : str
    online: bool
    session : bool
    battery_level: float
    timestamp: datetime 
    
class ConnectionRequest(BaseModel):
    car_id : str
    car_key : str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ConnectionRequestMQTT(BaseModel):
    car_id: str
    timestamp: datetime

class ConnectionStatus(str, Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    DISCONNECTED = "disconnected"


class ConnectionResponse(BaseModel):
    car_id : str
    status: ConnectionStatus
    timestamp: datetime 