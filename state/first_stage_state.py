import pygame

class FirstStageState():
  def __init__(self, game):
    self.game = game

  def update(self, delta_time, actions):
    # 這個畫面是靜態的，所以 update 函式暫時不需要做任何事
    # 未來可以加上 "按任意鍵繼續" 之類的邏輯
    pass

  def render(self, surface: pygame.Surface):
    # 1. 將背景填滿白色
    surface.fill((255, 255, 255))
    
    # 2. 在畫面中央畫上黑色的 "第一關" 字樣
    self.game.draw_text(
      surface, 
      "第一關", 
      (0, 0, 0), 
      self.game.GAME_W / 2, 
      self.game.GAME_H / 2
    )