from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
  from src.game import Game


class State():
  def __init__(self, game: "Game"):
    self.game: "Game" = game
    self.prev_state: State | None = None

  def update(self, delta_time: float):
    pass

  def render(self, surface: pygame.Surface):
    pass

  def enter_state(self):
    if len(self.game.state_stack) > 1:
      self.prev_state = self.game.state_stack[-1]
    self.game.state_stack.append(self)

  def exit_state(self):
    self.game.state_stack.pop()
