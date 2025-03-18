from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from cruds.user import get_current_user_from_cookie
from models import player as player_model
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db
from .majan import taku, janshi
from typing import Any, Dict
import random



game_router = APIRouter()


# ゲーム状態を管理するクラス
class BinaryMahjongGame:
    def __init__(self, room_id: str):
        self.room_id = room_id
        self.taku = taku.Taku(aka=True)
        self.players = {}  
        self.player_seats = {}  
        self.current_turn_idx = 0
        self.game_started = False
        self.game_finished = False
        self.winner = None
        self.last_discarded_hai = None
        self.last_action_player = None
        self.doubt_available = False
        self.ron_player = None
        
        
        # プレイヤーを追加
    def add_player(self, player_id: str, name: str) -> bool:
        
        if len(self.players) >= 4:
            return False
            
        if len(self.players) == 0:
            player = janshi.Janshi(play=True, first=True)
        else:
            player = janshi.Janshi(play=True)
        player.name = name
        
        # 現在のプレイヤーの人数によって座席位置を決定
        seat_position = len(self.players)
        self.player_seats[player_id] = seat_position
        self.players[player_id] = player
        
        return True
        
        # ゲームを開始する
    def start_game(self) -> bool:
        
        if len(self.players) < 2 or self.game_started:
            return False
            
        random.shuffle(self.taku.yama)
        
        # 配牌
        for player_id, player in self.players.items():
            player.haipai(self.taku.yama)
            player.riipai()
            
        self.current_turn_idx = 0
        self.game_started = True
        
        return True
    

    def get_current_player_id(self) -> str:
        for player_id, position in self.player_seats.items():
            if position == self.current_turn_idx:
                return player_id
        return None
        
        # 牌を捨てる
    def discard_hai(self, player_id: str, hai_idx: int) -> tuple[bool, str]:
        
        # ゲームが開始されていないか、終了している場合はfalseを返す
        if not self.game_started or self.game_finished:
            return False, "ゲームは、開始されていないか終了しています"
        
        # 手番でないプレイヤーが牌を捨てようとした場合はfalseを返す。
        player_position = self.player_seats.get(player_id)
        if player_position != self.current_turn_idx:
            return False, "あなたの手番ではありません"
            
        player = self.players[player_id]
        
        # 無効な牌のインデックスの場合はfalseを返す
        if hai_idx < 0 or hai_idx >= len(player.tehai):
            return False, "無効な牌のインデックスです"
            
        # 牌を捨てる
        discarded_hai = player.dahai(hai_idx)
        
        # 最後に捨てた牌と捨てたプレイヤーを記録
        self.last_discarded_hai = discarded_hai
        self.last_action_player = player_id
        
        # 次の手番へ
        self.current_turn_idx = (self.current_turn_idx + 1) % len(self.players)
        
        # 次のプレイヤーにツモさせる
        next_player_id = self.get_current_player_id()
        if next_player_id:
            next_player = self.players[next_player_id]
            if len(self.taku.yama) > 0:
                next_player.tsumo(self.taku.yama)
                next_player.riipai()
            else:
                # 山がなくなったら流局
                self.game_finished = True
                return True, "流局"
                
        return True, "牌を捨てました"
        
        # ロンの宣言
    def claim_ron(self, player_id: str) -> tuple[bool, Any]:
        
        # ゲームが開始されていないか、終了している場合はfalseを返す
        if not self.game_started or self.game_finished:
            return False, 
            
        # 手番でないプレイヤーがロンを宣言しようとした場合はfalseを返す
        if self.last_action_player == player_id:
            return False, 
        
        # ロン宣言をしたプレイヤーを格納
        player = self.players[player_id]
        
        # バイナリ麻雀では、ロン宣言は自由だがダウト可能
        self.doubt_available = True
        
        # ロン宣言をしたプレイヤーを記録
        self.ron_player = player_id
        
        # 内部的にロン可能か確認（クライアントには知らせない）
        is_ron_valid = player.can_ron(self.last_discarded_hai)
        
        return True, {
            "doubt_available": True,
            "is_ron_valid": is_ron_valid  # 内部でのみ使用
        }
        
        # ロン宣言に対してダウトを宣言  
    def claim_doubt(self, doubter_id: str, target_id: str) -> tuple[bool, Any]:
        
        # doubt_availableがFalseの場合はfalseを返す
        if not self.doubt_available:
            return False, "ダウトできません"
            
        # 自分自身がdoubterの場合はfalseを返す
        if doubter_id == target_id:
            return False, "自分自身にダウトできません"
            
        # ロン宣言をしてない人にダウトをしようとしたらfalseを返す
        if target_id != self.ron_player:
            return False, "ロン宣言をしていないプレイヤーにダウトできません"
            
        target_player = self.players[target_id]
        
        # ロンが実際に可能かどうか確認
        is_ron_valid = target_player.can_ron(self.last_discarded_hai)
        
        if is_ron_valid:
            # ロン成立ならダウト失敗、ロン宣言者の勝ち
            self.game_finished = True
            self.winner = target_id
            return True, {
                "winner": target_id,
                "reason": "ロン成立、ダウト失敗"
            }
        else:
            # ロン不成立ならダウト成功、ダウト宣言者の勝ち
            self.game_finished = True
            self.winner = doubter_id
            return True, {
                "winner": doubter_id,
                "reason": "ロン不成立、ダウト成功"
            }
    
    def get_game_state(self, viewer_id: str = None) -> dict:
        """ゲーム状態を取得"""
        state = {
            "room_id": self.room_id,
            "game_started": self.game_started,
            "game_finished": self.game_finished,
            "current_turn": self.current_turn_idx,
            "current_player_id": self.get_current_player_id(),
            "hai_left": len(self.taku.yama),  
            "dora_indicator": self.taku.dora_hyouji[0].str if self.taku.dora_hyouji else None,
            "players": {},
            "doubt_available": self.doubt_available,
            "ron_player": self.ron_player
        }
        
        # もしwinnerがいれば、勝者を記録
        if self.winner:
            state["winner"] = self.winner
           
        # プレイヤー本人を取得
        for player_id, player in self.players.items():
            is_viewer = (player_id == viewer_id)
            
            # そのプレイヤーの名前、座席、これまでに捨てた牌を取得
            player_state = {
                "name": player.name,
                "seat": self.player_seats[player_id],
                "discarded": [hai.str for hai in player.kawa] 
            }
            
            # 自分の手牌は表示するが、他者の手牌は非表示
            if is_viewer:
                player_state["hand"] = [hai.str for hai in player.tehai] 
                
            state["players"][player_id] = player_state
            
        # 最後に捨てられた牌の情報
        if self.last_discarded_hai:
            state["last_discarded_hai"] = self.last_discarded_hai.str
            state["last_action_player"] = self.last_action_player
            
        return state


