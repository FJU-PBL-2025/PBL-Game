from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
  from src.game import Game
from src.state.state import State
from src.tile_render import TiledMapRenderer


class GameWorldState(State):
  def __init__(self, game: "Game"):
    State.__init__(self, game)
    
    self.map: TiledMapRenderer = TiledMapRenderer("test-map")

  def update(self, delta_time: float):
    i_m = self.game.input_manager
    
    self.game.player.update(delta_time)
    self.game.player.handle_movement(delta_time, i_m, self.map.tiles, self.map.metadata)
    
    if i_m.is_key_down_once(pygame.K_ESCAPE):
      self.exit_state()

  def render(self, surface: pygame.Surface):
    surface.fill((255, 255, 255))
    self.map.render(surface)
    self.game.player.render(surface)
