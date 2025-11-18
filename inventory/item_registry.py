from inventory.item import Item, ItemType, ArmorSlot


class ItemRegistry:
  """物品註冊表 - 管理所有遊戲物品"""

  def __init__(self):
    self.items = {}
    self._register_default_items()

  def register(self, item: Item):
    """註冊物品"""
    self.items[item.item_id] = item

  def get(self, item_id: str) -> Item:
    """獲取物品"""
    return self.items.get(item_id)

  def _register_default_items(self):
    """註冊預設物品（類似 Minecraft 的物品）"""

    # === 方塊類 ===
    dirt = Item("dirt", "Dirt", ItemType.BLOCK, max_stack=64,
                description="A block of dirt")
    dirt.set_icon_color((139, 69, 19))  # 棕色
    self.register(dirt)

    stone = Item("stone", "Stone", ItemType.BLOCK, max_stack=64,
                 description="A solid stone block")
    stone.set_icon_color((128, 128, 128))  # 灰色
    self.register(stone)

    wood = Item("wood", "Wood Planks", ItemType.BLOCK, max_stack=64,
                description="Wooden planks")
    wood.set_icon_color((205, 133, 63))  # 木頭色
    self.register(wood)

    cobblestone = Item("cobblestone", "Cobblestone", ItemType.BLOCK,
                       max_stack=64, description="Cobblestone block")
    cobblestone.set_icon_color((100, 100, 100))  # 深灰色
    self.register(cobblestone)

    glass = Item("glass", "Glass", ItemType.BLOCK, max_stack=64,
                 description="Transparent glass block")
    glass.set_icon_color((200, 230, 255))  # 淡藍色
    self.register(glass)

    # === 工具類 ===
    wooden_pickaxe = Item("wooden_pickaxe", "Wooden Pickaxe", ItemType.TOOL,
                          max_stack=1, durability=59,
                          description="A pickaxe made of wood")
    wooden_pickaxe.set_icon_color((160, 110, 70))
    self.register(wooden_pickaxe)

    stone_pickaxe = Item("stone_pickaxe", "Stone Pickaxe", ItemType.TOOL,
                         max_stack=1, durability=131,
                         description="A pickaxe made of stone")
    stone_pickaxe.set_icon_color((110, 110, 110))
    self.register(stone_pickaxe)

    iron_pickaxe = Item("iron_pickaxe", "Iron Pickaxe", ItemType.TOOL,
                        max_stack=1, durability=250,
                        description="A pickaxe made of iron")
    iron_pickaxe.set_icon_color((200, 200, 200))
    self.register(iron_pickaxe)

    wooden_axe = Item("wooden_axe", "Wooden Axe", ItemType.TOOL,
                      max_stack=1, durability=59,
                      description="An axe made of wood")
    wooden_axe.set_icon_color((160, 110, 70))
    self.register(wooden_axe)

    wooden_shovel = Item("wooden_shovel", "Wooden Shovel", ItemType.TOOL,
                         max_stack=1, durability=59,
                         description="A shovel made of wood")
    wooden_shovel.set_icon_color((160, 110, 70))
    self.register(wooden_shovel)

    # === 武器類 ===
    wooden_sword = Item("wooden_sword", "Wooden Sword", ItemType.WEAPON,
                        max_stack=1, durability=59,
                        description="A sword made of wood")
    wooden_sword.set_icon_color((160, 110, 70))
    self.register(wooden_sword)

    stone_sword = Item("stone_sword", "Stone Sword", ItemType.WEAPON,
                       max_stack=1, durability=131,
                       description="A sword made of stone")
    stone_sword.set_icon_color((110, 110, 110))
    self.register(stone_sword)

    iron_sword = Item("iron_sword", "Iron Sword", ItemType.WEAPON,
                      max_stack=1, durability=250,
                      description="A sword made of iron")
    iron_sword.set_icon_color((200, 200, 200))
    self.register(iron_sword)

    bow = Item("bow", "Bow", ItemType.WEAPON, max_stack=1, durability=384,
               description="A bow for shooting arrows")
    bow.set_icon_color((139, 90, 43))
    self.register(bow)

    # === 護甲類 ===
    iron_helmet = Item("iron_helmet", "Iron Helmet", ItemType.ARMOR,
                       max_stack=1, durability=165,
                       armor_slot=ArmorSlot.HELMET,
                       description="A helmet made of iron")
    iron_helmet.set_icon_color((200, 200, 200))
    self.register(iron_helmet)

    iron_chestplate = Item("iron_chestplate", "Iron Chestplate",
                           ItemType.ARMOR, max_stack=1, durability=240,
                           armor_slot=ArmorSlot.CHESTPLATE,
                           description="A chestplate made of iron")
    iron_chestplate.set_icon_color((200, 200, 200))
    self.register(iron_chestplate)

    iron_leggings = Item("iron_leggings", "Iron Leggings", ItemType.ARMOR,
                         max_stack=1, durability=225,
                         armor_slot=ArmorSlot.LEGGINGS,
                         description="Leggings made of iron")
    iron_leggings.set_icon_color((200, 200, 200))
    self.register(iron_leggings)

    iron_boots = Item("iron_boots", "Iron Boots", ItemType.ARMOR,
                      max_stack=1, durability=195,
                      armor_slot=ArmorSlot.BOOTS,
                      description="Boots made of iron")
    iron_boots.set_icon_color((200, 200, 200))
    self.register(iron_boots)

    # === 食物類 ===
    apple = Item("apple", "Apple", ItemType.FOOD, max_stack=64,
                 description="A delicious apple")
    apple.set_icon_color((255, 0, 0))  # 紅色
    self.register(apple)

    bread = Item("bread", "Bread", ItemType.FOOD, max_stack=64,
                 description="Freshly baked bread")
    bread.set_icon_color((222, 184, 135))  # 麵包色
    self.register(bread)

    cooked_beef = Item("cooked_beef", "Cooked Beef", ItemType.FOOD,
                       max_stack=64, description="Cooked beef")
    cooked_beef.set_icon_color((139, 69, 19))
    self.register(cooked_beef)

    # === 材料類 ===
    stick = Item("stick", "Stick", ItemType.MATERIAL, max_stack=64,
                 description="A wooden stick")
    stick.set_icon_color((139, 90, 43))
    self.register(stick)

    coal = Item("coal", "Coal", ItemType.MATERIAL, max_stack=64,
                description="A lump of coal")
    coal.set_icon_color((30, 30, 30))  # 黑色
    self.register(coal)

    iron_ingot = Item("iron_ingot", "Iron Ingot", ItemType.MATERIAL,
                      max_stack=64, description="An iron ingot")
    iron_ingot.set_icon_color((200, 200, 200))
    self.register(iron_ingot)

    gold_ingot = Item("gold_ingot", "Gold Ingot", ItemType.MATERIAL,
                      max_stack=64, description="A gold ingot")
    gold_ingot.set_icon_color((255, 215, 0))  # 金色
    self.register(gold_ingot)

    diamond = Item("diamond", "Diamond", ItemType.MATERIAL, max_stack=64,
                   description="A precious diamond")
    diamond.set_icon_color((0, 255, 255))  # 青色
    self.register(diamond)

    emerald = Item("emerald", "Emerald", ItemType.MATERIAL, max_stack=64,
                   description="A precious emerald")
    emerald.set_icon_color((0, 255, 0))  # 綠色
    self.register(emerald)

    # === 雜項 ===
    torch = Item("torch", "Torch", ItemType.MISC, max_stack=64,
                 description="Provides light")
    torch.set_icon_color((255, 200, 0))  # 黃色
    self.register(torch)

    arrow = Item("arrow", "Arrow", ItemType.MISC, max_stack=64,
                 description="Ammunition for bows")
    arrow.set_icon_color((139, 90, 43))
    self.register(arrow)


# 全局物品註冊表實例
ITEM_REGISTRY = ItemRegistry()
