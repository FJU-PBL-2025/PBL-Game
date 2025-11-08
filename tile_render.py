import pygame
import pytmx


class TiledMapRenderer():
  def __init__(self, filename):
    self.map = pytmx.load_pygame(filename)

  def render(self, surface: pygame.Surface):
    for layer in self.map.visible_layers:
      for x, y, gid, in layer:
        tile = self.map.get_tile_image_by_gid(gid)
        surface.blit(
          tile,
          (
            x * self.map.tilewidth,
            y * self.map.tileheight
          )
        )

