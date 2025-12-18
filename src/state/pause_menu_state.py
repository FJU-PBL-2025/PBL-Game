from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
  from src.game import Game
from src.state.state import State


class PauseMenuState(State):
  def __init__(self, game: "Game"):
    State.__init__(self, game)
    
    self.OPTIONS: list[str] = ["Resume", "Back to Main Menu", "Quit"]
    self.index: int = 0

  def update(self, delta_time: float):
    i_m = self.game.input_manager
    
    if i_m.is_key_down_once(pygame.K_RETURN):
      match self.index:
        case 0:
          self.exit_state()
        case 1:
          self.exit_state(pop_layer = 2)
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
    self.prev_state.render(surface)
    
    game_over_screen_fade = pygame.Surface((self.game.GAME_W, self.game.GAME_H))
    game_over_screen_fade.fill((0, 0, 0))
    game_over_screen_fade.set_alpha(160)
    surface.blit(game_over_screen_fade, (0, 0))
    
    self.game.draw_text(
      surface,
      "Game Paused",
      (255, 255, 255),
      (
        self.game.GAME_W / 2,
        self.game.GAME_H / 4
      )
    )
    for i, v in enumerate(self.OPTIONS):
      self.game.draw_text(
        surface,
        "> " + v if self.index == i else v,
        (255, 255, 255),
        (
          self.game.GAME_W / 2,
          self.game.GAME_H / 2 + i * 40
        )
      )
