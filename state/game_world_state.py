import pygame

from state.state import State


class GameWorldState(State):
  def __init__(self, game):
    State.__init__(self, game)

  def update(self, delta_time: float, actions: dict):
    if actions.get(pygame.K_ESCAPE):
      self.exit_state()
    self.game.reset_keys()

  def render(self, surface: pygame.Surface):
    surface.fill((255, 255, 255))
    self.game.draw_text(
      surface,
      "PBL Game World",
      (0, 0, 0),
      self.game.GAME_W / 2,
      self.game.GAME_H / 2
    )
