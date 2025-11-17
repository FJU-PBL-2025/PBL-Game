import pygame

class Player(pygame.sprite.Sprite):
  def __init__(self):
    pygame.sprite.Sprite.__init__(self)
    
    self.speed = 200
    self.running_speed = 300
    self.running = False
    
    self.x = 0
    self.y = 0
    
    # 載入原始圖片
    original_image = pygame.image.load("./assets/knight.png")
    # 設定放大倍率
    scale_factor = 1.5
    original_size = original_image.get_size()
    new_size = (int(original_size[0] * scale_factor), int(original_size[1] * scale_factor))
    self.image = pygame.transform.scale(original_image, new_size)
    
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
    metadata: dict,
    game = None
  ):
    dx = 0
    dy = 0
    
    # 根據是否按下 Shift 鍵來決定速度
    current_speed = self.running_speed if actions.get(pygame.K_LSHIFT) or actions.get(pygame.K_RSHIFT) else self.speed
    
    if actions.get(pygame.K_a) or actions.get(pygame.K_LEFT):
      dx -= current_speed * delta_time
    if actions.get(pygame.K_d) or actions.get(pygame.K_RIGHT):
      dx += current_speed * delta_time
    if actions.get(pygame.K_w) or actions.get(pygame.K_UP):
      dy -= current_speed * delta_time
    if actions.get(pygame.K_s) or actions.get(pygame.K_DOWN):
      dy += current_speed * delta_time
    
    # 檢查是否與傳送門 (exit) 碰撞
    if game and "exit" in metadata:
      hit_tiles = pygame.sprite.spritecollide(self, tiles, False)
      for tile in hit_tiles:
        for exit_info in metadata["exit"]:
          # 檢查碰撞到的圖塊座標是否與 exit 中定義的座標相符
          if tile.x == exit_info["x"] and tile.y == exit_info["y"]:
            # 取得目標地圖名稱和玩家在新地圖的出生位置
            target_map = exit_info["to"]
            # 檢查出口是否定義了出生點，若無則傳入 None
            # 這允許我們切換到沒有玩家位置的場景 (例如關卡標題畫面)
            if "start_pos" in exit_info:
              player_start_pos = (exit_info["start_pos"]["x"], exit_info["start_pos"]["y"])
            else:
              player_start_pos = None
            game.change_map(target_map, player_start_pos) 
            return # 觸發傳送後，結束當前移動處理

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
