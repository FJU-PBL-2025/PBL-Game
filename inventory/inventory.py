from typing import Optional, List
from inventory.item import Item
from inventory.item_stack import ItemStack


class Inventory:
  """背包系統 - Minecraft 風格"""

  def __init__(self):
    # 主背包：27 格 (9x3)
    self.main_slots: List[ItemStack] = [ItemStack() for _ in range(27)]

    # 快捷欄：9 格 (1x9)
    self.hotbar_slots: List[ItemStack] = [ItemStack() for _ in range(9)]

    # 護甲欄：4 格（頭盔、胸甲、護腿、靴子）
    self.armor_slots: List[ItemStack] = [ItemStack() for _ in range(4)]

    # 副手欄：1 格
    self.offhand_slot: ItemStack = ItemStack()

    # 游標物品（滑鼠拿著的物品）
    self.cursor_stack: ItemStack = ItemStack()

  def get_all_storage_slots(self) -> List[ItemStack]:
    """獲取所有儲存格（主背包 + 快捷欄）"""
    return self.main_slots + self.hotbar_slots

  def get_slot(self, slot_index: int) -> Optional[ItemStack]:
    """獲取指定格子（0-35: 主背包+快捷欄）"""
    all_slots = self.get_all_storage_slots()
    if 0 <= slot_index < len(all_slots):
      return all_slots[slot_index]
    return None

  def add_item(self, item: Item, count: int = 1) -> int:
    """
    添加物品到背包
    返回無法添加的剩餘數量
    """
    remaining = count

    # 先嘗試堆疊到已有的格子
    for slot in self.get_all_storage_slots():
      if remaining <= 0:
        break

      if not slot.is_empty() and slot.item.item_id == item.item_id:
        if slot.can_add(item, remaining):
          added = slot.add(remaining)
          remaining -= added

    # 如果還有剩餘，放入空格子
    for slot in self.get_all_storage_slots():
      if remaining <= 0:
        break

      if slot.is_empty():
        amount_to_add = min(remaining, item.max_stack)
        slot.set_item(item, amount_to_add)
        remaining -= amount_to_add

    return remaining

  def remove_item(self, item_id: str, count: int = 1) -> int:
    """
    從背包移除指定物品
    返回實際移除的數量
    """
    removed = 0
    remaining = count

    for slot in self.get_all_storage_slots():
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
    for slot in self.get_all_storage_slots():
      if not slot.is_empty() and slot.item.item_id == item_id:
        total += slot.count
        if total >= count:
          return True
    return False

  def count_item(self, item_id: str) -> int:
    """計算背包中某物品的總數"""
    total = 0
    for slot in self.get_all_storage_slots():
      if not slot.is_empty() and slot.item.item_id == item_id:
        total += slot.count
    return total

  def get_first_empty_slot(self) -> Optional[int]:
    """獲取第一個空格子的索引"""
    for i, slot in enumerate(self.get_all_storage_slots()):
      if slot.is_empty():
        return i
    return None

  def is_full(self) -> bool:
    """檢查背包是否已滿"""
    return self.get_first_empty_slot() is None

  def clear(self):
    """清空整個背包"""
    for slot in self.main_slots:
      slot.clear()
    for slot in self.hotbar_slots:
      slot.clear()
    for slot in self.armor_slots:
      slot.clear()
    self.offhand_slot.clear()
    self.cursor_stack.clear()

  def __repr__(self):
    non_empty = sum(1 for slot in self.get_all_storage_slots() if not slot.is_empty())
    return f"Inventory({non_empty}/36 slots used)"
