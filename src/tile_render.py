import pygame
import pytmx
import json


class TiledMapRenderer():
  def __init__(self, map_name: str):
    self.tiles: pygame.sprite.Group[Tile] = pygame.sprite.Group()
    self.map: pytmx.TiledMap | None = None
    self.metadata: dict | None = None
    
    self.change_map(map_name)

  def change_map(self, map_name: str):
    self.tiles.empty()
    
    self.map = pytmx.load_pygame(f"./assets/map/{map_name}/map.tmx")
    
    with open(f"./assets/map/{map_name}/map.meta.json", "r") as f:
      self.metadata = json.load(f)
    
    for layer in self.map.visible_layers:
      for x, y, gid in layer:
        tile = Tile(
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

class Tile(pygame.sprite.Sprite):
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
