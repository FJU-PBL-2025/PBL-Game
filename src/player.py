import pygame

from src.input_manager import InputManager
from src.tile_render import MapMetadata, MapTile


class Player(pygame.sprite.Sprite):
  def __init__(self):
    pygame.sprite.Sprite.__init__(self)
    
    self.speed: int = 200
    
    self.x: int = 0
    self.y: int = 0
    
    self.in_exit: bool = False
    
    self.image: pygame.Surface = pygame.image.load("./assets/knight.png")
    
    self.rect: pygame.Rect = self.image.get_rect()
  
  def render(self, surface: pygame.Surface):
    surface.blit(
      self.image,
      self.rect
    )
  
  def handle_movement(
    self,
    delta_time: float,
    input_manager: InputManager,
    tiles: pygame.sprite.Group[MapTile],
    metadata: MapMetadata
  ) -> list[MapTile]:
    dx = 0
    dy = 0
    
    if input_manager.is_key_down(pygame.K_a) or input_manager.is_key_down(pygame.K_LEFT):
      dx -= self.speed * delta_time
    if input_manager.is_key_down(pygame.K_d) or input_manager.is_key_down(pygame.K_RIGHT):
      dx += self.speed * delta_time
    if input_manager.is_key_down(pygame.K_w) or input_manager.is_key_down(pygame.K_UP):
      dy -= self.speed * delta_time
    if input_manager.is_key_down(pygame.K_s) or input_manager.is_key_down(pygame.K_DOWN):
      dy += self.speed * delta_time
    
    hit_tiles_set = set()
    
    if dx != 0:
      old_x = self.x
      self.x += dx
      self.rect.centerx = self.x
      
      hit_tiles = pygame.sprite.spritecollide(self, tiles, False)
      hit_tiles_set.update(hit_tiles)
      blocked_tiles = [t for t in hit_tiles if t.gid in metadata.collisions]
      
      if len(blocked_tiles) > 0:
        self.x = old_x
        self.rect.centerx = self.x
    
    if dy != 0:
      old_y = self.y
      self.y += dy
      self.rect.centery = self.y
      
      hit_tiles = pygame.sprite.spritecollide(self, tiles, False)
      hit_tiles_set.update(hit_tiles)
      blocked_tiles = [t for t in hit_tiles if t.gid in metadata.collisions]
      
      if len(blocked_tiles) > 0:
        self.y = old_y
        self.rect.centery = self.y
    
    self.rect.center = (self.x, self.y)
    
    if dx == 0 and dy == 0:
      hit_tiles_set.update(pygame.sprite.spritecollide(self, tiles, False))
    
    return list(hit_tiles_set)

  def update(self, delta_time: float):
    pass

  def set_position(self, x: int, y: int):
    self.x = x
    self.y = y
