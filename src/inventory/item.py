from enum import Enum
from typing import Optional

import pygame


class ItemType(Enum):
  """物品類型"""
  EQUIPMENT = "equipment"   # 裝備
  CONSUMABLE = "consumable" # 消耗品
  MATERIAL = "material"     # 材料
  KEY_ITEM = "key_item"     # 關鍵道具


class Item:
  """物品定義類別"""

  def __init__(
    self,
    item_id: str,
    name: str,
    item_type: ItemType,
    max_stack: int = 99,
    description: str = "",
    icon_path: Optional[str] = None
  ):
    self.item_id: str = item_id
    self.name: str = name
    self.item_type: ItemType = item_type
    self.max_stack: int = max_stack
    self.description: str = description

    # 圖示
    self.icon_surface: Optional[pygame.Surface] = None
    self.icon_color: tuple = (100, 100, 100)

    if icon_path:
      self.load_icon(icon_path)

  def load_icon(self, path: str):
    """載入物品圖示"""
    try:
      self.icon_surface = pygame.image.load(path).convert_alpha()
    except Exception:
      self.icon_surface = None

  def create_icon(self, size: int = 32):
    """創建簡單的色塊圖示"""
    self.icon_surface = pygame.Surface((size, size), pygame.SRCALPHA)
    self.icon_surface.fill(self.icon_color)
    pygame.draw.rect(self.icon_surface, (50, 50, 50), (0, 0, size, size), 2)

  def set_icon_color(self, color: tuple):
    """設置圖示顏色"""
    self.icon_color = color

  def is_stackable(self) -> bool:
    """判斷是否可堆疊"""
    return self.max_stack > 1

  def __repr__(self):
    return f"Item({self.item_id}, {self.name})"
