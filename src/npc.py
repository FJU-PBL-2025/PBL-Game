import pygame
import json
from dataclasses import dataclass


@dataclass
class DialogueOption:
  text: str
  next: str | None


@dataclass
class Dialogue:
  text: str
  options: list[DialogueOption] | None


class Npc(pygame.sprite.Sprite):
  def __init__(self, name: str, tile_width: int, tile_height: int):
    pygame.sprite.Sprite.__init__(self)

    self.name: str = name
    self.tile_width: int = tile_width
    self.tile_height: int = tile_height

    with open(f"./assets/entity/npc/{name}/npc.meta.json", "r", encoding="utf-8") as f:
      json_data = json.load(f)

    self.display_name: str = json_data.get("display_name", name)

    self.spawn_x: int = json_data["spawn"]["x"]
    self.spawn_y: int = json_data["spawn"]["y"]

    self.x: float = self.spawn_x * tile_width + tile_width / 2
    self.y: float = self.spawn_y * tile_height + tile_height / 2

    original_image = pygame.image.load(json_data["source_img"])
    self.image: pygame.Surface = pygame.transform.scale(original_image, (int(tile_width * 3), int(tile_height * 3)))
    self.rect: pygame.Rect = self.image.get_rect()
    self.rect.center = (self.x, self.y)

    self.dialogue_tree: dict[str, Dialogue] = {}
    self._load_dialogue(json_data.get("dialogue", {}))

    self.current_dialogue_id: str | None = None

  def _load_dialogue(self, dialogue_data: dict):
    for node_id, node_data in dialogue_data.items():
      options = None
      if node_data.get("options"):
        options = [
          DialogueOption(text=opt["text"], next=opt.get("next"))
          for opt in node_data["options"]
        ]

      self.dialogue_tree[node_id] = Dialogue(
        text=node_data["text"], options=options
      )

  def start_dialogue(self) -> Dialogue | None:
    self.current_dialogue_id = "init"
    return self.get_current_dialogue()

  def get_current_dialogue(self) -> Dialogue | None:
    if self.current_dialogue_id is None:
      return None
    return self.dialogue_tree.get(self.current_dialogue_id)

  def advance_dialogue(self, option_index: int) -> Dialogue | None:
    current = self.get_current_dialogue()
    if current is None or current.options is None:
      self.current_dialogue_id = None
      return None

    if option_index < 0 or option_index >= len(current.options):
      return current

    next_id = current.options[option_index].next
    if next_id is None:
      self.current_dialogue_id = None
      return None

    self.current_dialogue_id = next_id
    return self.get_current_dialogue()

  def end_dialogue(self):
    self.current_dialogue_id = None

  def render(self, surface: pygame.Surface):
    surface.blit(self.image, self.rect)

  def update(self, delta_time: float):
    pass
