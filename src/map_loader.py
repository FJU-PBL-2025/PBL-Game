import pygame
import pytmx
import json

from src.npc import Npc
from src.audio_manager import AudioManager


class MapLoader():
  def __init__(self, name: str, audio_manager: AudioManager):
    self.tiles: pygame.sprite.Group[MapTile] = pygame.sprite.Group()
    self.npcs: pygame.sprite.Group[Npc] = pygame.sprite.Group()
    self.map: pytmx.TiledMap | None = None
    self.metadata: MapMetadata = MapMetadata()

    self.change_map(name, audio_manager)

  def change_map(self, name: str, audio_manager: AudioManager):
    self.tiles.empty()
    self.npcs.empty()
    self.metadata.clear()
    
    self.map = pytmx.load_pygame(f"./assets/map/{name}/map.tmx")
    
    with open(f"./assets/map/{name}/map.meta.json", "r") as f:
      json_data = json.load(f)
      
      self.metadata.collisions = json_data["collision_gid"]
      
      for exit in json_data["exit"]:
        self.metadata.exits[(exit["source_x"], exit["source_y"])] = MapExit(
          exit["dist"],
          exit["dist_x"],
          exit["dist_y"]
        )
      
      entity_data = json_data.get("entity", {})
      self.metadata.npc_names = entity_data.get("npc", [])
      
      self.metadata.music = json_data.get("music", "")
    
    if self.metadata.music:
      audio_manager.play_background_music(self.metadata.music)
    
    for layer in self.map.visible_layers:
      for x, y, gid in layer:
        tile = MapTile(
          self.map.get_tile_image_by_gid(gid),
          self.map.tiledgidmap[gid],
          x, y,
          self.map.tilewidth,
          self.map.tileheight
        )
        
        self.tiles.add(tile)
    
    for npc_name in self.metadata.npc_names:
      npc = Npc(npc_name, self.map.tilewidth, self.map.tileheight)
      self.npcs.add(npc)

  def render(self, surface: pygame.Surface):
    self.tiles.draw(
      surface
    )

class MapTile(pygame.sprite.Sprite):
  def __init__(
    self,
    image: pygame.Surface,
    gid: int,
    x: int,
    y: int,
    width: int,
    height: int
  ):
    pygame.sprite.Sprite.__init__(self)
    
    self.x: int = x
    self.y: int = y
    self.gid: int = gid
    
    self.image: pygame.Surface = image
    self.rect: pygame.Rect = pygame.Rect()
    self.rect.centerx = x * width
    self.rect.centery = y * height
    self.rect.width = width
    self.rect.height = height

class MapMetadata():
  def __init__(self):
    self.collisions: list[int] = []
    self.exits: dict[tuple[int], MapExit] = {}
    self.npc_names: list[str] = []
    self.music: str = ""
    
  def clear(self):
    self.collisions.clear()
    self.exits.clear()
    self.npc_names.clear()
    self.music = ""

class MapExit():
  def __init__(self, dist: str, dist_x: int, dist_y: int):
    self.dist: str = dist
    self.dist_x: int = dist_x
    self.dist_y: int = dist_y
