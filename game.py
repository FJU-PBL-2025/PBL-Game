import time
import pygame

from player import Player
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

  def draw_text(self, surface, text, color, x, y):
    text_surface = self.font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_surface, text_rect)

  def load_assets(self):
    self.font = pygame.font.SysFont("arial", 20)

  def load_states(self):
    self.title_screen = TitleScreenState(self)
    self.state_stack.append(self.title_screen)

  def reset_keys(self):
    for action in self.actions:
      self.actions[action] = False
