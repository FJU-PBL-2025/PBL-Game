import pygame

from state.state import State
from state.inventory_state import InventoryState
from tile_render import TiledMapRenderer
from inventory.inventory import Inventory
from inventory.item_registry import ITEM_REGISTRY


class GameWorldState(State):
  def __init__(self, game):
    State.__init__(self, game)

    self.map = TiledMapRenderer("test-map")

    # 將玩家位置設定在畫面中央
    self.game.player.x = self.game.GAME_W / 2
    self.game.player.y = self.game.GAME_H / 2
    self.game.player.rect.center = (self.game.player.x, self.game.player.y)

    # 創建玩家背包
    self.player_inventory = Inventory()

    # 添加一些測試物品到背包
    self._add_test_items()

  def update(self, delta_time: float, actions: dict):
    self.game.player.update(delta_time, actions)
    # 傳入 self.game 以便 player 可以觸發傳送
    self.game.player.handle_movement(
      delta_time,
      actions,
      self.map.tiles,
      self.map.metadata,
      self.game
    )

    if actions.get(pygame.K_ESCAPE):
      self.exit_state()
      self.game.reset_keys()
      return

    # 按 E 鍵開啟背包
    if actions.get(pygame.K_e):
      inventory_state = InventoryState(self.game, self.player_inventory)
      inventory_state.enter_state()
      self.game.reset_keys()
      return

    self.game.reset_keys()

  def render(self, surface: pygame.Surface):
    surface.fill((255, 255, 255))
    self.map.render(surface)
    self.game.player.render(surface)

  def _add_test_items(self):
    """添加測試物品到背包（用於演示）"""
    # 只添加少量物品
    self.player_inventory.add_item(ITEM_REGISTRY.get("dirt"), 16)
    self.player_inventory.add_item(ITEM_REGISTRY.get("stone"), 8)
    self.player_inventory.add_item(ITEM_REGISTRY.get("wood"), 4)

    # 一把鎬
    self.player_inventory.add_item(ITEM_REGISTRY.get("iron_pickaxe"), 1)

    # 一把劍
    self.player_inventory.add_item(ITEM_REGISTRY.get("iron_sword"), 1)

    # 少量食物
    self.player_inventory.add_item(ITEM_REGISTRY.get("apple"), 3)

    # 少量材料
    self.player_inventory.add_item(ITEM_REGISTRY.get("diamond"), 1)
    self.player_inventory.add_item(ITEM_REGISTRY.get("torch"), 8)
