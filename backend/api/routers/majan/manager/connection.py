from fastapi import WebSocket
from typing import Dict
from .game import BinaryMahjongGame

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

    def get_game(self, room_id: str) -> BinaryMahjongGame:
        return self.games.get(room_id)