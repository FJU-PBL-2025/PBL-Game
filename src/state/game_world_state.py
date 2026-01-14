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
    
    self.map_loader: MapLoader = MapLoader("awakening-room", self.game)
    
    # Load coin icon
    self.coin_icon = pygame.image.load("./assets/icon/coin.png").convert_alpha()
    self.coin_icon = pygame.transform.scale(self.coin_icon, (20, 20))  # Scale to appropriate size
    
    # Set player position to entry point
    self.game.player.set_position(
      self.map_loader.metadata.entry_x * self.map_loader.map.tilewidth + self.map_loader.map.tilewidth // 2,
      self.map_loader.metadata.entry_y * self.map_loader.map.tileheight + self.map_loader.map.tileheight // 2
    )

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
    
    # Draw coin display in top-right corner
    self._draw_coin_display(surface)
  
  def _draw_coin_display(self, surface: pygame.Surface):
    """Draw coin count in top-right corner"""
    coin_count = self.game.inventory.count_item("coin")
    
    # Background box
    box_width = 120
    box_height = 35
    box_x = self.game.GAME_W - box_width - 10
    box_y = 10
    
    pygame.draw.rect(
      surface,
      (40, 40, 60),
      (box_x, box_y, box_width, box_height),
      border_radius=5
    )
    pygame.draw.rect(
      surface,
      (255, 215, 0),
      (box_x, box_y, box_width, box_height),
      width=2,
      border_radius=5
    )
    
    # Coin icon and text
    icon_x = box_x + 8
    icon_y = box_y + (box_height - self.coin_icon.get_height()) // 2
    surface.blit(self.coin_icon, (icon_x, icon_y))
    
    # Coin count text (right-aligned within the box)
    text_y = box_y + box_height // 2
    # Calculate text width to properly right-align it
    coin_text = str(coin_count)
    text_surface = self.game.font.render(coin_text, True, (255, 215, 0))
    text_width = text_surface.get_width()
    # Position text so it's right-aligned with some padding from the right edge
    text_x = box_x + box_width - text_width // 2 - 10
    self.game.draw_text(
      surface,
      str(coin_count),
      (255, 215, 0),
      (text_x, text_y)
    )
  
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
      self.map_loader.objects,
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
      
      # Check for object exits
      if not self.game.player.in_exit:
        for obj in self.map_loader.objects:
          if obj.exit and pygame.sprite.collide_rect(self.game.player, obj):
            self.map_loader.change_map(obj.exit.dist)
            self.game.player.set_position(
              obj.exit.dist_x * self.map_loader.map.tilewidth + self.map_loader.map.tilewidth / 2,
              obj.exit.dist_y * self.map_loader.map.tileheight + self.map_loader.map.tileheight / 2
            )
            self.game.player.in_exit = True
            self.game.input_manager.pause(0.05)
            return
    elif not self.game.player.in_exit:
      # Check if exit requires boss to be defeated
      if self.map_loader.metadata.boss_died_exit:
        # Check if all NPCs on this map are defeated
        alive_npcs = [npc.name for npc in self.map_loader.npcs]
        if len(alive_npcs) > 0:
          # Boss still alive, can't exit
          return
      
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
