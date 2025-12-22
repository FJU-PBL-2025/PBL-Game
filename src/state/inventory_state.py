from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
  from src.game import Game
from src.state.state import State
from src.inventory.inventory_ui import InventoryUI


class InventoryState(State):
  """背包狀態 - 處理背包的輸入和顯示"""

  def __init__(self, game: "Game"):
    State.__init__(self, game)
    self.ui = InventoryUI(game)

    # 滑鼠按鍵狀態追蹤
    self.mouse_pressed: bool = False
    self.right_mouse_pressed: bool = False

  def update(self, delta_time: float):
    """更新背包狀態"""
    i_m = self.game.input_manager

    # 按 ESC 或 E 關閉背包
    if i_m.is_key_down_once(pygame.K_ESCAPE) or i_m.is_key_down_once(pygame.K_TAB):
      self.exit_state()
      return

    # 獲取滑鼠位置（轉換到遊戲畫布坐標）
    mouse_x, mouse_y = pygame.mouse.get_pos()
    scale_x = self.game.GAME_W / self.game.SCREEN_WIDTH
    scale_y = self.game.GAME_H / self.game.SCREEN_HEIGHT
    game_mouse_x = int(mouse_x * scale_x)
    game_mouse_y = int(mouse_y * scale_y)

    # 更新滑鼠懸停狀態
    self.ui.update_hover(game_mouse_x, game_mouse_y)

    # 處理滑鼠點擊
    mouse_buttons = pygame.mouse.get_pressed()

    # 左鍵點擊
    if mouse_buttons[0] and not self.mouse_pressed:
      self.mouse_pressed = True
      self.handle_left_click(game_mouse_x, game_mouse_y)
    elif not mouse_buttons[0]:
      self.mouse_pressed = False

    # 右鍵點擊
    if mouse_buttons[2] and not self.right_mouse_pressed:
      self.right_mouse_pressed = True
      self.handle_right_click(game_mouse_x, game_mouse_y)
    elif not mouse_buttons[2]:
      self.right_mouse_pressed = False

  def render(self, surface: pygame.Surface):
    """渲染背包界面"""
    # 先渲染下層狀態（遊戲畫面）
    if self.prev_state:
      self.prev_state.render(surface)

    # 在上面渲染背包 UI
    self.ui.render(surface)

  def handle_left_click(self, x: int, y: int):
    """處理左鍵點擊 - 拿起/放下整組物品"""
    result = self.ui.get_slot_at_position(x, y)
    if result is None:
      return

    slot_type, slot_index = result
    clicked_slot = self.get_slot_by_type(slot_type, slot_index)

    if clicked_slot is None:
      return

    cursor = self.game.inventory.cursor_stack

    if cursor.is_empty():
      # 拿起物品
      if not clicked_slot.is_empty():
        self.game.inventory.cursor_stack = clicked_slot.copy()
        clicked_slot.clear()
    else:
      # 游標有物品
      if clicked_slot.is_empty():
        # 放下物品
        clicked_slot.set_item(cursor.item, cursor.count)
        cursor.clear()
      elif clicked_slot.item.item_id == cursor.item.item_id:
        # 相同物品，嘗試堆疊
        if clicked_slot.item.is_stackable():
          total = clicked_slot.count + cursor.count
          if total <= clicked_slot.item.max_stack:
            clicked_slot.count = total
            cursor.clear()
          else:
            clicked_slot.count = clicked_slot.item.max_stack
            cursor.count = total - clicked_slot.item.max_stack
        else:
          # 不可堆疊，交換
          self.swap_slots(clicked_slot, cursor)
      else:
        # 不同物品，交換
        self.swap_slots(clicked_slot, cursor)

  def handle_right_click(self, x: int, y: int):
    """處理右鍵點擊 - 拿起/放下一半物品"""
    result = self.ui.get_slot_at_position(x, y)
    if result is None:
      return

    slot_type, slot_index = result
    clicked_slot = self.get_slot_by_type(slot_type, slot_index)

    if clicked_slot is None:
      return

    cursor = self.game.inventory.cursor_stack

    if cursor.is_empty():
      # 拿起一半
      if not clicked_slot.is_empty() and clicked_slot.count > 0:
        amount = (clicked_slot.count + 1) // 2
        self.game.inventory.cursor_stack = clicked_slot.split(amount)
    else:
      # 游標有物品
      if clicked_slot.is_empty():
        # 放下一個
        clicked_slot.set_item(cursor.item, 1)
        cursor.remove(1)
      elif clicked_slot.item.item_id == cursor.item.item_id:
        # 相同物品，放下一個
        if clicked_slot.item.is_stackable() and not clicked_slot.is_full():
          clicked_slot.add(1)
          cursor.remove(1)
      else:
        # 不同物品，交換
        self.swap_slots(clicked_slot, cursor)

  def swap_slots(self, slot1, slot2):
    """交換兩個格子的內容"""
    temp_item = slot1.item
    temp_count = slot1.count

    slot1.item = slot2.item
    slot1.count = slot2.count

    slot2.item = temp_item
    slot2.count = temp_count

  def get_slot_by_type(self, slot_type: str, slot_index: int):
    """根據類型和索引獲取格子對象"""
    if slot_type == 'equipment':
      return self.game.inventory.equipment_slots[slot_index]
    elif slot_type == 'item':
      return self.game.inventory.item_slots[slot_index]
    return None
