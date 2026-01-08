import json
from typing import TYPE_CHECKING, List, Dict, Any
from dataclasses import dataclass

if TYPE_CHECKING:
  from src.game import Game
from src.npc import Npc


@dataclass
class ShopItem:
  item_id: str
  name: str
  description: str
  price: List[Dict[str, Any]]
  stock: int


class ShopHelper:
  def __init__(self, game: "Game", npc: Npc):
    self.game = game
    self.npc = npc

    with open("./assets/items.json", "r") as f:
      self.item_definitions = json.load(f)

    self.shop_items: List[ShopItem] = []
    self._load_shop_data()

  def _load_shop_data(self):
    with open(f"./assets/entity/npc/{self.npc.name}/npc.meta.json", "r") as f:
      npc_data = json.load(f)

    shop_data = npc_data.get("shop", {})

    for item_id, item_data in shop_data.items():
      if item_id not in self.item_definitions:
        continue

      item_def = self.item_definitions[item_id]

      price_list = []
      for price_entry in item_data.get("price", []):
        for currency_id, currency_data in price_entry.items():
          price_list.append(
            {"item_id": currency_id, "qty": currency_data.get("qty", 1)}
          )

      self.shop_items.append(
        ShopItem(
          item_id = item_id,
          name = item_def.get("name", item_id),
          description = item_def.get("description", ""),
          price = price_list,
          stock = item_data.get("reserve", -1),
        )
      )

  def get_price_text(self, price: List[Dict[str, Any]]) -> str:
    parts = []
    for p in price:
      item_id = p["item_id"]
      qty = p["qty"]
      if item_id in self.item_definitions:
        name = self.item_definitions[item_id].get("name", item_id)
      else:
        name = item_id
      parts.append(f"{qty}x {name}")
    return ", ".join(parts) if parts else "Free"

  def can_afford(self, price: List[Dict[str, Any]]) -> bool:
    for p in price:
      item_id = p["item_id"]
      qty = p["qty"]
      if not self.game.inventory.has_item(item_id, qty):
        return False
    return True

  def purchase_item(self, shop_item: ShopItem) -> tuple[bool, str]:
    if shop_item.stock == 0:
      return False, "Out of stock!"

    if not self.can_afford(shop_item.price):
      return False, "Not enough currency!"

    for p in shop_item.price:
      self.game.inventory.remove_item(p["item_id"], p["qty"])

    remaining = self.game.inventory.add_item(shop_item.item_id, 1)
    if remaining > 0:
      for p in shop_item.price:
        self.game.inventory.add_item(p["item_id"], p["qty"])
      return False, "Inventory full!"

    if shop_item.stock > 0:
      shop_item.stock -= 1

    return True, f"Purchased {shop_item.name}!"
