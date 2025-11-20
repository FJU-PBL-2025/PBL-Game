import pygame
import pytmx
import json


class TiledMapRenderer():
  def __init__(self, map_name: str):
    self.tiles: pygame.sprite.Group[MapTile] = pygame.sprite.Group()
    self.map: pytmx.TiledMap | None = None
    self.metadata: MapMetadata = MapMetadata()
    
    self.change_map(map_name)

  def change_map(self, map_name: str):
    self.tiles.empty()
    self.metadata.clear()
    
    self.map = pytmx.load_pygame(f"./assets/map/{map_name}/map.tmx")
    
    with open(f"./assets/map/{map_name}/map.meta.json", "r") as f:
      json_data = json.load(f)
      
      self.metadata.collisions = json_data["collision_gid"]
      
      for exit in json_data["exit"]:
        self.metadata.exits[(exit["source_x"], exit["source_y"])] = MapExit(
          exit["dist"],
          exit["dist_x"],
          exit["dist_y"]
        )
    
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
    
  def clear(self):
    self.collisions.clear()
    self.exits.clear()

class MapExit():
  def __init__(self, dist: str, dist_x: int, dist_y: int):
    self.dist: str = dist
    self.dist_x: int = dist_x
    self.dist_y: int = dist_y
