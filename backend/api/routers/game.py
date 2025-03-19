from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from cruds.user import get_current_user_from_cookie
from models import player as player_model
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db
from .majan.manager.connection import ConnectionManager

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
    player_name = current_user["name"]
    
    result = await db.execute(
        select(player_model.Player)
        .where(player_model.Player.user_id == user_id)
    )

    player = result.scalars().first()
    
    player_id = player.id
    
    await manager.connect(websocket, room_id, player_id)
    
    game = manager.get_game(room_id)
    
    # タイムアウトイベントのコールバックを設定
    if game:
        async def on_doubt_timeout(timeout_result):
            await manager.broadcast({
                "action": "doubt_timeout",
                "winner": timeout_result["winner"],
                "reason": timeout_result["reason"]
            }, room_id)
        
        # コールバックを登録
        game.on_doubt_timeout = on_doubt_timeout
    
    # player_idがplayersにない
    if game and player_id not in game.players:
        # ゲームが開始されている場合はエラーを返す
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
            
            #get_gameでroom_idに対応するBinaryMahjongGameを取得
            game = manager.get_game(room_id)
            
            if not game:
                await websocket.send_json({"error": "ゲームが見つかりません"})
                continue
                
            # actionを取得
            action = data.get("action")
            
            # actionが"start_game"の場合, start_gameメソッドを実行
            if action == "start_game":
                # trueが返ってきた場合
                if game.start_game():
                    await manager.broadcast({"action": "game_started"}, room_id)
                else:
                    await websocket.send_json({"error": "ゲームを開始できません"})
                    
          
            # actionが"discard"の場合, discard_haiメソッドを実行
            elif action == "discard":
                hai_idx = data.get("hai_idx")
                success, result = await game.discard_hai(player_id, hai_idx)
                
                if success:
                    await manager.broadcast({
                        "action": "hai_discarded",
                        "player_id": player_id,
                        "message": result.get("message", ""),
                        "ron_available": result.get("ron_available", False),
                        "ron_timeout": result.get("ron_timeout", 0)
                    }, room_id)
                else:
                    await websocket.send_json({"error": result})
                    
            # actionが"tsumo"の場合, claim_tumoメソッドを実行
            elif action == "claim_tumo":
                success, result = await game.claim_tumo(player_id)
                
                if success:
                    
                    player_hand = [hai.str for hai in game.players[player_id].tehai]
                    
                    await manager.broadcast({
                        "action": "tumo_claimed",
                        "player_id": player_id,
                        "doubt_available": result.get("doubt_available", False),
                        "doubt_timeout": result.get("doubt_timeout", 30),
                        "hand": player_hand
                    }, room_id)
                else:
                    await websocket.send_json({"error": result})
                    
            # actionが"claim_ron"の場合, claim_ronメソッドを実行
            elif action == "claim_ron":
                success, result = await game.claim_ron(player_id)
                
                if success:
                    
                    player_hand = [hai.str for hai in game.players[player_id].tehai]
                    
                    await manager.broadcast({
                        "action": "ron_claimed",
                        "player_id": player_id,
                        "doubt_available": result.get("doubt_available", False),
                        "doubt_timeout": result.get("doubt_timeout", 30),
                        "hand": player_hand,
                        "last_hai": str(game.last_discarded_hai) if game.last_discarded_hai else None
                    }, room_id)
                else:
                    await websocket.send_json({"error": result})
                        
            # actionが"claim_doubt"の場合, claim_doubtメソッドを実行
            elif action == "claim_doubt":
                target_id = data.get("target_id")
                success, result = await game.claim_doubt(player_id, target_id)
                
                if success:
                    
                    target_hand = [str(hai) for hai in game.players[target_id].tehai]
                    
                    await manager.broadcast({
                        "action": "doubt_result",
                        "doubter_id": player_id,
                        "target_id": target_id,
                        "winner": result["winner"],
                        "reason": result["reason"],
                        "hand": target_hand
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