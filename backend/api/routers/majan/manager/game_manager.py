from .. import taku, janshi
import random
from typing import Any, Tuple
from asyncio import sleep

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
        self.ron_available = False
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
    async def discard_hai(self, player_id: str, hai_idx: int) -> Tuple[bool, str]:
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
        
        ron_time_seconds = 10
        
        self.ron_available = True
        
        result = {
            "message": "牌を捨てました",
            "ron_available": True,
            "ron_timeout": ron_time_seconds
        }
        
        await sleep(ron_time_seconds)
        
       # 猶予時間後、誰もロンしていなければ次の手番に進む
        if not self.game_finished:
            # ロン宣言できなくする
            self.ron_available = False
            
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
                    result["message"] = "流局"
                    return True, result
        
        return True, result
        
    # ロンの宣言
    async def claim_ron(self, player_id: str) -> Tuple[bool, Any]:
        # ゲームが開始されていないか、終了している場合はfalseを返す
        if not self.game_started or self.game_finished:
            return False, "ゲームは開始されていないか終了しています"
        
        # ロン宣言が可能な状態でないとfalseを返す
        if not hasattr(self, 'ron_available') or not self.ron_available:
            return False, "現在ロン宣言はできません"
        
        # ロン宣言をしたプレイヤーを格納
        player = self.players[player_id]
        
        # バイナリ麻雀では、ロン宣言は自由だがダウト可能
        self.doubt_available = True
        self.ron_available = False  # ロン宣言されたらもうロンできない
        
        # ロン宣言をしたプレイヤーを記録
        self.ron_player = player_id
        
        # 内部的にロン可能か確認（クライアントには知らせない）
        is_ron_valid = player.can_ron(self.last_discarded_hai)
        
        # ダウト時間（秒）
        doubt_time_seconds = 30
        
        # 待機時間をクライアントに通知するために返す
        doubt_timeout = doubt_time_seconds
        
        # 時間制限後の自動判定
        await sleep(doubt_time_seconds)
        
        # まだダウトされてない場合かつ、まだ勝者が決まっていない場合
        if self.doubt_available and not self.game_finished:
            # ダウト時間が過ぎた場合の処理
            self.doubt_available = False
            self.game_finished = True
            
            # ロン宣言が実際に有効だったかでゲーム結果を判定
            if is_ron_valid:
                self.winner = player_id
                result = {
                    "winner": player_id,
                    "reason": "ロン成立、ダウト時間切れ"
                }
            else:
                # バイナリ麻雀の場合、ロンが不成立でも時間切れなら不正ロンを見逃したことになるので
                # ロン宣言者の勝ち（通常の麻雀ルールとは違う特殊ルール）
                self.winner = player_id
                result = {
                    "winner": player_id,
                    "reason": "ロン不成立だが、ダウト時間切れによりロン宣言者の勝ち"
                }
            
            # この結果を通知できるようにManagerクラスに渡すために追加
            return True, {
                "doubt_available": False,
                "is_ron_valid": is_ron_valid,
                "timeout_result": result,
                "game_finished": True
            }
        
        # ここに到達するのは、すでにdoubt_availableがFalseになっているか、
        # game_finishedがTrueになっている場合（ダウトされた場合）
        return True, {
            "doubt_available": self.doubt_available,
            "is_ron_valid": is_ron_valid
        }
            
    # ロン宣言に対してダウトを宣言  
    async def claim_doubt(self, doubter_id: str, target_id: str) -> Tuple[bool, Any]:
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