import json
from typing import List, Optional

from src.inventory.item import Item, ItemType
from src.inventory.item_stack import ItemStack


class Inventory:
  """
  背包系統
  - 裝備欄：4 格（頭盔、胸甲、褲子、鞋子）
  - 道具欄：27 格 (9x3)
  """

  EQUIPMENT_SLOTS = 4
  ITEM_COLS = 9
  ITEM_ROWS = 3
  ITEM_SLOTS = ITEM_COLS * ITEM_ROWS  # 27

  def __init__(self):
    # 裝備欄：4 格（頭盔、胸甲、褲子、鞋子）
    self.equipment_slots: List[ItemStack] = [
      ItemStack() for _ in range(self.EQUIPMENT_SLOTS)
    ]

    # 道具欄：27 格 (9x3)
    self.item_slots: List[ItemStack] = [
      ItemStack() for _ in range(self.ITEM_SLOTS)
    ]

    # 游標物品（滑鼠拿著的物品）
    self.cursor_stack: ItemStack = ItemStack()

  def add_item(self, item_id: str, count: int = 1) -> int:
    """
    添加物品到道具欄
    返回無法添加的剩餘數量
    """
    remaining = count

    with open("./assets/items.json", "r") as f:
      items = json.load(f)

    item = items[item_id]
    item = Item(
      item_id = item_id,
      name = item["name"],
      item_type = ItemType(item["item_type"]),
      max_stack = item["max_stack"],
      description = item["description"],
      icon = item["icon"]
    )

    # 先嘗試堆疊到已有的格子
    for slot in self.item_slots:
      if remaining <= 0:
        break

      if not slot.is_empty() and slot.item.item_id == item.item_id:
        if slot.can_add(item, remaining):
          added = slot.add(remaining)
          remaining -= added

    # 如果還有剩餘，放入空格子
    for slot in self.item_slots:
      if remaining <= 0:
        break

      if slot.is_empty():
        amount_to_add = min(remaining, item.max_stack)
        slot.set_item(item, amount_to_add)
        remaining -= amount_to_add

    return remaining

  def remove_item(self, item_id: str, count: int = 1) -> int:
    """
    從道具欄移除指定物品
    返回實際移除的數量
    """
    removed = 0
    remaining = count

    for slot in self.item_slots:
      if remaining <= 0:
        break

      if not slot.is_empty() and slot.item.item_id == item_id:
        actual_remove = slot.remove(remaining)
        removed += actual_remove
        remaining -= actual_remove

    return removed

  def has_item(self, item_id: str, count: int = 1) -> bool:
    """檢查是否擁有指定數量的物品"""
    total = 0
    for slot in self.item_slots:
      if not slot.is_empty() and slot.item.item_id == item_id:
        total += slot.count
        if total >= count:
          return True
    return False

  def count_item(self, item_id: str) -> int:
    """計算道具欄中某物品的總數"""
    total = 0
    for slot in self.item_slots:
      if not slot.is_empty() and slot.item.item_id == item_id:
        total += slot.count
    return total

  def get_first_empty_slot(self) -> Optional[int]:
    """獲取第一個空格子的索引"""
    for i, slot in enumerate(self.item_slots):
      if slot.is_empty():
        return i
    return None

  def is_full(self) -> bool:
    """檢查道具欄是否已滿"""
    return self.get_first_empty_slot() is None

  def clear(self):
    """清空整個背包"""
    for slot in self.equipment_slots:
      slot.clear()
    for slot in self.item_slots:
      slot.clear()
    self.cursor_stack.clear()

  def __repr__(self):
    non_empty = sum(1 for slot in self.item_slots if not slot.is_empty())
    return f"Inventory({non_empty}/{self.ITEM_SLOTS} item slots used)"
