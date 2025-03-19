from typing import Any, Tuple, Optional
from .state import GameState
from .timer import GameTimer
from .action import GameActionManager

class BinaryMahjongGame:
    """バイナリ麻雀ゲームを管理する総合クラス"""
    
    def __init__(self, room_id: str):
        self.state = GameState(room_id)
        self.timer = GameTimer()
        self.action = GameActionManager(self.state, self.timer)
        self.room_id = room_id
        
        # コールバック関数
        self.on_doubt_timeout = None
        self._register_callbacks()
    
    def _register_callbacks(self):
        """コールバック関数を登録"""
        # ActionManagerのタイムアウトイベントを伝播
        self.action.on_doubt_timeout = self._propagate_doubt_timeout
    
    async def _propagate_doubt_timeout(self, result: dict):
        """ダウトタイムアウトイベントを伝播"""
        if self.on_doubt_timeout:
            await self.on_doubt_timeout(result)
    
    # --- プロパティへのアクセサ ---
    
    @property
    def players(self):
        return self.state.players
    
    @property
    def player_seats(self):
        return self.state.player_seats
    
    @property
    def game_started(self):
        return self.state.game_started
    
    @property
    def game_finished(self):
        return self.state.game_finished
    
    @property
    def winner(self):
        return self.state.winner
    
    @property
    def last_discarded_hai(self):
        return self.state.last_discarded_hai
    
    @property
    def ron_player(self):
        return self.state.ron_player
    
    @property
    def tumo_player(self):
        return self.state.tumo_player
    
    @property
    def public_hands(self):
        return self.state.public_hands
    
    @property
    def current_turn_idx(self):
        return self.state.current_turn_idx
    
    # --- ゲームの基本操作 ---
    
    def add_player(self, player_id: str, name: str) -> bool:
        """プレイヤーを追加"""
        return self.state.add_player(player_id, name)
    
    def start_game(self) -> bool:
        """ゲームを開始"""
        return self.action.start_game()
    
    def get_current_player_id(self) -> Optional[str]:
        """現在の手番プレイヤーIDを取得"""
        return self.state.get_current_player_id()
    
    def get_game_state(self, viewer_id: str = None) -> dict:
        """ゲーム状態を取得"""
        return self.state.get_game_state_dict(viewer_id)
    
    # --- プレイヤーアクション ---
    
    async def discard_hai(self, player_id: str, hai_idx: int) -> Tuple[bool, dict]:
        """牌を捨てる"""
        return await self.action.discard_hai(player_id, hai_idx)
    
    async def claim_tumo(self, player_id: str) -> Tuple[bool, Any]:
        """ツモあがり宣言"""
        return await self.action.claim_tumo(player_id)
    
    async def claim_ron(self, player_id: str) -> Tuple[bool, Any]:
        """ロン宣言"""
        return await self.action.claim_ron(player_id)
    
    async def claim_doubt(self, doubter_id: str, target_id: str) -> Tuple[bool, Any]:
        """ダウト宣言"""
        return await self.action.claim_doubt(doubter_id, target_id)