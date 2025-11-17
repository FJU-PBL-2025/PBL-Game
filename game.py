import time
import pygame

from player import Player
from state.first_stage_state import FirstStageState
from state.first_level_state import FirstLevelState
from state.title_screen_state import TitleScreenState


class Game():
  def __init__(self):
    pygame.init()
    pygame.display.set_caption("PBL Game")
    
    self.clock = pygame.time.Clock()
    
    self.running = True
    self.playing = True
    
    self.GAME_W = 1280
    self.GAME_H = 720
    self.SCREEN_WIDTH = 1280
    self.SCREEN_HEIGHT = 720
    
    self.game_canvas = pygame.Surface(
      (self.GAME_W, self.GAME_H)
    )
    self.screen = pygame.display.set_mode(
      (self.SCREEN_WIDTH, self.SCREEN_HEIGHT),
      pygame.SCALED | pygame.RESIZABLE
    )
    
    self.actions = {}
    
    self.delta_time = 0.0
    self.prev_time = 0.0
    self.state_stack = []

    self.settings = {
        'language': 'English',
        'volume': 50,
        'x_sensitivity': 1.0,
        'y_sensitivity': 1.0,
    }
    
    self.player = Player()
    
    self.load_assets()
    self.load_states()

  def game_loop(self):
    while self.playing:
      self.get_delta_time()
      self.get_events()
      self.update()
      self.render()

  def get_events(self):
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        self.playing = False
        self.running = False

      if event.type == pygame.KEYDOWN:
        self.actions[event.key] = True

      if event.type == pygame.KEYUP:
        self.actions[event.key] = False

  def update(self):
    self.state_stack[-1].update(self.delta_time, self.actions)

  def render(self):
    self.state_stack[-1].render(self.game_canvas)

    self.screen.blit(
      pygame.transform.scale(
        self.game_canvas,
        (
          self.SCREEN_WIDTH,
          self.SCREEN_HEIGHT
        )
      ),
      (0, 0)
    )
    pygame.display.flip()

  def get_delta_time(self):
    now = time.time()
    self.delta_time = now - self.prev_time
    self.prev_time = now

  def draw_text(self, surface, text, color, x, y, align="center"):
    text_surface = self.font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if align == "center":
        text_rect.center = (x, y)
    elif align == "left":
        text_rect.midleft = (x, y)
    elif align == "right":
        text_rect.midright = (x, y)
    surface.blit(text_surface, text_rect)

  def load_assets(self):
    # 使用支援中文的字型 "微軟正黑體"。
    # 36 是字體大小，可以自行調整。
    # 如果你的系統沒有這個字型，可以換成 "msjh.ttc" 或其他中文字型名稱。
    self.font = pygame.font.SysFont("microsoftjhenghei", 36)

  def load_states(self):
    # 使用字典來管理所有關卡狀態
    self.level_states = {}
    self.title_screen = TitleScreenState(self)
    self.state_stack.append(self.title_screen)

    # 預先載入非地圖的特殊狀態
    # 地圖狀態 (如 level1) 將在 change_map 函式中動態載入
    self.level_states["first_stage_screen"] = FirstStageState(self)

  def reset_keys(self):
    for action in self.actions:
      self.actions[action] = False
  
  def enter_state(self, new_state):
    # 進入新場景前，重置按鍵狀態，避免前一個場景的按鍵影響新場景
    self.reset_keys()
    self.state_stack.append(new_state)

  def change_map(self, map_name, player_pos):
    # 如果目標地圖還沒載入，就動態載入它
    if map_name not in self.level_states:
      # 這裡假設所有關卡都使用 FirstLevelState，未來可以擴充
      self.level_states[map_name] = FirstLevelState(self, map_name=map_name)
    
    # 設定玩家在新場景的出生位置
    # 如果 player_pos 是 None，表示這是一個非地圖場景，不需要移動玩家
    if player_pos:
      self.player.x, self.player.y = player_pos
      self.player.rect.center = self.player.x, self.player.y

    self.enter_state(self.level_states[map_name])
