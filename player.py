import pygame

class Player(pygame.sprite.Sprite):
  def __init__(self):
    pygame.sprite.Sprite.__init__(self)
    
    self.speed = 200
    
    self.x = 0
    self.y = 0
    
    self.image = pygame.image.load("./assets/knight.png")
    
    self.rect = self.image.get_rect()
  
  def render(self, surface):
    surface.blit(
      self.image,
      self.rect
    )
  
  def handle_movement(
    self,
    delta_time: float,
    actions: dict,
    tiles: pygame.sprite.Group,
    metadata: dict
  ):
    dx = 0
    dy = 0
    
    if actions.get(pygame.K_a) or actions.get(pygame.K_LEFT):
      dx -= self.speed * delta_time
    if actions.get(pygame.K_d) or actions.get(pygame.K_RIGHT):
      dx += self.speed * delta_time
    if actions.get(pygame.K_w) or actions.get(pygame.K_UP):
      dy -= self.speed * delta_time
    if actions.get(pygame.K_s) or actions.get(pygame.K_DOWN):
      dy += self.speed * delta_time
    
    if dx != 0:
      old_x = self.x
      self.x += dx
      self.rect.centerx = self.x
      
      hit_tiles = pygame.sprite.spritecollide(self, tiles, False)
      blocked_tiles = [t for t in hit_tiles if t.gid in metadata["collision_gid"]]
      
      if len(blocked_tiles) > 0:
        self.x = old_x
        self.rect.centerx = self.x
    
    if dy != 0:
      old_y = self.y
      self.y += dy
      self.rect.centery = self.y
      
      hit_tiles = pygame.sprite.spritecollide(self, tiles, False)
      blocked_tiles = [t for t in hit_tiles if t.gid in metadata["collision_gid"]]
      
      if len(blocked_tiles) > 0:
        self.y = old_y
        self.rect.centery = self.y
    
    self.rect.center = (self.x, self.y)

  def update(self, delta_time: float, actions: dict):
    pass
