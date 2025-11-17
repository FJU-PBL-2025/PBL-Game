# c:\Users\ting6\Documents\GitHub\PBL-Game (test)\state\mini_level_state.py

import pygame
# 假設你有一個基底 State 類別，如果沒有，可以直接繼承 object
from .state import State 

class MiniLevelState(State):
    def __init__(self, game):
        State.__init__(self, game)
        # 可以在這裡初始化小關卡需要的變數

    def update(self, delta_time, actions):
        # 這裡處理小關卡的邏輯更新
        # 例如：如果玩家按下 ESC，就退出這個關卡
        if actions.get(pygame.K_ESCAPE):
            self.exit_state() # 呼叫基底 State 的方法來退出
            self.game.reset_keys()

    def render(self, surface):
        # 1. 先用黑色填滿整個畫布，清除上一幀的畫面 (地圖)
        surface.fill(pygame.Color("black"))
        
        # 2. 畫上新的文字
        self.game.draw_text(surface, "第一個小關卡", 
                            pygame.Color("white"), 
                            self.game.GAME_W / 2, self.game.GAME_H / 2)
