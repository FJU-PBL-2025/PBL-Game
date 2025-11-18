import pygame
import pytmx
import json


class TiledMapRenderer():
  def __init__(self, map_name):
    self.tiles = pygame.sprite.Group()
    self.map = None
    self.metadata = None
    
    self.change_map(map_name)

  def change_map(self, map_name):
    self.map = pytmx.load_pygame(f"./assets/map/{map_name}/map.tmx")
    with open(f"./assets/map/{map_name}/map.meta.json", "r") as f:
      self.metadata = json.load(f)
    
    self.tiles.empty()
    
    for layer in self.map.visible_layers:
      for x, y, gid in layer:
        tile = Tile(
          self.map.get_tile_image_by_gid(gid),
          gid,
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
  def __init__(self, image, gid, x, y, width, height):
    pygame.sprite.Sprite.__init__(self)
    
    self.x = x
    self.y = y
    self.gid = gid
    
    self.image = image
    self.rect = pygame.Rect()
    self.rect.centerx = x * width
    self.rect.centery = y * height
    self.rect.width = width
    self.rect.height = height
