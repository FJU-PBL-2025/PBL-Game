import pygame


class InputManager():
  def __init__(self):
    self.actions: dict[int, KeyState | None] = {}
  
  def capture(self):
    for event in pygame.event.get():
      if event.type in [pygame.KEYDOWN, pygame.KEYUP] and self.actions.get(event.key) is None:
        self.actions[event.key] = KeyState()
        
      if event.type == pygame.KEYDOWN:
        self.actions[event.key].pressed = True

      if event.type == pygame.KEYUP:
        self.actions[event.key].clear()

  def tick(self, delta_time: float):
    for k in self.actions.keys():
      action = self.actions[k]
      if action.pressed:
        action.total_time += delta_time

  def reset_keys(self):
    for k in self.actions.keys():
      self.actions[k].clear()
  
  def is_key_down(self, key: int):
    if self.actions.get(key) is None:
      self.actions[key] = KeyState()
    
    return self.actions[key].pressed
  
  def is_key_down_once(self, key: int):
    if self.actions.get(key) is None:
      self.actions[key] = KeyState()
      
    if not self.actions[key].pressed:
      return False
    
    if self.actions[key].total_time != 0.0:
      return False
    
    return True
  
  def is_key_down_delayed(self, key: int, delay: float):
    if self.actions.get(key) is None:
      self.actions[key] = KeyState()
      
    if not self.actions[key].pressed:
      return False

    if self.actions[key].total_time != 0.0 and self.actions[key].total_time - self.actions[key].last_triggered < delay:
      return False
    
    self.actions[key].last_triggered = self.actions[key].total_time
    
    return True

class KeyState():
  def __init__(self):
    self.pressed: bool = False
    self.last_triggered: float = 0.0
    self.total_time: float = 0.0
    
  def clear(self):
      self.pressed = False
      self.total_time = 0.0
      self.last_triggered = 0.0
