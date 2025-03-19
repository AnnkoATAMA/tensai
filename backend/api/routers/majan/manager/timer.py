import asyncio
from typing import Any, Callable, Coroutine

class GameTimer:
    """ゲーム内のタイマー処理を管理するクラス"""
    
    def __init__(self):
        self.ron_timer = None
        self.doubt_timer = None
        self.tumo_timer = None
    
    async def start_ron_timer(self, 
                             seconds: int, 
                             on_timeout: Callable[[], Coroutine[Any, Any, None]]) -> None:
        """ロン猶予時間のタイマーを開始"""
        if self.ron_timer:
            self.ron_timer.cancel()
        
        async def timer_callback():
            try:
                await asyncio.sleep(seconds)
                await on_timeout()
            except asyncio.CancelledError:
                pass
        
        self.ron_timer = asyncio.create_task(timer_callback())
    
    async def start_doubt_timer(self, 
                               seconds: int, 
                               on_timeout: Callable[[bool, str], Coroutine[Any, Any, None]], 
                               is_valid: bool,
                               player_id: str,
                               claim_type: str) -> None:
        """ダウト猶予時間のタイマーを開始"""
        if self.doubt_timer:
            self.doubt_timer.cancel()
        
        async def timer_callback():
            try:
                await asyncio.sleep(seconds)
                await on_timeout(is_valid, player_id, claim_type)
            except asyncio.CancelledError:
                pass
        
        self.doubt_timer = asyncio.create_task(timer_callback())
    
    def cancel_all_timers(self):
        """全てのタイマーをキャンセル"""
        for timer_name in ['ron_timer', 'doubt_timer', 'tumo_timer']:
            timer = getattr(self, timer_name)
            if timer:
                timer.cancel()
                setattr(self, timer_name, None)
    
    def cancel_timer(self, timer_name: str):
        """指定したタイマーをキャンセル"""
        timer = getattr(self, timer_name, None)
        if timer:
            timer.cancel()
            setattr(self, timer_name, None)