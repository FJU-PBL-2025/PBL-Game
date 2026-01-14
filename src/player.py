import pygame

from src.input_manager import InputManager
from src.audio_manager import AudioManager
from src.map_loader import MapMetadata, MapTile, MapObject


class Player(pygame.sprite.Sprite):
  def __init__(self):
    pygame.sprite.Sprite.__init__(self)
    
    self.speed: int = 200
    
    self.x: int = 0
    self.y: int = 0
    
    self.in_exit: bool = False
    
    # Load player character sprites for 8 directions and scale them
    original_sprites = {
      'south': pygame.image.load("./assets/icon/south.png"),
      'south-east': pygame.image.load("./assets/icon/south-east.png"),
      'east': pygame.image.load("./assets/icon/east.png"),
      'north-east': pygame.image.load("./assets/icon/north-east.png"),
      'north': pygame.image.load("./assets/icon/north.png"),
      'north-west': pygame.image.load("./assets/icon/north-west.png"),
      'west': pygame.image.load("./assets/icon/west.png"),
      'south-west': pygame.image.load("./assets/icon/south-west.png")
    }
    
    # Scale all sprites by 1.75x
    self.sprites = {}
    for direction, sprite in original_sprites.items():
      scaled_size = (int(sprite.get_width() * 1.75), int(sprite.get_height() * 1.75))
      self.sprites[direction] = pygame.transform.scale(sprite, scaled_size)
    
    self.current_direction = 'south'
    self.image: pygame.Surface = self.sprites[self.current_direction]
    
    # Use original size for collision detection, not scaled size
    original_size = original_sprites[self.current_direction].get_rect()
    self.rect: pygame.Rect = pygame.Rect(0, 0, original_size.width, original_size.height)
  
  def update_direction(self, dx: float, dy: float):
    """Update player direction based on movement"""
    if dx == 0 and dy == 0:
      return  # No movement, keep current direction
    
    # Determine direction based on movement
    if dy > 0:  # Moving down
      if dx > 0:
        self.current_direction = 'south-east'
      elif dx < 0:
        self.current_direction = 'south-west'
      else:
        self.current_direction = 'south'
    elif dy < 0:  # Moving up
      if dx > 0:
        self.current_direction = 'north-east'
      elif dx < 0:
        self.current_direction = 'north-west'
      else:
        self.current_direction = 'north'
    else:  # Moving horizontally
      if dx > 0:
        self.current_direction = 'east'
      else:
        self.current_direction = 'west'
    
    # Update sprite
    self.image = self.sprites[self.current_direction]

  def render(self, surface: pygame.Surface):
    # Center the scaled image on the collision rect
    image_rect = self.image.get_rect()
    image_rect.center = self.rect.center
    surface.blit(
      self.image,
      image_rect
    )
  
  def handle_movement(
    self,
    delta_time: float,
    input_manager: InputManager,
    tiles: pygame.sprite.Group[MapTile],
    objects: pygame.sprite.Group[MapObject],
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
    
    # Update direction based on movement
    self.update_direction(dx, dy)
    
    hit_tiles_set: set[MapTile] = set()
    
    if dx != 0:
      old_x = self.x
      self.x += dx
      self.rect.centerx = self.x
      
      hit_tiles = pygame.sprite.spritecollide(self, tiles, False)
      hit_tiles_set.update(hit_tiles)
      blocked_tiles = [t for t in hit_tiles if t.gid in metadata.collisions]
      
      # Check collision with objects
      hit_objects = pygame.sprite.spritecollide(self, objects, False)
      blocked_objects = [o for o in hit_objects if o.collision]
      
      if len(blocked_tiles) > 0 or len(blocked_objects) > 0:
        self.x = old_x
        self.rect.centerx = self.x
    
    if dy != 0:
      old_y = self.y
      self.y += dy
      self.rect.centery = self.y
      
      hit_tiles = pygame.sprite.spritecollide(self, tiles, False)
      hit_tiles_set.update(hit_tiles)
      blocked_tiles = [t for t in hit_tiles if t.gid in metadata.collisions]
      
      # Check collision with objects
      hit_objects = pygame.sprite.spritecollide(self, objects, False)
      blocked_objects = [o for o in hit_objects if o.collision]
      
      if len(blocked_tiles) > 0 or len(blocked_objects) > 0:
        self.y = old_y
        self.rect.centery = self.y
    
    self.rect.center = (self.x, self.y)
    
    if dx == 0 and dy == 0:
      hit_tiles_set.update(pygame.sprite.spritecollide(self, tiles, False))
    
    if dx == 0 and dy == 0:
      AudioManager.stop_sound()
    else:
      AudioManager.play_sound(metadata.walk_sound)
    
    return list(hit_tiles_set)

  def update(self, delta_time: float):
    pass

  def set_position(self, x: int, y: int):
    self.x = x
    self.y = y
