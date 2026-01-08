from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
  from src.game import Game
from src.npc import Npc
from src.state.state import State
from src.shop_helper import ShopHelper


class ShopState(State):
  def __init__(self, game: "Game", npc: Npc):
    State.__init__(self, game)

    self.npc = npc
    self.selected_index = 0
    self.message = ""
    self.message_timer = 0.0

    self.shop_helper = ShopHelper(game, npc)

    self.panel_margin = 60
    self.panel_padding = 20
    self.item_height = 40
    self.title_height = 50

  def update(self, delta_time: float):
    i_m = self.game.input_manager

    if self.message_timer > 0:
      self.message_timer -= delta_time
      if self.message_timer <= 0:
        self.message = ""

    if i_m.is_key_down_once(pygame.K_ESCAPE):
      self.exit_state()
      return

    if len(self.shop_helper.shop_items) == 0:
      return

    if i_m.is_key_down_delayed(pygame.K_w, 0.15) or i_m.is_key_down_delayed(pygame.K_UP, 0.15):
      self.selected_index = (self.selected_index - 1) % len(
        self.shop_helper.shop_items
      )

    if i_m.is_key_down_delayed(pygame.K_s, 0.15) or i_m.is_key_down_delayed(pygame.K_DOWN, 0.15):
      self.selected_index = (self.selected_index + 1) % len(
        self.shop_helper.shop_items
      )

    if i_m.is_key_down_once(pygame.K_RETURN) or i_m.is_key_down_once(pygame.K_e):
      success, message = self.shop_helper.purchase_item(
        self.shop_helper.shop_items[self.selected_index]
      )
      self.message = message
      self.message_timer = 2.0

  def render(self, surface: pygame.Surface):
    self.prev_state.render(surface)

    overlay = pygame.Surface((self.game.GAME_W, self.game.GAME_H))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(150)
    surface.blit(overlay, (0, 0))

    shop_items = self.shop_helper.shop_items

    panel_width = self.game.GAME_W - self.panel_margin * 2
    content_height = self.title_height + len(shop_items) * self.item_height + 80
    panel_height = min(
      content_height + self.panel_padding * 2,
      self.game.GAME_H - self.panel_margin * 2,
    )

    panel_x = self.panel_margin
    panel_y = (self.game.GAME_H - panel_height) // 2

    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
    panel_surface = pygame.Surface((panel_width, panel_height))
    panel_surface.fill((40, 40, 60))
    panel_surface.set_alpha(230)
    surface.blit(panel_surface, panel_rect)

    pygame.draw.rect(surface, (100, 100, 140), panel_rect, 3, border_radius=8)

    title_y = panel_y + self.panel_padding + 15
    self.game.draw_text(
      surface,
      f"{self.npc.display_name}'s Shop",
      (180, 180, 220),
      (self.game.GAME_W // 2, title_y),
    )

    line_y = title_y + 25
    pygame.draw.line(
      surface,
      (80, 80, 120),
      (panel_x + 20, line_y),
      (panel_x + panel_width - 20, line_y),
      2,
    )

    items_start_y = line_y + 20

    if len(shop_items) == 0:
      self.game.draw_text(
        surface,
        "No items available",
        (150, 150, 150),
        (self.game.GAME_W // 2, items_start_y + 30),
      )
    else:
      for i, item in enumerate(shop_items):
        item_y = items_start_y + i * self.item_height

        is_selected = i == self.selected_index
        is_out_of_stock = item.stock == 0
        can_afford = self.shop_helper.can_afford(item.price)

        if is_selected:
          highlight_rect = pygame.Rect(
            panel_x + 10, item_y - 5, panel_width - 20, self.item_height - 5
          )
          highlight = pygame.Surface(
            (highlight_rect.width, highlight_rect.height), pygame.SRCALPHA
          )
          highlight.fill((255, 255, 255, 30))
          surface.blit(highlight, highlight_rect)

        if is_out_of_stock:
          name_color = (100, 100, 100)
          price_color = (80, 80, 80)
          stock_color = (150, 80, 80)
        elif not can_afford:
          name_color = (200, 150, 150) if is_selected else (180, 130, 130)
          price_color = (200, 100, 100)
          stock_color = (150, 150, 150)
        elif is_selected:
          name_color = (255, 255, 100)
          price_color = (200, 200, 100)
          stock_color = (150, 200, 150)
        else:
          name_color = (255, 255, 255)
          price_color = (180, 180, 180)
          stock_color = (150, 200, 150)

        prefix = "> " if is_selected else "  "
        name_x = panel_x + 40
        name_text = f"{prefix}{item.name}"
        name_surface = self.game.font.render(name_text, True, name_color)
        surface.blit(name_surface, (name_x, item_y))

        price_text = self.shop_helper.get_price_text(item.price)
        price_x = panel_x + panel_width // 2
        price_surface = self.game.font.render(price_text, True, price_color)
        surface.blit(price_surface, (price_x, item_y))

        if item.stock < 0:
          stock_text = "∞"
        elif item.stock == 0:
          stock_text = "SOLD OUT"
        else:
          stock_text = f"x{item.stock}"
        stock_x = panel_x + panel_width - 100
        stock_surface = self.game.font.render(stock_text, True, stock_color)
        surface.blit(stock_surface, (stock_x, item_y))

    message_y = panel_y + panel_height - 50
    if self.message:
      message_color = (
        (100, 255, 100) if "Purchased" in self.message else (255, 150, 150)
      )
      self.game.draw_text(
        surface, self.message, message_color, (self.game.GAME_W // 2, message_y)
      )

    instructions_y = panel_y + panel_height - 25
    self.game.draw_text(
      surface,
      "[W/S] Navigate  [E/Enter] Buy  [ESC] Exit",
      (150, 150, 150),
      (self.game.GAME_W // 2, instructions_y),
    )
