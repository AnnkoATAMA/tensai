from pydantic import BaseModel, Field
from enum import Enum

class GameType(str, Enum):
    SANMA = "sanma"
    YONMA = "yonma"

# basic room infomation
class RoomBase(BaseModel):
    max_players: int = Field(..., title="最大プレイヤー数")
    game_type: GameType = Field(..., title="ゲームタイプ")

# create room
class RoomCreate(RoomBase):
    pass

# return rooms
class Room(RoomBase):
    id: int = Field(..., title="ルームID")
    
class RoomUpdate(BaseModel):
    game_type: GameType = Field(..., title="ゲームタイプ")
    

    