from sqlalchemy import Column, Integer, String, DateTime, Enum, func
from db import Base

class Room(Base):
    __tablename__ = "rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    max_players = Column(Integer, nullable=False)
    game_type = Column(Enum('sanma', 'yonma'), nullable=False)