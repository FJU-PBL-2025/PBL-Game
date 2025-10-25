import pytmx


class TiledMapRenderer():
  def __init__(self, filename):
    self.tmx_map = pytmx.load_pygame(filename)

  def render(self, surface):
    ...
