from db import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import room as room_schema
from cruds.user import get_current_user_from_cookie
from cruds import room as room_crud


room_router = APIRouter()

@room_router.post("/room", response_model=room_schema.Room)
async def create_room(
    form_data: room_schema.RoomCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user_from_cookie)
    ):
    
    return await room_crud.create_room(form_data, db, current_user)

@room_router.get("/room")
async def get_rooms(db: AsyncSession = Depends(get_db)):
    return await room_crud.get_rooms(db)

@room_router.put("/room/{room_id}", response_model=room_schema.Room)
async def update_room(
    room_id: int,
    form_data: room_schema.RoomUpdate,
    current_user: dict = Depends(get_current_user_from_cookie),
    db: AsyncSession = Depends(get_db)
    ):
    
    return await room_crud.update_room(room_id, form_data, db, current_user)

@room_router.delete("/room/{room_id}")
async def delete_room(
    room_id: int,
    current_user: dict = Depends(get_current_user_from_cookie),
    db: AsyncSession = Depends(get_db)
    ):
    
    return await room_crud.delete_room(room_id, db, current_user)

@room_router.post("/room/{room_id}/join")
async def join_room(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user_from_cookie)
    ):

    return await room_crud.join_room(room_id, db, current_user)

@room_router.delete("/room/{room_id}/leave")
async def leave_room(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user_from_cookie)
    ):

    return await room_crud.leave_room(room_id, db, current_user)

@room_router.get("/room/{room_id}/players")
async def get_room_players(
    room_id: int,
    db: AsyncSession = Depends(get_db)
    ):

    return await room_crud.get_room_players(room_id, db)