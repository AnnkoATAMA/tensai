from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from cruds.user import get_current_user_from_cookie
from models import player as player_model
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db
from .majan.manager.connection_manager import ConnectionManager

game_router = APIRouter()
manager = ConnectionManager()

@game_router.websocket("/room/{room_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket, 
    room_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user_from_cookie)
    ):
    
    user_id = current_user["id"]
    
    result = await db.execute(
        select(player_model.Player)
        .where(player_model.Player.user_id == user_id)
    )

    player = result.scalars().first()
    
    player_id = player.id
    player_name = current_user["name"]
    
    await manager.connect(websocket, room_id, player_id)
    
    game = manager.get_game(room_id)
    
    # player_idがplayersになく、gameが開始していた場合
    if game and player_id not in game.players:
        if game.game_started:
            await manager.send_personal(
                {"error": "ゲームはすでに開始されています"},
                room_id, player_id
            )
            
        # そうでなければプレイヤーを追加
        else:
            game.add_player(player_id, player_name)
            await manager.broadcast(
                {"action": "player_joined", "player_id": player_id, "name": player_name},
                room_id
            )
    
    try:
        while True:
            data = await websocket.receive_json()
            game = manager.get_game(room_id)
            
            if not game:
                await websocket.send_json({"error": "ゲームが見つかりません"})
                continue
                
            # actionを取得
            action = data.get("action")
            
            # actionが"start_game"の場合, start_gameメソッドを実行
            if action == "start_game":
                if game.start_game():
                    await manager.broadcast({"action": "game_started"}, room_id)
                else:
                    await websocket.send_json({"error": "ゲームを開始できません"})
                    
            # actionが"discard"の場合, discard_haiメソッドを実行
            elif action == "discard":
                hai_idx = data.get("hai_idx")
                success, message = game.discard_hai(player_id, hai_idx)
                
                if success:
                    await manager.broadcast({
                        "action": "hai_discarded",
                        "player_id": player_id,
                        "message": message
                    }, room_id)
                else:
                    await websocket.send_json({"error": message})
                    
            # actionが"claim_ron"の場合, claim_ronメソッドを実行
            elif action == "claim_ron":
                success, result = game.claim_ron(player_id)
                
                if success:
                    await manager.broadcast({
                        "action": "ron_claimed",
                        "player_id": player_id,
                        "doubt_available": result.get("doubt_available", False)
                    }, room_id)
                else:
                    await websocket.send_json({"error": result})
                    
            # actionが"claim_doubt"の場合, claim_doubtメソッドを実行
            elif action == "claim_doubt":
                target_id = data.get("target_id")
                success, result = game.claim_doubt(player_id, target_id)
                
                if success:
                    await manager.broadcast({
                        "action": "doubt_result",
                        "doubter_id": player_id,
                        "target_id": target_id,
                        "winner": result["winner"],
                        "reason": result["reason"]
                    }, room_id)
                else:
                    await websocket.send_json({"error": result})
                    
            # actionが"get_game_state"の場合, get_game_stateメソッドを実行
            elif action == "get_game_state":
                await websocket.send_json({
                    "action": "game_state",
                    "game_state": game.get_game_state(player_id)
                })
                
    except WebSocketDisconnect:
        manager.disconnect(room_id, player_id)
        await manager.broadcast({
            "action": "player_disconnected",
            "player_id": player_id
        }, room_id)