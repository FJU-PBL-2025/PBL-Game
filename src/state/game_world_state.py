from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
  from src.game import Game
from src.state.state import State
from src.state.dialogue_state import DialogueState
from src.state.inventory_state import InventoryState
from src.map_loader import MapLoader
from src.state.pause_menu_state import PauseMenuState
from src.npc import Npc


class GameWorldState(State):
  def __init__(self, game: "Game"):
    State.__init__(self, game)
    
    self.map_loader: MapLoader = MapLoader("test-map")

  def update(self, delta_time: float):
    i_m = self.game.input_manager
    
    self.game.player.update(delta_time)
    self.check_exit(delta_time)
    
    self.check_npc_interaction()

    if i_m.is_key_down_once(pygame.K_ESCAPE):
      new_state = PauseMenuState(self.game)
      new_state.enter_state()

    if i_m.is_key_down_once(pygame.K_TAB):
      new_state = InventoryState(self.game)
      new_state.enter_state()

  def render(self, surface: pygame.Surface):
    surface.fill((255, 255, 255))
    self.map_loader.render(surface)
    
    for npc in self.map_loader.npcs:
      npc.render(surface)
    
    self.game.player.render(surface)
  
  def check_npc_interaction(self):
    i_m = self.game.input_manager
    
    if not i_m.is_key_down_once(pygame.K_e):
      return
    
    hit_npcs: list[Npc] = pygame.sprite.spritecollide(
      self.game.player,
      self.map_loader.npcs,
      False
    )
    
    if len(hit_npcs) > 0:
      npc = hit_npcs[0]
      dialogue_state = DialogueState(self.game, npc)
      dialogue_state.enter_state()

  def check_exit(self, delta_time: float):
    i_m = self.game.input_manager
    
    hit_tiles = self.game.player.handle_movement(
      delta_time,
      i_m,
      self.map_loader.tiles,
      self.map_loader.metadata
    )
    
    hit_exit_tiles = list(
      filter(
        lambda t: self.map_loader.metadata.exits.get((t.x, t.y)) is not None,
        hit_tiles
      )
    )
    
    if len(hit_exit_tiles) == 0:
      self.game.player.in_exit = False
    elif not self.game.player.in_exit:
      exit_tile = hit_exit_tiles[0]
      hit_exit = self.map_loader.metadata.exits.get(
        (exit_tile.x, exit_tile.y)
      )
      
      self.map_loader.change_map(hit_exit.dist)
      self.game.player.set_position(
        hit_exit.dist_x * self.map_loader.map.tilewidth + self.map_loader.map.tilewidth / 2,
        hit_exit.dist_y * self.map_loader.map.tileheight + self.map_loader.map.tileheight / 2
      )
      self.game.player.in_exit = True
      self.game.input_manager.pause(0.05)
