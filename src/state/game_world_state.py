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
from src.inventory.inventory import Inventory
from src.inventory.item import Item, ItemType


class GameWorldState(State):
  def __init__(self, game: "Game"):
    State.__init__(self, game)

    self.map_loader: MapLoader = MapLoader("test-map")

    # 創建玩家背包
    self.player_inventory: Inventory = Inventory()

    # 添加測試物品
    self._add_test_items()

  def update(self, delta_time: float):
    i_m = self.game.input_manager
    
    self.game.player.update(delta_time)
    self.check_exit(delta_time)

    if i_m.is_key_down_once(pygame.K_ESCAPE):
      new_state = PauseMenuState(self.game)
      new_state.enter_state()

    # 按 E 鍵：優先跟 NPC 互動，沒有 NPC 則開背包
    if i_m.is_key_down_once(pygame.K_e):
      if not self.check_npc_interaction():
        inventory_state = InventoryState(self.game, self.player_inventory)
        inventory_state.enter_state()

  def render(self, surface: pygame.Surface):
    surface.fill((255, 255, 255))
    self.map_loader.render(surface)
    
    for npc in self.map_loader.npcs:
      npc.render(surface)
    
    self.game.player.render(surface)
  
  def check_npc_interaction(self) -> bool:
    """檢查 NPC 互動，返回是否有互動發生"""
    hit_npcs: list[Npc] = pygame.sprite.spritecollide(
      self.game.player,
      self.map_loader.npcs,
      False
    )

    if len(hit_npcs) > 0:
      npc = hit_npcs[0]
      dialogue_state = DialogueState(self.game, npc)
      dialogue_state.enter_state()
      return True

    return False

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

  def _add_test_items(self):
    """添加測試物品到背包"""
    # 創建一些測試物品
    sword = Item("sword", "Iron Sword", ItemType.EQUIPMENT, max_stack=1, description="A sharp sword")
    sword.set_icon_color((180, 180, 200))

    shield = Item("shield", "Wooden Shield", ItemType.EQUIPMENT, max_stack=1, description="A sturdy shield")
    shield.set_icon_color((139, 90, 43))

    potion = Item("potion", "Health Potion", ItemType.CONSUMABLE, max_stack=99, description="Restores HP")
    potion.set_icon_color((255, 50, 50))

    wood = Item("wood", "Wood", ItemType.MATERIAL, max_stack=99, description="Building material")
    wood.set_icon_color((139, 69, 19))

    stone = Item("stone", "Stone", ItemType.MATERIAL, max_stack=99, description="A common rock")
    stone.set_icon_color((128, 128, 128))

    key = Item("key", "Golden Key", ItemType.KEY_ITEM, max_stack=1, description="Opens something...")
    key.set_icon_color((255, 215, 0))

    # 添加到背包
    self.player_inventory.add_item(sword, 1)
    self.player_inventory.add_item(potion, 5)
    self.player_inventory.add_item(wood, 12)
    self.player_inventory.add_item(stone, 8)
    self.player_inventory.add_item(key, 1)
