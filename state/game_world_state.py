import pygame

from state.state import State
from tile_render import TiledMapRenderer


class GameWorldState(State):
  def __init__(self, game):
    State.__init__(self, game)
    
    self.map = TiledMapRenderer("test-map")

    # 將玩家位置設定在畫面中央
    self.game.player.x = self.game.GAME_W / 2
    self.game.player.y = self.game.GAME_H / 2
    self.game.player.rect.center = (self.game.player.x, self.game.player.y)

  def update(self, delta_time: float, actions: dict):
    self.game.player.update(delta_time, actions)
    # 傳入 self.game 以便 player 可以觸發傳送
    self.game.player.handle_movement(
      delta_time,
      actions,
      self.map.tiles,
      self.map.metadata,
      self.game
    )
    
    if actions.get(pygame.K_ESCAPE):
      self.exit_state()
      self.game.reset_keys()

  def render(self, surface: pygame.Surface):
    surface.fill((255, 255, 255))
    self.map.render(surface)
    self.game.player.render(surface)
