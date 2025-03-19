from typing import Optional
from .. import taku, janshi

class GameState:
    """ゲームの状態を管理するクラス"""
    
    def __init__(self, room_id: str):
        self.room_id = room_id
        self.taku = taku.Taku(aka=True)
        self.players = {}
        self.player_seats = {}
        self.current_turn_idx = 0
        self.game_started = False
        self.game_finished = False
        self.winner = None
        
        # 牌関連
        self.last_discarded_hai = None
        self.last_action_player = None
        
        # 宣言状態
        self.doubt_available = False
        self.ron_available = True
        self.ron_player = None
        self.tumo = True
        self.tumo_player = None
        
        # 手牌公開
        self.public_hands = set()
    
    def add_player(self, player_id: str, name: str) -> bool:
        """プレイヤーを追加"""
        if len(self.players) >= 4:
            return False

        if len(self.players) == 0:
            player = janshi.Janshi(play=True, first=True)
        else:
            player = janshi.Janshi(play=True)
        player.name = name

        seat_position = len(self.players)
        self.player_seats[player_id] = seat_position
        self.players[player_id] = player

        return True
    
    def get_current_player_id(self) -> Optional[str]:
        """現在の手番プレイヤーIDを取得"""
        for player_id, position in self.player_seats.items():
            if position == self.current_turn_idx:
                return player_id
        return None
    
    def next_turn(self):
        """次のプレイヤーの手番に移行"""
        self.current_turn_idx = (self.current_turn_idx + 1) % len(self.players)
        
    def make_hand_public(self, player_id: str):
        """プレイヤーの手牌を公開状態にする"""
        self.public_hands.add(player_id)
        
    def is_player_turn(self, player_id: str) -> bool:
        """指定したプレイヤーの手番かどうか"""
        player_position = self.player_seats.get(player_id)
        return player_position == self.current_turn_idx
    
    def get_game_state_dict(self, viewer_id: Optional[str] = None) -> dict:
        """ゲーム状態を辞書形式で取得"""
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
            "ron_player": self.ron_player,
            "tumo_player": self.tumo_player
        }
        
        if self.winner:
            state["winner"] = self.winner
           
        for player_id, player in self.players.items():
            is_viewer = (player_id == viewer_id)
            
            player_state = {
                "name": player.name,
                "seat": self.player_seats[player_id],
                "discarded": [hai.str for hai in player.kawa] 
            }
            
            if is_viewer or player_id in self.public_hands:
                player_state["hand"] = [hai.str for hai in player.tehai]
                
                if player_id in self.public_hands:
                    player_state["hand_public"] = True
                    
            state["players"][player_id] = player_state
            
        if self.last_discarded_hai:
            state["last_discarded_hai"] = self.last_discarded_hai.str
            state["last_action_player"] = self.last_action_player
            
        return state