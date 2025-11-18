import pygame
from enum import Enum
from typing import Optional


class ItemType(Enum):
  """物品類型"""
  BLOCK = "block"           # 方塊
  TOOL = "tool"             # 工具
  WEAPON = "weapon"         # 武器
  ARMOR = "armor"           # 護甲
  FOOD = "food"             # 食物
  MATERIAL = "material"     # 材料
  MISC = "misc"             # 雜項


class ArmorSlot(Enum):
  """護甲欄位"""
  HELMET = "helmet"         # 頭盔
  CHESTPLATE = "chestplate" # 胸甲
  LEGGINGS = "leggings"     # 護腿
  BOOTS = "boots"           # 靴子


class Item:
  """物品定義類別"""

  def __init__(
    self,
    item_id: str,
    name: str,
    item_type: ItemType,
    max_stack: int = 64,
    durability: Optional[int] = None,
    armor_slot: Optional[ArmorSlot] = None,
    description: str = ""
  ):
    self.item_id = item_id          # 物品唯一 ID
    self.name = name                # 物品名稱
    self.item_type = item_type      # 物品類型
    self.max_stack = max_stack      # 最大堆疊數量
    self.durability = durability    # 耐久度（工具/武器/護甲）
    self.armor_slot = armor_slot    # 護甲欄位
    self.description = description  # 物品描述

    # 圖示（先用顏色代替，之後可以改成圖片）
    self.icon_surface = None
    self.icon_color = (100, 100, 100)  # 預設灰色

  def create_icon(self, size: int = 32):
    """創建物品圖示（簡單的色塊，之後可以換成圖片）"""
    self.icon_surface = pygame.Surface((size, size))
    self.icon_surface.fill(self.icon_color)
    # 添加邊框
    pygame.draw.rect(self.icon_surface, (50, 50, 50), (0, 0, size, size), 2)

  def set_icon_color(self, color: tuple):
    """設置圖示顏色"""
    self.icon_color = color
    if self.icon_surface:
      size = self.icon_surface.get_width()
      self.create_icon(size)

  def is_stackable(self) -> bool:
    """判斷是否可堆疊"""
    return self.max_stack > 1 and self.durability is None

  def __repr__(self):
    return f"Item({self.item_id}, {self.name})"
