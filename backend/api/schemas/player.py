from pydantic import BaseModel, Field
from enum import Enum

class Status(str, Enum):
    WAITING = "waiting"
    READY = "ready"
    PLAYING = "playing"
    DISCONNECTED = "disconnected"


class Player(BaseModel):
    id: int = Field(..., title="プレイヤーID")
    name: str = Field(..., title="プレイヤー名")
    

class PlayerUpdate(BaseModel):
    name: str = Field(..., title="プレイヤー名")
    
