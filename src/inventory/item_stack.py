from typing import Optional

from src.inventory.item import Item


class ItemStack:
  """物品堆疊類別 - 代表背包中的一個格子"""

  def __init__(self, item: Optional[Item] = None, count: int = 0):
    self.item: Optional[Item] = item
    self.count: int = count

  def is_empty(self) -> bool:
    """是否為空"""
    return self.item is None or self.count <= 0

  def is_full(self) -> bool:
    """是否已滿"""
    if self.is_empty():
      return False
    return self.count >= self.item.max_stack

  def can_add(self, other_item: Item, amount: int = 1) -> bool:
    """是否可以添加物品"""
    if self.is_empty():
      return True
    if self.item.item_id != other_item.item_id:
      return False
    if not self.item.is_stackable():
      return False
    return self.count + amount <= self.item.max_stack

  def add(self, amount: int = 1) -> int:
    """添加數量，返回實際添加的數量"""
    if self.is_empty():
      return 0

    max_can_add = self.item.max_stack - self.count
    actual_add = min(amount, max_can_add)
    self.count += actual_add
    return actual_add

  def remove(self, amount: int = 1) -> int:
    """移除數量，返回實際移除的數量"""
    if self.is_empty():
      return 0

    actual_remove = min(amount, self.count)
    self.count -= actual_remove

    if self.count <= 0:
      self.clear()

    return actual_remove

  def clear(self):
    """清空格子"""
    self.item = None
    self.count = 0

  def set_item(self, item: Item, count: int = 1):
    """設置物品"""
    self.item = item
    self.count = min(count, item.max_stack)

  def copy(self) -> "ItemStack":
    """複製物品堆疊"""
    return ItemStack(self.item, self.count)

  def split(self, amount: int) -> "ItemStack":
    """分割物品堆疊，返回新的堆疊"""
    if self.is_empty():
      return ItemStack()

    actual_amount = min(amount, self.count)
    self.count -= actual_amount

    if self.count <= 0:
      item = self.item
      self.clear()
      return ItemStack(item, actual_amount)

    return ItemStack(self.item, actual_amount)

  def __repr__(self):
    if self.is_empty():
      return "ItemStack(Empty)"
    return f"ItemStack({self.item.name} x{self.count})"
