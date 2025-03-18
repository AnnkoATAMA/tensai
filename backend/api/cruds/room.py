from fastapi import Depends, HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import room as room_schema
from models import room as room_model
from models import player as player_model
from models import user as user_model
from cruds.user import get_current_user_from_cookie

async def check_player_existence(
    user_id, room_id, db
    ):
    
    result = await db.execute(
        select(player_model.Player)
        .where(player_model.Player.room_id == room_id)
        .where(player_model.Player.user_id == user_id)
    )
    
    player = result.scalars().first()
    
    return player
    


# /room POST
async def create_room(
    form_data: room_schema.RoomCreate,
    db: AsyncSession,
    current_user: dict = Depends(get_current_user_from_cookie)
    ):

    user_id = current_user["id"]

    result = await db.execute(
        select(player_model.Player)
        .where(player_model.Player.user_id == user_id)
    )

    player = result.scalars().first()

    if player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already in a room"
        )

    room_data = room_model.Room(
        max_players=form_data.max_players,
        game_type=form_data.game_type
    )

    db.add(room_data)
    await db.commit()
    await db.refresh(room_data)

    room_id = room_data.id

    player_data = player_model.Player(
        room_id=room_id,
        user_id=user_id,
    )

    db.add(player_data)
    await db.commit()

    return {
        "id": room_id,
        "max_players": form_data.max_players,
        "game_type": form_data.game_type
    }

# /room GET
async def get_rooms(db: AsyncSession):
    
    result = await db.execute(
        select(room_model.Room)
    )   
    
    rooms = result.scalars().all()
    
    return rooms

#/room/{room_id} PUT
async def update_room(
    room_id: int,
    form_data: room_schema.RoomUpdate,
    db: AsyncSession,
    current_user: dict = Depends(get_current_user_from_cookie)
    ):
    
    user_id = current_user["id"]
    
    player = await check_player_existence(user_id, room_id, db)
    
    if not player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not in this room"
        )
    
    room_data = await db.get(room_model.Room, room_id)
    room_data.game_type = form_data.game_type
    
    await db.commit()
    
    return {
        "id": room_id,
        "max_players": room_data.max_players,
        "game_type": room_data.game_type
    }
    
# /room/{room_id} DELETE
async def delete_room(
    room_id: int, 
    db: AsyncSession,
    current_user: dict = Depends(get_current_user_from_cookie) 
    ):
    
    user_id = current_user["id"]
    
    player = await check_player_existence(user_id, room_id, db)
    
    if not player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not in this room"
        )
    
    room_data = await db.get(room_model.Room, room_id)
    
    result = await db.execute(
        select(player_model.Player).where(player_model.Player.room_id == room_id)
    )
    
    players = result.scalars().all()
    
    for player in players:
        await db.delete(player) 
    
    await db.delete(room_data)
    
    await db.commit()
    
    return {"message": "delete success"}

# /room/{room_id}/join POST
async def join_room(
    room_id: int,
    db: AsyncSession,
    current_user: dict = Depends(get_current_user_from_cookie)
    ):
    
    user_id = current_user["id"]
    
    player = await check_player_existence(user_id, room_id, db)
    
    if player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already in this room"
        )
        
    room_data = await db.get(room_model.Room, room_id)
    if not room_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
        
    result = await db.execute(
        select(player_model.Player)
        .where(player_model.Player.room_id == room_id)
    )
    
    players = result.scalars().all()
    player_count = len(players)
    
    if player_count >= room_data.max_players:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Room is full. Maximum players: {room_data.max_players}"
        )
    
    
    player_data = player_model.Player(
        room_id=room_id,
        user_id=user_id,
    )
    
    db.add(player_data)
    await db.commit()
    
    return {
        "id": room_id,
        "user_id": user_id,
    }
    
# /room/{room_id}/leave DELETE
async def leave_room(
    room_id: int,
    db: AsyncSession,
    current_user: dict = Depends(get_current_user_from_cookie)
    ):
    
    user_id = current_user["id"]
    
    player = await check_player_existence(user_id, room_id, db)
    
    if not player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not in this room"
        )
    
    await db.delete(player)
    await db.commit()
    
    return {"message": "leave success"}


async def get_room_players(room_id: int, db: AsyncSession):
    try:
        result = await db.execute(
            select(player_model.Player.user_id, user_model.User.name)
            .join(user_model.User, user_model.User.id == player_model.Player.user_id)
            .where(player_model.Player.room_id == room_id)
        )
        players = result.fetchall()

        if not players:
            return []

        return [{"user_id": player[0], "username": player[1]} for player in players]

    except Exception as e:
        print(f"Error in get_room_players: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
