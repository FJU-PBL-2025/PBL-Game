import pygame

from state.state import State
from tile_render import TiledMapRenderer


class GameWorldState(State):
  def __init__(self, game):
    State.__init__(self, game)
    
    self.map_renderer = TiledMapRenderer("./assets/map/test-map/test-map.tmx")

  def update(self, delta_time: float, actions: dict):
    if actions.get(pygame.K_ESCAPE):
      self.exit_state()
    self.game.reset_keys()

  def render(self, surface: pygame.Surface):
    surface.fill((255, 255, 255))
    self.map_renderer.render(surface)

