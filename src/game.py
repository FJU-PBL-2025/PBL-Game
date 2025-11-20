import time
import pygame

from src.input_manager import InputManager
from src.player import Player
from src.state.state import State
from src.state.title_screen_state import TitleScreenState


class Game():
  def __init__(self):
    pygame.init()
    pygame.display.set_caption("PBL Game")
    
    self.clock: pygame.time.Clock = pygame.time.Clock()
    
    self.running: bool = True
    self.playing: bool = True
    
    self.GAME_W: int = 1280
    self.GAME_H: int = 720
    self.SCREEN_WIDTH: int = 1280
    self.SCREEN_HEIGHT: int = 720
    
    self.game_canvas: pygame.Surface = pygame.Surface(
      (self.GAME_W, self.GAME_H)
    )
    self.screen: pygame.Surface = pygame.display.set_mode(
      (self.SCREEN_WIDTH, self.SCREEN_HEIGHT),
      pygame.SCALED | pygame.RESIZABLE
    )
    
    self.delta_time: float = 0.0
    self.prev_time: float = 0.0
    self.state_stack: list[State] = []
    
    self.player: Player = Player()
    self.input_manager: InputManager = InputManager()
    
    self.load_assets()
    self.load_states()

  def game_loop(self):
    while self.playing:
      self.get_delta_time()
      # 只在主迴圈呼叫一次 event.get()
      events = pygame.event.get()
      self.get_events(events)
      # 更新 input_manager 的狀態
      self.input_manager.capture_events(events)
      self.update()
      self.render()
      self.input_manager.tick(self.delta_time)

  def get_events(self, events):
    for event in events:
      if event.type == pygame.QUIT:
        self.playing = False
        self.running = False

  def update(self):
    self.state_stack[-1].update(self.delta_time)

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

  def draw_text(
    self,
    surface: pygame.Surface,
    text: str | bytes | None,
    color: pygame.typing.ColorLike,
    center: tuple
  ):
    text_surface = self.font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = center
    surface.blit(text_surface, text_rect)

  def load_assets(self):
    self.font = pygame.font.SysFont("arial", 20)

  def load_states(self):
    self.title_screen = TitleScreenState(self)
    self.state_stack.append(self.title_screen)
