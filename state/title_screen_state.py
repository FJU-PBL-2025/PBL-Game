import pygame

from state.game_world_state import GameWorldState
from state.settings_state import SettingsState
from state.state import State


class TitleScreenState(State):
  def __init__(self, game):
    State.__init__(self, game)
    
    self.OPTIONS = ["Play", "Settings", "Quit"]
    self.index = 0

  def update(self, delta_time: float, actions: dict):
    if actions.get(pygame.K_RETURN):
      match self.index:
        case 0:
          new_state = GameWorldState(self.game)
          new_state.enter_state()
        case 1:
          new_state = SettingsState(self.game)
          new_state.enter_state()
        case 2:
          self.game.playing = False
          self.game.running = False
    
    if actions.get(pygame.K_w) or actions.get(pygame.K_UP):
      if self.index == 0:
        self.index = len(self.OPTIONS) - 1
      else:
        self.index -= 1
    
    if actions.get(pygame.K_s) or actions.get(pygame.K_DOWN):
      if self.index == len(self.OPTIONS) - 1:
        self.index = 0
      else:
        self.index += 1

    self.game.reset_keys()

  def render(self, surface: pygame.Surface):
    surface.fill((255, 255, 255))
    self.game.draw_text(
      surface,
      "PBL Game",
      (0, 0, 0),
      self.game.GAME_W / 2,
      self.game.GAME_H / 4
    )
    for i, v in enumerate(self.OPTIONS):
      self.game.draw_text(
        surface,
        "> " + v if self.index == i else v,
        (0, 0, 0),
        self.game.GAME_W / 2,
        self.game.GAME_H / 2 + i * 40
      )
