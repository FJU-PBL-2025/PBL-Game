from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
  from src.game import Game
from src.battle_helper import BattleHelper
from src.state.state import State
from src.npc import Npc

class BattleState(State):
  def __init__(self, game: "Game", npc: "Npc"):
    State.__init__(self, game)
    
    self.game = game
    self.npc = npc
    
    self.battle_helper = BattleHelper(self.game, self.npc)

  def update(self, delta_time: float):
    i_m = self.game.input_manager
    
    if i_m.is_key_down_once(pygame.K_ESCAPE):
      self.exit_state()
  
  def render(self, surface: pygame.Surface):
    surface.fill((0, 0, 0))
