from pydantic import BaseModel, Field
from datetime import datetime, timezone
from enum import Enum

class CarStatus(BaseModel):
    online: bool
    session : bool
    battery_level: float
    timestamp: datetime 
    
class ConnectionRequest(BaseModel):
    car_id : str
    car_key : str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ConnectionStatus(str, Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    DISCONNECTED = "disconnected"


class ConnectionResponse(BaseModel):
    car_id : str
    status: ConnectionStatus
    timestamp: datetime 