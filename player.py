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

  def update(self, delta_time: float, actions: dict):
    if actions.get(pygame.K_w) or actions.get(pygame.K_UP):
      self.y -= self.speed * delta_time
    if actions.get(pygame.K_s) or actions.get(pygame.K_DOWN):
      self.y += self.speed * delta_time
      
    if actions.get(pygame.K_a) or actions.get(pygame.K_LEFT):
      self.x -= self.speed * delta_time
    if actions.get(pygame.K_d) or actions.get(pygame.K_RIGHT):
      self.x += self.speed * delta_time
    
    self.rect.center = (self.x, self.y)
