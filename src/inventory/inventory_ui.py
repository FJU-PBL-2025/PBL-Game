from typing import TYPE_CHECKING, Optional, Tuple

import pygame

if TYPE_CHECKING:
  from src.game import Game
from src.inventory.inventory import Inventory
from src.inventory.item_stack import ItemStack


class InventoryUI:
  """
  背包 UI 渲染器
  使用 assets/ui/inventory-export.png 作為背景 (176x94)

  UI 佈局：
  - 上排：4 格裝備欄（頭盔、胸甲、褲子、鞋子）
  - 下面：9x3 = 27 格道具欄
  """

  # 裝備欄位置（4 格）- (x, y, w, h) 每格 16x16
  EQUIP_SLOTS = [
    (53, 12, 16, 16),   # 頭盔
    (71, 12, 16, 16),   # 胸甲
    (89, 12, 16, 16),   # 褲子
    (107, 12, 16, 16),  # 鞋子
  ]

  # 道具欄位置 (9x3)
  ITEM_SLOT_SIZE = 16  # 每格大小 16x16
  ITEM_COLS_X = [8, 26, 44, 62, 80, 98, 116, 134, 152]  # 9 欄的 X 座標
  ITEM_ROWS_Y = [34, 52, 70]  # 3 排的 Y 座標

  # 實際 UI 區域大小（圖片左上角的有效區域）
  UI_WIDTH = 176
  UI_HEIGHT = 94

  def __init__(self, game: "Game"):
    self.game = game

    # 載入背景圖片並裁切有效區域
    full_image: pygame.Surface = pygame.image.load(
      "./assets/ui/inventory-export.png"
    ).convert_alpha()

    # 裁切左上角 176x94 的有效區域
    self.bg_image = full_image.subsurface((0, 0, self.UI_WIDTH, self.UI_HEIGHT))

    # 計算縮放比例（放大 UI）
    self.scale = 4
    self.bg_scaled = pygame.transform.scale(
      self.bg_image,
      (
        self.UI_WIDTH * self.scale,
        self.UI_HEIGHT * self.scale
      )
    )

    # UI 位置（置中）
    self.ui_x = (game.GAME_W - self.bg_scaled.get_width()) // 2
    self.ui_y = (game.GAME_H - self.bg_scaled.get_height()) // 2

    # 滑鼠懸停狀態
    self.hovered_slot: Optional[int] = None
    self.hovered_slot_type: Optional[str] = None  # 'equipment' or 'item'

    # 字體 - 使用支援中文的自定義字體
    try:
      self.font = pygame.font.Font("./assets/font.ttf", 14)
      self.small_font = pygame.font.Font("./assets/font.ttf", 12)
    except:
      # 備用字體
      self.font = pygame.font.SysFont("arial", 14)
      self.small_font = pygame.font.SysFont("arial", 12)

  def render(self, surface: pygame.Surface):
    """渲染整個背包介面"""
    # 繪製半透明背景
    overlay = pygame.Surface((self.game.GAME_W, self.game.GAME_H))
    overlay.set_alpha(150)
    overlay.fill((0, 0, 0))
    surface.blit(overlay, (0, 0))

    # 繪製背包背景圖片
    surface.blit(self.bg_scaled, (self.ui_x, self.ui_y))

    # 繪製裝備欄物品
    self.render_equipment_slots(surface)

    # 繪製道具欄物品
    self.render_item_slots(surface)

    # 繪製游標物品
    self.render_cursor_item(surface)

    # 繪製工具提示
    if self.hovered_slot is not None:
      self.render_tooltip(surface)

  def render_equipment_slots(self, surface: pygame.Surface):
    """渲染裝備欄物品"""
    for i, (ex, ey, ew, eh) in enumerate(self.EQUIP_SLOTS):
      slot = self.game.inventory.equipment_slots[i]

      x = self.ui_x + ex * self.scale
      y = self.ui_y + ey * self.scale
      w = ew * self.scale
      h = eh * self.scale

      is_hovered = (self.hovered_slot == i and self.hovered_slot_type == 'equipment')

      # 繪製高亮
      if is_hovered:
        highlight = pygame.Surface((w, h), pygame.SRCALPHA)
        highlight.fill((255, 255, 255, 80))
        surface.blit(highlight, (x, y))

      # 繪製物品（填滿整個格子）
      if not slot.is_empty():
        self.draw_item_icon(surface, x, y, slot, w, h)

  def render_item_slots(self, surface: pygame.Surface):
    """渲染道具欄物品"""
    for row in range(Inventory.ITEM_ROWS):
      for col in range(Inventory.ITEM_COLS):
        slot_index = row * Inventory.ITEM_COLS + col
        slot = self.game.inventory.item_slots[slot_index]

        x = self.ui_x + self.ITEM_COLS_X[col] * self.scale
        y = self.ui_y + self.ITEM_ROWS_Y[row] * self.scale
        size = self.ITEM_SLOT_SIZE * self.scale

        is_hovered = (self.hovered_slot == slot_index and self.hovered_slot_type == 'item')

        # 繪製高亮
        if is_hovered:
          highlight = pygame.Surface((size, size), pygame.SRCALPHA)
          highlight.fill((255, 255, 255, 80))
          surface.blit(highlight, (x, y))

        # 繪製物品（填滿整個格子）
        if not slot.is_empty():
          self.draw_item_icon(surface, x, y, slot, size, size, draw_count=True)

  def render_cursor_item(self, surface: pygame.Surface):
    """渲染游標上的物品"""
    if self.game.inventory.cursor_stack.is_empty():
      return

    mouse_x, mouse_y = pygame.mouse.get_pos()
    scale_x = self.game.GAME_W / self.game.SCREEN_WIDTH
    scale_y = self.game.GAME_H / self.game.SCREEN_HEIGHT
    game_mouse_x = int(mouse_x * scale_x)
    game_mouse_y = int(mouse_y * scale_y)

    icon_size = self.ITEM_SLOT_SIZE * self.scale
    self.draw_item_icon(
      surface,
      game_mouse_x - icon_size // 2,
      game_mouse_y - icon_size // 2,
      self.game.inventory.cursor_stack,
      icon_size,
      icon_size,
      draw_count=True
    )

  def draw_item_icon(
    self,
    surface: pygame.Surface,
    x: int,
    y: int,
    slot: ItemStack,
    width: int,
    height: int,
    draw_count: bool = False
  ):
    """繪製物品圖示"""
    if slot.is_empty():
      return

    # 確保物品圖示已創建
    if slot.item.icon_surface is None:
      slot.item.create_icon(32)

    # 縮放並繪製圖示
    scaled_icon = pygame.transform.scale(slot.item.icon_surface, (width, height))
    surface.blit(scaled_icon, (x, y))

    # 繪製數量
    if draw_count and slot.count > 1:
      count_text = str(slot.count)
      text_surface = self.small_font.render(count_text, True, (255, 255, 255))

      # 繪製陰影
      shadow_surface = self.small_font.render(count_text, True, (0, 0, 0))
      surface.blit(shadow_surface, (x + width - text_surface.get_width() - 1, y + height - text_surface.get_height() + 1))

      # 繪製文字
      surface.blit(text_surface, (x + width - text_surface.get_width() - 2, y + height - text_surface.get_height()))

  def render_tooltip(self, surface: pygame.Surface):
    """渲染工具提示"""
    slot = self.get_hovered_slot_object()
    if slot is None or slot.is_empty():
      return

    mouse_x, mouse_y = pygame.mouse.get_pos()
    scale_x = self.game.GAME_W / self.game.SCREEN_WIDTH
    scale_y = self.game.GAME_H / self.game.SCREEN_HEIGHT
    game_mouse_x = int(mouse_x * scale_x)
    game_mouse_y = int(mouse_y * scale_y)

    # 準備文字
    lines = [slot.item.name]
    if slot.item.description:
      lines.append(slot.item.description)

    # 計算大小
    padding = 8
    line_height = 20
    max_width = max(self.font.size(line)[0] for line in lines)
    tooltip_width = max_width + padding * 2
    tooltip_height = len(lines) * line_height + padding * 2

    # 計算位置
    tooltip_x = game_mouse_x + 15
    tooltip_y = game_mouse_y + 15

    if tooltip_x + tooltip_width > self.game.GAME_W:
      tooltip_x = game_mouse_x - tooltip_width - 15
    if tooltip_y + tooltip_height > self.game.GAME_H:
      tooltip_y = game_mouse_y - tooltip_height - 15

    # 繪製背景
    pygame.draw.rect(surface, (30, 30, 30), (tooltip_x, tooltip_y, tooltip_width, tooltip_height))
    pygame.draw.rect(surface, (100, 100, 100), (tooltip_x, tooltip_y, tooltip_width, tooltip_height), 2)

    # 繪製文字
    for i, line in enumerate(lines):
      text_surface = self.font.render(line, True, (255, 255, 255))
      surface.blit(text_surface, (tooltip_x + padding, tooltip_y + padding + i * line_height))

  def get_slot_at_position(self, x: int, y: int) -> Optional[Tuple[str, int]]:
    """獲取指定位置的格子（返回類型和索引）"""
    # 檢查裝備欄
    for i, (ex, ey, ew, eh) in enumerate(self.EQUIP_SLOTS):
      slot_x = self.ui_x + ex * self.scale
      slot_y = self.ui_y + ey * self.scale
      slot_w = ew * self.scale
      slot_h = eh * self.scale

      if slot_x <= x < slot_x + slot_w and slot_y <= y < slot_y + slot_h:
        return ('equipment', i)

    # 檢查道具欄
    for row in range(Inventory.ITEM_ROWS):
      for col in range(Inventory.ITEM_COLS):
        slot_index = row * Inventory.ITEM_COLS + col

        slot_x = self.ui_x + self.ITEM_COLS_X[col] * self.scale
        slot_y = self.ui_y + self.ITEM_ROWS_Y[row] * self.scale
        slot_size = self.ITEM_SLOT_SIZE * self.scale

        if slot_x <= x < slot_x + slot_size and slot_y <= y < slot_y + slot_size:
          return ('item', slot_index)

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

    if self.hovered_slot_type == 'equipment':
      return self.game.inventory.equipment_slots[self.hovered_slot]
    elif self.hovered_slot_type == 'item':
      return self.game.inventory.item_slots[self.hovered_slot]

    return None
