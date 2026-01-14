import pygame
import pytmx
import json

from src.npc import Npc
from src.audio_manager import AudioManager


class MapLoader():
  def __init__(self, name: str, game = None):
    self.game = game
    self.tiles: pygame.sprite.Group[MapTile] = pygame.sprite.Group()
    self.npcs: pygame.sprite.Group[Npc] = pygame.sprite.Group()
    self.objects: pygame.sprite.Group[MapObject] = pygame.sprite.Group()
    self.map: pytmx.TiledMap | None = None
    self.metadata: MapMetadata = MapMetadata()

    self.change_map(name)

  def change_map(self, name: str):
    self.tiles.empty()
    self.npcs.empty()
    self.objects.empty()
    self.metadata.clear()
    
    self.map = pytmx.load_pygame(f"./assets/map/{name}/map.tmx")
    
    with open(f"./assets/map/{name}/map.meta.json", "r", encoding = "utf-8") as f:
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
      
      # Load objects
      for obj_data in json_data.get("object", []):
        show_when_boss_dead = obj_data.get("show_when_boss_dead", False)
        hide_when_boss_dead = obj_data.get("hide_when_boss_dead", False)
        
        # Check if object should be shown based on boss status
        should_skip = False
        if self.game:
          if show_when_boss_dead:
            if isinstance(show_when_boss_dead, list):
              # Check if all specified bosses are defeated
              all_bosses_dead = all(boss in self.game.defeated_npcs for boss in show_when_boss_dead)
              if not all_bosses_dead:
                should_skip = True
            else:
              # Original logic for boolean or single boss
              map_npc_names = entity_data.get("npc", [])
              bosses_alive = any(npc not in self.game.defeated_npcs for npc in map_npc_names)
              if bosses_alive:
                should_skip = True
          
          if hide_when_boss_dead:
            map_npc_names = entity_data.get("npc", [])
            bosses_alive = any(npc not in self.game.defeated_npcs for npc in map_npc_names)
            if not bosses_alive:
              should_skip = True
        
        if should_skip:
          continue
        
        # Get exit data if present
        obj_exit = None
        if "exit" in obj_data:
          exit_data = obj_data["exit"]
          obj_exit = MapExit(exit_data["dist"], exit_data["dist_x"], exit_data["dist_y"])
        
        map_obj = MapObject(
          obj_data["img"],
          obj_data["x"],
          obj_data["y"],
          obj_data.get("collision", True),
          self.map.tilewidth,
          self.map.tileheight,
          obj_exit
        )
        self.objects.add(map_obj)
      
      self.metadata.music = json_data.get("music", "")
      self.metadata.walk_sound = json_data.get("walk_sound", "")
      self.metadata.boss_died_exit = json_data.get("boss_died_exit", False)
      
      # Load entry point
      entry_point = json_data.get("entry_point", {"x": 16, "y": 9})  # Default center-ish position
      self.metadata.entry_x = entry_point["x"]
      self.metadata.entry_y = entry_point["y"]
    
    if self.metadata.music:
      AudioManager.play_background_music(self.metadata.music)
    
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
      # Skip defeated NPCs
      if self.game and npc_name in self.game.defeated_npcs:
        continue
      npc = Npc(npc_name, self.map.tilewidth, self.map.tileheight)
      self.npcs.add(npc)

  def render(self, surface: pygame.Surface):
    self.tiles.draw(surface)
    self.objects.draw(surface)

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
    self.walk_sound: str = ""
    self.entry_x: int = 16
    self.entry_y: int = 9
    self.boss_died_exit: bool = False
    
  def clear(self):
    self.collisions.clear()
    self.exits.clear()
    self.npc_names.clear()
    self.music = ""
    self.walk_sound = ""
    self.entry_x = 16
    self.entry_y = 9
    self.boss_died_exit = False

class MapObject(pygame.sprite.Sprite):
  def __init__(
    self,
    image_name: str,
    x: int,
    y: int,
    collision: bool,
    tile_width: int,
    tile_height: int,
    exit: "MapExit" = None
  ):
    pygame.sprite.Sprite.__init__(self)
    
    self.x: int = x
    self.y: int = y
    self.collision: bool = collision
    self.exit: MapExit = exit
    
    # Load the image
    try:
      self.image: pygame.Surface = pygame.image.load(f"./assets/map/tileset/{image_name}.png")
    except FileNotFoundError:
      # Create a placeholder if image not found
      self.image = pygame.Surface((tile_width, tile_height))
      self.image.fill((255, 0, 255))  # Magenta placeholder
    
    self.rect: pygame.Rect = pygame.Rect()
    self.rect.x = x * tile_width
    self.rect.y = y * tile_height
    self.rect.width = self.image.get_width()
    self.rect.height = self.image.get_height()

class MapExit():
  def __init__(self, dist: str, dist_x: int, dist_y: int):
    self.dist: str = dist
    self.dist_x: int = dist_x
    self.dist_y: int = dist_y
