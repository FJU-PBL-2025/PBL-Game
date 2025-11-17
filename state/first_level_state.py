import pygame

from tile_render import TiledMapRenderer

class FirstLevelState():
  def __init__(self, game, map_name="level1"):
    self.game = game
    self.map_renderer = TiledMapRenderer(map_name)

    # 將玩家位置設定在畫面中央
    self.game.player.x = self.game.GAME_W / 2
    self.game.player.y = self.game.GAME_H / 2
    self.game.player.rect.center = (self.game.player.x, self.game.player.y)

  def update(self, delta_time, actions):
    self.game.player.handle_movement(
      delta_time,
      actions,
      self.map_renderer.tiles,
      self.map_renderer.metadata,
      self.game # 傳入 game 物件以進行狀態切換
    )

  def render(self, surface: pygame.Surface):
    surface.fill((0, 0, 0)) # 清除畫布
    self.map_renderer.render(surface)
    self.game.player.render(surface)