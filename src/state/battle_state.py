from typing import TYPE_CHECKING, List

import pygame

if TYPE_CHECKING:
  from src.game import Game
from src.battle_helper import BattleHelper, BattleEntity, BattleSkill
from src.state.state import State
from src.npc import Npc


class BattleState(State):
  def __init__(self, game: "Game", npc: "Npc"):
    State.__init__(self, game)
    
    self.game = game
    self.npc = npc
    
    self.battle_helper = BattleHelper(self.game, self.npc)
    
    self.skill_index: int = 0
    self.selected_skills: List[str] = []
    self.is_player_turn: bool = True
    self.battle_over: bool = False
    self.player_won: bool = False
    self.turn_delay: float = 0.0
    
    self.bar_width: int = 200
    self.bar_height: int = 20
    self.padding: int = 20
    
    self.player_sprite = pygame.image.load("./assets/knight.png")
    self.enemy_sprite = self.npc.image
  
  def _get_available_skills(self) -> List[BattleSkill]:
    return [
      skill for skill in self.battle_helper.player.skills.values()
      if skill.current_cooldown == 0
    ]
  
  def update(self, delta_time: float):
    i_m = self.game.input_manager
    
    if self.battle_over:
      if i_m.is_key_down_once(pygame.K_RETURN):
        self.exit_state()
      return
    
    if not self.is_player_turn:
      self.turn_delay -= delta_time
      if self.turn_delay <= 0:
        result = self.battle_helper.execute_enemy_turn()
        if result is not None:
          self.battle_over = True
          self.player_won = result
        else:
          self.is_player_turn = True
      return
    
    player = self.battle_helper.player
    skill_list = list(player.skills.values())
    
    if i_m.is_key_down_delayed(pygame.K_w, 0.15) or i_m.is_key_down_delayed(pygame.K_UP, 0.15):
      self.skill_index = (self.skill_index - 1) % len(skill_list)
    
    if i_m.is_key_down_delayed(pygame.K_s, 0.15) or i_m.is_key_down_delayed(pygame.K_DOWN, 0.15):
      self.skill_index = (self.skill_index + 1) % len(skill_list)
    
    if i_m.is_key_down_once(pygame.K_SPACE):
      current_skill = skill_list[self.skill_index]
      if current_skill.current_cooldown == 0:
        if current_skill.id in self.selected_skills:
          self.selected_skills.remove(current_skill.id)
        else:
          self.selected_skills.append(current_skill.id)
    
    if i_m.is_key_down_once(pygame.K_RETURN):
      result = self.battle_helper.execute_player_turn(self.selected_skills)
      self.selected_skills = []
      
      if result is not None:
        self.battle_over = True
        self.player_won = result
      else:
        self.is_player_turn = False
        self.turn_delay = 1.0  

  def _draw_hp_bar(
    self,
    surface: pygame.Surface,
    entity: BattleEntity,
    x: int,
    y: int,
    align_right: bool = False
  ):
    hp_ratio = max(0, entity.current_hp / entity.max_hp)
    shield_ratio = min(1, entity.shield / entity.max_hp) if entity.shield > 0 else 0

    bar_x = x - self.bar_width if align_right else x
    
    pygame.draw.rect(
      surface,
      (60, 60, 60),
      (bar_x, y, self.bar_width, self.bar_height),
      border_radius = 4
    )
    
    hp_width = int(self.bar_width * hp_ratio)
    if hp_width > 0:
      hp_color = (50, 200, 80) if hp_ratio > 0.3 else (200, 80, 50)
      pygame.draw.rect(
        surface,
        hp_color,
        (bar_x, y, hp_width, self.bar_height),
        border_radius = 4
      )
    
    if shield_ratio > 0:
      shield_width = int(self.bar_width * shield_ratio)
      pygame.draw.rect(
        surface,
        (100, 150, 220),
        (bar_x, y + self.bar_height + 4, shield_width, 8),
        border_radius = 2
      )
    
    hp_text = f"{int(entity.current_hp)} / {entity.max_hp}"
    text_surface = self.game.font.render(hp_text, True, (255, 255, 255))
    text_rect = text_surface.get_rect()
    text_rect.center = (bar_x + self.bar_width // 2, y + self.bar_height // 2)
    surface.blit(text_surface, text_rect)
    
    if entity.shield > 0:
      shield_text = f"+{entity.shield} Shield"
      shield_surface = self.game.font.render(shield_text, True, (150, 200, 255))
      shield_rect = shield_surface.get_rect()
      shield_rect.center = (bar_x + self.bar_width // 2, y + self.bar_height + 20)
      surface.blit(shield_surface, shield_rect)

  def _draw_effects(
    self,
    surface: pygame.Surface,
    entity: BattleEntity,
    x: int,
    y: int,
    align_right: bool = False
  ):
    if not entity.effects:
      return
    
    effect_texts = [f"{e.name}({e.duration})" for e in entity.effects]
    effect_str = ", ".join(effect_texts)
    
    color = (255, 200, 100) if any(e.negative for e in entity.effects) else (100, 255, 200)
    text_surface = self.game.font.render(effect_str, True, color)
    text_rect = text_surface.get_rect()
    
    if align_right:
      text_rect.right = x
    else:
      text_rect.left = x
    text_rect.top = y
    
    surface.blit(text_surface, text_rect)

  def _draw_skill_panel(self, surface: pygame.Surface):
    panel_height = 180
    panel_y = self.game.GAME_H - panel_height
    
    panel_surface = pygame.Surface((self.game.GAME_W, panel_height))
    panel_surface.fill((30, 30, 50))
    panel_surface.set_alpha(240)
    surface.blit(panel_surface, (0, panel_y))
    
    pygame.draw.line(
      surface,
      (80, 80, 120),
      (0, panel_y),
      (self.game.GAME_W, panel_y),
      2
    )
    
    turn_text = "YOUR TURN - Select Skills (Space to toggle, Enter to confirm)" if self.is_player_turn else "ENEMY TURN..."
    self.game.draw_text(
      surface,
      turn_text,
      (200, 200, 255),
      (self.game.GAME_W // 2, panel_y + 20)
    )
    
    player = self.battle_helper.player
    skill_list = list(player.skills.values())
    
    start_x = 100
    start_y = panel_y + 50
    col_width = 300
    row_height = 35
    
    for i, skill in enumerate(skill_list):
      col = i % 2
      row = i // 2
      
      x = start_x + col * col_width
      y = start_y + row * row_height
      
      is_selected = skill.id in self.selected_skills
      is_cursor = i == self.skill_index
      on_cooldown = skill.current_cooldown > 0
      
      if on_cooldown:
        color = (100, 100, 100)
        prefix = f"[CD: {skill.current_cooldown}] "
      elif is_selected:
        color = (100, 255, 150)
        prefix = "[v] "
      else:
        color = (255, 255, 255)
        prefix = "[ ] "
      
      if is_cursor:
        prefix = "> " + prefix
        color = (255, 255, 100) if not on_cooldown else (150, 150, 100)
      else:
        prefix = "  " + prefix
      
      skill_text = f"{prefix}{skill.name}"
      text_surface = self.game.font.render(skill_text, True, color)
      surface.blit(text_surface, (x, y))

  def render(self, surface: pygame.Surface):
    surface.fill((20, 20, 35))
    
    battle_area_height = self.game.GAME_H - 180
    
    player_x = self.game.GAME_W // 4
    player_y = battle_area_height // 2
    player_rect = self.player_sprite.get_rect(center = (player_x, player_y))
    surface.blit(self.player_sprite, player_rect)
    
    enemy_x = 3 * self.game.GAME_W // 4
    enemy_y = battle_area_height // 2
    enemy_rect = self.enemy_sprite.get_rect(center = (enemy_x, enemy_y))
    surface.blit(self.enemy_sprite, enemy_rect)
    
    self.game.draw_text(
      surface,
      self.battle_helper.player.name,
      (255, 255, 255),
      (player_x, 30)
    )
    self._draw_hp_bar(
      surface,
      self.battle_helper.player,
      player_x - self.bar_width // 2,
      50
    )
    self._draw_effects(
      surface,
      self.battle_helper.player,
      player_x - self.bar_width // 2,
      100
    )
    
    self.game.draw_text(
      surface,
      self.battle_helper.enemy.name,
      (255, 100, 100),
      (enemy_x, 30)
    )
    self._draw_hp_bar(
      surface,
      self.battle_helper.enemy,
      enemy_x - self.bar_width // 2,
      50
    )
    self._draw_effects(
      surface,
      self.battle_helper.enemy,
      enemy_x - self.bar_width // 2,
      100
    )
    
    if self.battle_helper.player.frozen:
      self.game.draw_text(
        surface,
        "FROZEN!",
        (100, 200, 255),
        (player_x, player_y + 80)
      )
    if self.battle_helper.enemy.frozen:
      self.game.draw_text(
        surface,
        "FROZEN!",
        (100, 200, 255),
        (enemy_x, enemy_y + 80)
      )
    
    if not self.battle_over:
      self._draw_skill_panel(surface)
    
    if self.battle_over:
      overlay = pygame.Surface((self.game.GAME_W, self.game.GAME_H))
      overlay.fill((0, 0, 0))
      overlay.set_alpha(180)
      surface.blit(overlay, (0, 0))
      
      if self.player_won:
        result_text = "VICTORY!"
        result_color = (100, 255, 100)
      else:
        result_text = "DEFEAT..."
        result_color = (255, 100, 100)
      
      self.game.draw_text(
        surface,
        result_text,
        result_color,
        (self.game.GAME_W // 2, self.game.GAME_H // 2 - 30)
      )
      self.game.draw_text(
        surface,
        "[Press Enter to continue]",
        (200, 200, 200),
        (self.game.GAME_W // 2, self.game.GAME_H // 2 + 20)
      )
