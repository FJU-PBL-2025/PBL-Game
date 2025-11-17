import pygame
import pytmx


class TiledMapRenderer():
  def __init__(self, filename):
    self.tiles = pygame.sprite.Group()
    
    self.change_map(filename)

  def change_map(self, filename):
    self.map = pytmx.load_pygame(filename)
    self.tiles.empty()
    for layer in self.map.visible_layers:
      for x, y, gid, in layer:
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
