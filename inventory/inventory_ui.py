import pygame
from typing import Optional, Tuple
from inventory.inventory import Inventory
from inventory.item_stack import ItemStack


class InventoryUI:
  """背包 UI 渲染器 - Minecraft 風格"""

  def __init__(self, game, inventory: Inventory):
    self.game = game
    self.inventory = inventory

    # UI 配置
    self.slot_size = 48  # 格子大小
    self.slot_padding = 4  # 格子間距
    self.icon_size = 40  # 物品圖示大小

    # 顏色配置（Minecraft 風格）
    self.bg_color = (139, 139, 139)  # 背景灰色
    self.slot_color = (139, 139, 139)  # 格子顏色
    self.slot_border_color = (55, 55, 55)  # 格子邊框
    self.selected_color = (255, 255, 255)  # 選中高亮
    self.text_color = (255, 255, 255)  # 文字顏色
    self.shadow_color = (63, 63, 63)  # 文字陰影

    # 字體
    self.font = pygame.font.SysFont("arial", 16)
    self.small_font = pygame.font.SysFont("arial", 14)

    # UI 位置計算
    self.calculate_positions()

    # 選中的格子索引
    self.hovered_slot = None
    self.hovered_slot_type = None  # 'main', 'hotbar', 'armor', 'crafting', etc.

  def calculate_positions(self):
    """計算 UI 各部分的位置"""
    screen_w = self.game.GAME_W
    screen_h = self.game.GAME_H

    # 主背包位置（9x3）
    main_width = 9 * (self.slot_size + self.slot_padding)
    main_height = 3 * (self.slot_size + self.slot_padding)
    self.main_x = (screen_w - main_width) // 2
    self.main_y = screen_h // 2 - 50

    # 快捷欄位置（9x1）
    self.hotbar_x = self.main_x
    self.hotbar_y = self.main_y + main_height + 10

    # 護甲欄位置（左側）
    self.armor_x = self.main_x - (self.slot_size + self.slot_padding) * 2 - 20
    self.armor_y = self.main_y

    # 背包標題位置
    self.title_x = self.main_x
    self.title_y = self.main_y - 40

  def render(self, surface: pygame.Surface):
    """渲染整個背包介面"""
    # 繪製半透明背景
    overlay = pygame.Surface((self.game.GAME_W, self.game.GAME_H))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    surface.blit(overlay, (0, 0))

    # 繪製標題
    self.draw_text(surface, "Inventory", self.title_x, self.title_y, self.text_color)

    # 繪製各個區域
    self.render_main_inventory(surface)
    self.render_hotbar(surface)
    self.render_armor_slots(surface)

    # 繪製游標物品（最後繪製，保持在最上層）
    self.render_cursor_item(surface)

    # 繪製工具提示
    if self.hovered_slot is not None:
      self.render_tooltip(surface)

  def render_main_inventory(self, surface: pygame.Surface):
    """渲染主背包（9x3）"""
    for row in range(3):
      for col in range(9):
        slot_index = row * 9 + col
        x = self.main_x + col * (self.slot_size + self.slot_padding)
        y = self.main_y + row * (self.slot_size + self.slot_padding)

        slot = self.inventory.main_slots[slot_index]
        is_hovered = (self.hovered_slot == slot_index and
                     self.hovered_slot_type == 'main')

        self.draw_slot(surface, x, y, slot, is_hovered)

  def render_hotbar(self, surface: pygame.Surface):
    """渲染快捷欄（9x1）"""
    for col in range(9):
      x = self.hotbar_x + col * (self.slot_size + self.slot_padding)
      y = self.hotbar_y

      slot = self.inventory.hotbar_slots[col]
      is_hovered = (self.hovered_slot == col and
                   self.hovered_slot_type == 'hotbar')

      self.draw_slot(surface, x, y, slot, is_hovered)

  def render_armor_slots(self, surface: pygame.Surface):
    """渲染護甲欄（4 格垂直排列）"""
    armor_names = ["Helmet", "Chestplate", "Leggings", "Boots"]

    for i in range(4):
      x = self.armor_x
      y = self.armor_y + i * (self.slot_size + self.slot_padding)

      slot = self.inventory.armor_slots[i]
      is_hovered = (self.hovered_slot == i and
                   self.hovered_slot_type == 'armor')

      self.draw_slot(surface, x, y, slot, is_hovered)

      # 繪製護甲類型標籤
      label_text = armor_names[i][:3]  # 縮寫
      self.draw_text(surface, label_text, x - 30, y + self.slot_size // 2,
                    self.text_color, size=12)

  def render_cursor_item(self, surface: pygame.Surface):
    """渲染游標上的物品"""
    if not self.inventory.cursor_stack.is_empty():
      mouse_x, mouse_y = pygame.mouse.get_pos()
      # 調整滑鼠位置到遊戲畫布坐標
      scale_x = self.game.GAME_W / self.game.SCREEN_WIDTH
      scale_y = self.game.GAME_H / self.game.SCREEN_HEIGHT
      game_mouse_x = int(mouse_x * scale_x)
      game_mouse_y = int(mouse_y * scale_y)

      self.draw_item_icon(surface,
                         game_mouse_x - self.icon_size // 2,
                         game_mouse_y - self.icon_size // 2,
                         self.inventory.cursor_stack, draw_count=True)

  def draw_slot(self, surface: pygame.Surface, x: int, y: int,
               slot: ItemStack, is_hovered: bool = False):
    """繪製單個格子"""
    # 繪製格子背景
    pygame.draw.rect(surface, self.slot_color, (x, y, self.slot_size, self.slot_size))

    # 繪製格子邊框
    border_color = self.selected_color if is_hovered else self.slot_border_color
    border_width = 3 if is_hovered else 2
    pygame.draw.rect(surface, border_color,
                    (x, y, self.slot_size, self.slot_size), border_width)

    # 繪製物品圖示和數量
    if not slot.is_empty():
      icon_x = x + (self.slot_size - self.icon_size) // 2
      icon_y = y + (self.slot_size - self.icon_size) // 2
      self.draw_item_icon(surface, icon_x, icon_y, slot, draw_count=True)

  def draw_item_icon(self, surface: pygame.Surface, x: int, y: int,
                    slot: ItemStack, draw_count: bool = False):
    """繪製物品圖示"""
    if slot.is_empty():
      return

    # 確保物品圖示已創建
    if slot.item.icon_surface is None:
      slot.item.create_icon(self.icon_size)

    # 繪製圖示
    surface.blit(slot.item.icon_surface, (x, y))

    # 繪製數量（如果大於 1）
    if draw_count and slot.count > 1:
      count_text = str(slot.count)
      text_x = x + self.icon_size - 8
      text_y = y + self.icon_size - 16
      self.draw_text(surface, count_text, text_x, text_y,
                    self.text_color, shadow=True, size=14)

    # 繪製耐久度條（如果有）
    if slot.durability is not None and slot.item.durability is not None:
      bar_width = self.icon_size - 4
      bar_height = 3
      bar_x = x + 2
      bar_y = y + self.icon_size - 6

      # 背景條
      pygame.draw.rect(surface, (0, 0, 0),
                      (bar_x, bar_y, bar_width, bar_height))

      # 耐久度條
      durability_percent = slot.durability / slot.item.durability
      filled_width = int(bar_width * durability_percent)

      # 根據耐久度百分比改變顏色
      if durability_percent > 0.5:
        bar_color = (0, 255, 0)  # 綠色
      elif durability_percent > 0.25:
        bar_color = (255, 255, 0)  # 黃色
      else:
        bar_color = (255, 0, 0)  # 紅色

      pygame.draw.rect(surface, bar_color,
                      (bar_x, bar_y, filled_width, bar_height))

  def render_tooltip(self, surface: pygame.Surface):
    """渲染工具提示（顯示物品名稱和描述）"""
    slot = self.get_hovered_slot_object()
    if slot is None or slot.is_empty():
      return

    mouse_x, mouse_y = pygame.mouse.get_pos()
    scale_x = self.game.GAME_W / self.game.SCREEN_WIDTH
    scale_y = self.game.GAME_H / self.game.SCREEN_HEIGHT
    game_mouse_x = int(mouse_x * scale_x)
    game_mouse_y = int(mouse_y * scale_y)

    # 準備工具提示文本
    lines = [slot.item.name]
    if slot.item.description:
      lines.append(slot.item.description)
    if slot.durability is not None:
      lines.append(f"Durability: {slot.durability}/{slot.item.durability}")

    # 計算工具提示大小
    padding = 8
    line_height = 20
    max_width = max(self.font.size(line)[0] for line in lines)
    tooltip_width = max_width + padding * 2
    tooltip_height = len(lines) * line_height + padding * 2

    # 計算位置（避免超出螢幕）
    tooltip_x = game_mouse_x + 15
    tooltip_y = game_mouse_y + 15

    if tooltip_x + tooltip_width > self.game.GAME_W:
      tooltip_x = game_mouse_x - tooltip_width - 15
    if tooltip_y + tooltip_height > self.game.GAME_H:
      tooltip_y = game_mouse_y - tooltip_height - 15

    # 繪製背景
    pygame.draw.rect(surface, (16, 16, 16),
                    (tooltip_x, tooltip_y, tooltip_width, tooltip_height))
    pygame.draw.rect(surface, (80, 0, 150),
                    (tooltip_x, tooltip_y, tooltip_width, tooltip_height), 2)

    # 繪製文本
    for i, line in enumerate(lines):
      text_y = tooltip_y + padding + i * line_height
      self.draw_text(surface, line, tooltip_x + padding, text_y,
                    self.text_color, size=16)

  def draw_text(self, surface: pygame.Surface, text: str, x: int, y: int,
               color: tuple, shadow: bool = False, size: int = 16):
    """繪製文字（帶陰影）"""
    font = self.font if size == 16 else self.small_font

    if shadow:
      # 繪製陰影
      shadow_surface = font.render(text, True, self.shadow_color)
      surface.blit(shadow_surface, (x + 2, y + 2))

    # 繪製文字
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, (x, y))

  def get_slot_at_position(self, x: int, y: int) -> Optional[Tuple[str, int]]:
    """獲取指定位置的格子（返回類型和索引）"""
    # 檢查主背包
    for row in range(3):
      for col in range(9):
        slot_x = self.main_x + col * (self.slot_size + self.slot_padding)
        slot_y = self.main_y + row * (self.slot_size + self.slot_padding)

        if (slot_x <= x < slot_x + self.slot_size and
            slot_y <= y < slot_y + self.slot_size):
          return ('main', row * 9 + col)

    # 檢查快捷欄
    for col in range(9):
      slot_x = self.hotbar_x + col * (self.slot_size + self.slot_padding)
      slot_y = self.hotbar_y

      if (slot_x <= x < slot_x + self.slot_size and
          slot_y <= y < slot_y + self.slot_size):
        return ('hotbar', col)

    # 檢查護甲欄
    for i in range(4):
      slot_x = self.armor_x
      slot_y = self.armor_y + i * (self.slot_size + self.slot_padding)

      if (slot_x <= x < slot_x + self.slot_size and
          slot_y <= y < slot_y + self.slot_size):
        return ('armor', i)

    return None

  def update_hover(self, mouse_x: int, mouse_y: int):
    """更新滑鼠懸停狀態"""
    result = self.get_slot_at_position(mouse_x, mouse_y)
    if result:
      self.hovered_slot_type, self.hovered_slot = result
    else:
      self.hovered_slot = None
      self.hovered_slot_type = None

  def get_hovered_slot_object(self) -> Optional[ItemStack]:
    """獲取當前懸停的格子對象"""
    if self.hovered_slot is None or self.hovered_slot_type is None:
      return None

    if self.hovered_slot_type == 'main':
      return self.inventory.main_slots[self.hovered_slot]
    elif self.hovered_slot_type == 'hotbar':
      return self.inventory.hotbar_slots[self.hovered_slot]
    elif self.hovered_slot_type == 'armor':
      return self.inventory.armor_slots[self.hovered_slot]

    return None
