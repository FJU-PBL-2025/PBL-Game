from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
  from src.game import Game
from src.state.game_world_state import GameWorldState
from src.state.settings_state import SettingsState
from src.state.state import State


class TitleScreenState(State):
  def __init__(self, game: "Game"):
    State.__init__(self, game)
    
    self.OPTIONS: list[str] = ["Play", "Settings", "Quit"]
    self.index: int = 0

  def update(self, delta_time: float):
    i_m = self.game.input_manager
    
    if i_m.is_key_down_once(pygame.K_RETURN):
      match self.index:
        case 0:
          new_state = GameWorldState(self.game)
          new_state.enter_state()
        case 1:
          new_state = SettingsState(self.game)
          new_state.enter_state()
        case 2:
          pygame.event.post(pygame.Event(pygame.QUIT))
    
    if i_m.is_key_down_delayed(pygame.K_w, 0.2) or i_m.is_key_down_delayed(pygame.K_UP, 0.2):
      if self.index == 0:
        self.index = len(self.OPTIONS) - 1
      else:
        self.index -= 1
    
    if i_m.is_key_down_delayed(pygame.K_s, 0.2) or i_m.is_key_down_delayed(pygame.K_DOWN, 0.2):
      if self.index == len(self.OPTIONS) - 1:
        self.index = 0
      else:
        self.index += 1

  def render(self, surface: pygame.Surface):
    surface.fill((255, 255, 255))
    self.game.draw_text(
      surface,
      "PBL Game",
      (0, 0, 0),
      (
        self.game.GAME_W / 2,
        self.game.GAME_H / 4
      )
    )
    for i, v in enumerate(self.OPTIONS):
      self.game.draw_text(
        surface,
        "> " + v if self.index == i else v,
        (0, 0, 0),
        (
          self.game.GAME_W / 2,
          self.game.GAME_H / 2 + i * 40
        )
      )