# ゲームとWebSocket接続を管理するクラス
class ConnectionManager:
    def __init__(self):
        self.games: Dict[str, BinaryMahjongGame] = {}
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, room_id: str, player_id: str):
        await websocket.accept()
        
        # ルームが存在しなければ、avtive_connectionsにルームを追加
        if room_id not in self.active_connections:
            self.active_connections[room_id] = {}
            # ゲームを初期化して追加
            self.games[room_id] = BinaryMahjongGame(room_id)
            
        # player_idをkeyにしてWebSocketを追加
        self.active_connections[room_id][player_id] = websocket
        
        
        await self.broadcast(
            {"action": "player_connected", "player_id": player_id},
            room_id
        )
        
    def disconnect(self, room_id: str, player_id: str):
        # ルームとプレイヤーが存在すれば削除
        if room_id in self.active_connections and player_id in self.active_connections[room_id]:
            del self.active_connections[room_id][player_id]
            
        # ルームに誰も接続していなければ削除
        if room_id in self.active_connections and not self.active_connections[room_id]:
            if room_id in self.games:
                del self.games[room_id]
            del self.active_connections[room_id]
            
    async def broadcast(self, message: dict, room_id: str):
        if room_id in self.active_connections:
            for player_id, connection in self.active_connections[room_id].items():
                game = self.games.get(room_id)
                if game:
                    player_message = {**message}
                    if "game_state" not in player_message:
                        player_message["game_state"] = game.get_game_state(player_id)
                    await connection.send_json(player_message)
                    
    async def send_personal(self, message: dict, room_id: str, player_id: str):
        if (room_id in self.active_connections and 
            player_id in self.active_connections[room_id]):
            await self.active_connections[room_id][player_id].send_json(message)


manager = ConnectionManager()


# WebSocketエンドポイント
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
    
    game = manager.games.get(room_id)
    
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
            game = manager.games.get(room_id)
            
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