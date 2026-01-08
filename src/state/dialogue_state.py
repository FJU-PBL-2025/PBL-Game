from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
  from src.game import Game
from src.npc import Npc
from src.state.state import State
from src.state.battle_state import BattleState
from src.state.shop_state import ShopState


class DialogueState(State):
  def __init__(self, game: "Game", npc: Npc):
    State.__init__(self, game)

    self.npc: Npc = npc
    self.index: int = 0

    self.current_dialogue = self.npc.start_dialogue()

    self.box_height: int = 200
    self.box_margin: int = 40
    self.padding: int = 20

  def update(self, delta_time: float):
    i_m = self.game.input_manager

    if self.current_dialogue is None:
      self.exit_state()
      return

    options = self.current_dialogue.options

    if options and len(options) > 0:
      if i_m.is_key_down_delayed(pygame.K_w, 0.2) or i_m.is_key_down_delayed(
        pygame.K_UP, 0.2
      ):
        if self.index == 0:
          self.index = len(options) - 1
        else:
          self.index -= 1

      if i_m.is_key_down_delayed(pygame.K_s, 0.2) or i_m.is_key_down_delayed(
        pygame.K_DOWN, 0.2
      ):
        if self.index == len(options) - 1:
          self.index = 0
        else:
          self.index += 1

      if i_m.is_key_down_once(pygame.K_RETURN) or i_m.is_key_down_once(
        pygame.K_e
      ):
        self.current_dialogue = self.npc.advance_dialogue(self.index)
        self.index = 0

        if self.npc.current_dialogue_id == "fight":
          self.exit_state()
          battle_state = BattleState(self.game, self.npc)
          battle_state.enter_state()
          return

        if self.npc.current_dialogue_id == "shop":
          self.exit_state()
          shop_state = ShopState(self.game, self.npc)
          shop_state.enter_state()
          return

        if self.current_dialogue is None:
          self.exit_state()
    else:
      if i_m.is_key_down_once(pygame.K_RETURN) or i_m.is_key_down_once(
        pygame.K_e
      ):
        self.npc.end_dialogue()
        self.exit_state()

  def render(self, surface: pygame.Surface):
    self.prev_state.render(surface)

    overlay = pygame.Surface((self.game.GAME_W, self.game.GAME_H))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(100)
    surface.blit(overlay, (0, 0))

    box_rect = pygame.Rect(
      self.box_margin,
      self.game.GAME_H - self.box_height - self.box_margin,
      self.game.GAME_W - self.box_margin * 2,
      self.box_height,
    )

    box_surface = pygame.Surface((box_rect.width, box_rect.height))
    box_surface.fill((40, 40, 60))
    box_surface.set_alpha(230)
    surface.blit(box_surface, box_rect)

    pygame.draw.rect(surface, (100, 100, 140), box_rect, 3, border_radius=8)

    if self.current_dialogue is None:
      return

    self.game.draw_text(
      surface,
      self.npc.display_name,
      (180, 180, 220),
      (box_rect.left + 80, box_rect.top + 25),
    )

    self.game.draw_text(
      surface,
      self.current_dialogue.text,
      (255, 255, 255),
      (box_rect.centerx, box_rect.top + 60),
    )

    options = self.current_dialogue.options
    if options:
      for i, opt in enumerate(options):
        prefix = "> " if self.index == i else "  "
        color = (255, 255, 100) if self.index == i else (200, 200, 200)
        self.game.draw_text(
          surface,
          prefix + opt.text,
          color,
          (box_rect.centerx, box_rect.top + 100 + i * 30),
        )
    else:
      self.game.draw_text(
        surface,
        "[Press E or Enter to continue]",
        (150, 150, 150),
        (box_rect.centerx, box_rect.top + 120),
      )
