from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
  from src.game import Game
from src.state.state import State


class SettingsState(State):
  def __init__(self, game: "Game"):
    State.__init__(self, game)

  def update(self, delta_time: float):
    i_m = self.game.input_manager
    
    if i_m.is_key_down_once(pygame.K_ESCAPE):
      self.exit_state()

  def render(self, surface: pygame.Surface):
    surface.fill((255, 255, 255))
    self.game.draw_text(
      surface,
      "Game Settings",
      (0, 0, 0),
      (
        self.game.GAME_W / 2,
        self.game.GAME_H / 4
      )
    )
