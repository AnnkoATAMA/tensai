import random
from typing import Tuple, Any
from .state import GameState
from .timer import GameTimer

class GameActionManager:
    """ゲームのアクション処理を管理するクラス"""
    
    def __init__(self, game_state: GameState, timer: GameTimer):
        self.state = game_state
        self.timer = timer
        self.on_doubt_timeout = None  # コールバック関数
    
    def start_game(self) -> bool:
        """ゲームを開始する"""
        if len(self.state.players) < 2 or self.state.game_started:
            return False

        random.shuffle(self.state.taku.yama)

        # 配牌
        for player_id, player in self.state.players.items():
            player.haipai(self.state.taku.yama)
            player.riipai()

        self.state.current_turn_idx = 0
        self.state.game_started = True

        return True
    
    async def discard_hai(self, player_id: str, hai_idx: int) -> Tuple[bool, dict]:
        """牌を捨てる"""
        # 事前条件チェック
        if not self.state.game_started or self.state.game_finished:
            return False, "ゲームは、開始されていないか終了しています"

        if not self.state.is_player_turn(player_id):
            return False, "あなたの手番ではありません"

        player = self.state.players[player_id]

        # 無効な牌のインデックスの場合はfalseを返す
        if hai_idx < 0 or hai_idx >= len(player.tehai):
            return False, "無効な牌のインデックスです"

        # 牌を捨てる
        discarded_hai = player.dahai(hai_idx)

        # 最後に捨てた牌と捨てたプレイヤーを記録
        self.state.last_discarded_hai = discarded_hai
        self.state.last_action_player = player_id

        ron_time_seconds = 10

        # ロン宣言が可能なフラグを立てる
        self.state.ron_available = True

        # ロンタイマーを開始
        await self.timer.start_ron_timer(ron_time_seconds, self._on_ron_timeout)

        # 即座に結果を返す
        result = {
            "message": "牌を捨てました",
            "ron_available": True,
            "ron_timeout": ron_time_seconds
        }

        return True, result
    
    async def _on_ron_timeout(self):
        """ロン猶予時間終了時の処理"""
        if self.state.ron_available and not self.state.game_finished:
            # ロン宣言できなくする
            self.state.ron_available = False

            # 次の手番へ
            self.state.next_turn()

            # 次のプレイヤーにツモさせる
            next_player_id = self.state.get_current_player_id()
            if next_player_id:
                next_player = self.state.players[next_player_id]
                if len(self.state.taku.yama) > 0:
                    next_player.tsumo(self.state.taku.yama)
                    next_player.riipai()
                else:
                    # 山がなくなったら流局
                    self.state.game_finished = True
    
    async def claim_tumo(self, player_id: str) -> Tuple[bool, Any]:
        """ツモあがり宣言"""
        
        # 事前条件チェック
        if not self.state.game_started or self.state.game_finished:
            return False, "ゲームは開始されていないか終了しています"
            
        if not self.state.is_player_turn(player_id):
            return False, "あなたの手番ではありません"
        
        player = self.state.players[player_id]
        
        # 状態の更新
        self.state.doubt_available = True
        self.state.tumo = False
        self.timer.cancel_timer('tumo_timer')
        
        # ツモプレイヤーを記録
        self.state.tumo_player = player_id
        
        # 手牌を公開
        self.state.make_hand_public(player_id)
        
        # ツモあがり可能かチェック（内部判定）
        is_tumo_valid = player.can_tumo()
        
        # ダウトタイマーの設定
        doubt_time_seconds = 30
        self.timer.cancel_timer('doubt_timer')

        # タイマー開始
        await self.timer.start_doubt_timer(
            doubt_time_seconds, 
            self._on_doubt_timeout,
            is_tumo_valid,
            player_id,
            "ツモあがり"
        )

        # 結果を返す
        result = {
            "message": "ツモあがりが宣言されました",
            "doubt_available": True,
            "is_tumo_valid": is_tumo_valid,
            "doubt_timeout": doubt_time_seconds
        }

        return True, result
        
    
    async def claim_ron(self, player_id: str) -> Tuple[bool, Any]:
        """ロン宣言"""
        
        # 事前条件チェック
        if not self.state.game_started or self.state.game_finished:
            return False, "ゲームは開始されていないか終了しています"

        if not self.state.ron_available:
            return False, "現在ロン宣言はできません"

        player = self.state.players[player_id]

        # 状態の更新
        self.state.doubt_available = True
        self.state.ron_available = False
        self.timer.cancel_timer('ron_timer')
        
        # ロンプレイヤーを記録
        self.state.ron_player = player_id
        
        # 手牌を公開
        self.state.make_hand_public(player_id)

        # ロン可能かチェック（内部判定）
        is_ron_valid = player.can_ron(self.state.last_discarded_hai)
        
        # ダウトタイマーの設定
        doubt_time_seconds = 30
        self.timer.cancel_timer('doubt_timer')
        
        # タイマー開始
        await self.timer.start_doubt_timer(
            doubt_time_seconds, 
            self._on_doubt_timeout,
            is_ron_valid,
            player_id,
            "ロン"
        )

        # 結果を返す
        result = {
            "doubt_available": True,
            "is_ron_valid": is_ron_valid,
            "doubt_timeout": doubt_time_seconds
        }

        return True, result

    async def _on_doubt_timeout(self, is_valid: bool, player_id: str, claim_type: str):
        """ダウト猶予時間終了時の処理"""
        if self.state.doubt_available and not self.state.game_finished:
            # ダウト時間が過ぎた場合の処理
            self.state.doubt_available = False
            self.state.game_finished = True

            # 宣言が実際に有効だったかでゲーム結果を判定
            if is_valid:
                self.state.winner = player_id
                timeout_result = {
                    "winner": player_id,
                    "reason": f"{claim_type}成立、ダウト時間切れ"
                }
            else:
                # バイナリ麻雀の場合、宣言が不成立でも時間切れなら不正宣言を見逃したことになるので
                # 宣言者の勝ち（通常の麻雀ルールとは違う特殊ルール）
                self.state.winner = player_id
                timeout_result = {
                    "winner": player_id,
                    "reason": f"{claim_type}不成立だが、ダウト時間切れにより宣言者の勝ち"
                }

            # イベントを発火して、タイムアウト結果をブロードキャストする
            if self.on_doubt_timeout:
                await self.on_doubt_timeout(timeout_result)
    
    async def claim_doubt(self, doubter_id: str, target_id: str) -> Tuple[bool, Any]:
        """ダウト宣言"""
        
        # 事前条件チェック
        if not self.state.doubt_available:
            return False, "ダウトできません"
            
        if doubter_id == target_id:
            return False, "自分自身にダウトできません"
            
        if target_id != self.state.ron_player and target_id != self.state.tumo_player:
            return False, "あがり宣言をしていないプレイヤーにダウトできません"
        
        # タイマーのキャンセル
        self.timer.cancel_timer('doubt_timer')
        
        # ダウト不可にする
        self.state.doubt_available = False
            
        target_player = self.state.players[target_id]
        
        # ロンかツモかで判定方法を切り替え
        if target_id == self.state.ron_player:
            is_valid = target_player.can_ron(self.state.last_discarded_hai)
            claim_type = "ロン"
        else:  # target_id == self.state.tumo_player
            is_valid = target_player.can_tumo()
            claim_type = "ツモ"
        
        self.state.game_finished = True
        
        if is_valid:
            # あがり成立ならダウト失敗、あがり宣言者の勝ち
            self.state.winner = target_id
            return True, {
                "winner": target_id,
                "reason": f"{claim_type}成立、ダウト失敗"
            }
        else:
            # あがり不成立ならダウト成功、ダウト宣言者の勝ち
            self.state.winner = doubter_id
            return True, {
                "winner": doubter_id,
                "reason": f"{claim_type}不成立、ダウト成功"
            }