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
    
    if actions.get(pygame.K_w) or actions.get(pygame.K_UP):
      self.game.player.pos_y -= self.game.player.speed * delta_time
    if actions.get(pygame.K_s) or actions.get(pygame.K_DOWN):
      self.game.player.pos_y += self.game.player.speed * delta_time
      
    if actions.get(pygame.K_a) or actions.get(pygame.K_LEFT):
      self.game.player.pos_x -= self.game.player.speed * delta_time
    if actions.get(pygame.K_d) or actions.get(pygame.K_RIGHT):
      self.game.player.pos_x += self.game.player.speed * delta_time

  def render(self, surface: pygame.Surface):
    surface.fill((255, 255, 255))
    self.map_renderer.render(surface)
    pygame.draw.circle(
      surface,
      (255, 0, 0),
      (self.game.player.pos_x, self.game.player.pos_y),
      16.0,
    )
