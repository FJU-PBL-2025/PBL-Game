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
    self.showing_level_up: bool = False
    self.level_up_info: dict = None
    
    self.bar_width: int = 200
    self.bar_height: int = 20
    self.padding: int = 20
    
    # Load player sprite and scale it 3x (south-east facing enemy)
    original_player_sprite = pygame.image.load("./assets/icon/south-east.png")
    original_size = original_player_sprite.get_size()
    self.player_sprite = pygame.transform.scale(
      original_player_sprite, 
      (original_size[0] * 3, original_size[1] * 3)
    )
    
    # Scale enemy sprite - max 8x from original image
    # Get the original image before NPC scaling was applied
    original_enemy_image = pygame.image.load(f"./assets/entity/npc/{self.npc.name}/npc.meta.json".replace("npc.meta.json", "").rstrip("/") + "/../../../" + "entity/boss/" + self.npc.name + "/rotations/south.png")
    import json
    with open(f"./assets/entity/npc/{self.npc.name}/npc.meta.json", "r", encoding = "utf-8") as f:
      npc_data = json.load(f)
    # Load south-west facing image for battle
    enemy_img_path = npc_data["source_img"].replace("south.png", "south-west.png")
    original_enemy_image = pygame.image.load(enemy_img_path)
    
    # Calculate battle scale: use npc scale but cap at 8
    battle_scale = min(self.npc.scale, 8)
    self.enemy_sprite = pygame.transform.scale(
      original_enemy_image,
      (int(original_enemy_image.get_width() * battle_scale), int(original_enemy_image.get_height() * battle_scale))
    )

    self.reward_given: bool = False
  
  def _get_available_skills(self) -> List[BattleSkill]:
    return [
      skill for skill in self.battle_helper.player.skills.values()
      if skill.current_cooldown == 0
    ]
  
  def update(self, delta_time: float):
    i_m = self.game.input_manager
    
    if self.battle_over:
      if not self.reward_given and self.player_won:
        self.reward_given = True
        if self.battle_helper.enemy.reward:
          for item_id, count in self.battle_helper.enemy.reward.items():
            self.game.inventory.add_item(item_id, count)

      if i_m.is_key_down_once(pygame.K_RETURN):
        # If showing level up message, dismiss it first
        if self.showing_level_up:
          self.showing_level_up = False
          self.exit_state()
          return
        
        if not self.player_won:
          # Player died, teleport to village (新手村)
          self._teleport_to_village()
          self.exit_state()
        else:
          # Player won - mark NPC as defeated and remove from current map
          self.game.defeated_npcs.add(self.npc.name)
          self._remove_defeated_npc()
          # Level up (max level 7)
          if self.game.player_level < 7:
            old_level = self.game.player_level
            old_hp = self.game.level_hp[old_level]
            self.game.player_level += 1
            new_hp = self.game.level_hp[self.game.player_level]
            
            # Prepare level up info
            self.level_up_info = {
              'new_level': self.game.player_level,
              'hp_increase': new_hp - old_hp,
              'new_hp': new_hp,
              'skills': self._get_unlock_skills(self.game.player_level)
            }
            self.showing_level_up = True
          else:
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
    
    turn_text = "你的回合 - 選擇技能 (空白鍵切換，Enter 確認)" if self.is_player_turn else "敵人回合..."
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
      f"LV{self.game.player_level} {self.battle_helper.player.name}",
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
        result_text = "您贏了！"
        result_color = (100, 255, 100)
      else:
        result_text = "You Died!"
        result_color = (255, 100, 100)
      
      self.game.draw_text(
        surface,
        result_text,
        result_color,
        (self.game.GAME_W // 2, self.game.GAME_H // 2 - 30)
      )
      
      if not self.showing_level_up:
        self.game.draw_text(
          surface,
          "[按下 Enter 繼續]",
          (200, 200, 200),
          (self.game.GAME_W // 2, self.game.GAME_H // 2 + 20)
        )
      else:
        # Show level up message
        self._draw_level_up_screen(surface)

  def _get_unlock_skills(self, level: int) -> list[str]:
    """Get skills unlocked at the given level"""
    level_skills = {
      2: ["界王拳", "奧術彈"],
      3: ["反擊架式", "光之波動"],
      4: ["光之太刀", "隕石球"],
      5: ["光能盾牌", "治癒聖光"],
      6: ["Excalibur", "噴射火焰"],
      7: ["星爆氣流斬", "領域展開"]
    }
    return level_skills.get(level, [])

  def _draw_level_up_screen(self, surface: pygame.Surface):
    """Draw level up message overlay"""
    if not self.level_up_info:
      return
    
    # Draw level up box
    box_width = 400
    box_height = 250
    box_x = (self.game.GAME_W - box_width) // 2
    box_y = (self.game.GAME_H - box_height) // 2 + 50
    
    # Draw box background
    pygame.draw.rect(
      surface,
      (40, 40, 60),
      (box_x, box_y, box_width, box_height),
      border_radius=10
    )
    pygame.draw.rect(
      surface,
      (100, 200, 255),
      (box_x, box_y, box_width, box_height),
      width=3,
      border_radius=10
    )
    
    # Level up title
    self.game.draw_text(
      surface,
      f"升級到 LV{self.level_up_info['new_level']}！",
      (255, 220, 100),
      (self.game.GAME_W // 2, box_y + 35)
    )
    
    # HP increase
    self.game.draw_text(
      surface,
      f"血量上限提升：{self.level_up_info['new_hp'] - self.level_up_info['hp_increase']} → {self.level_up_info['new_hp']} (+{self.level_up_info['hp_increase']})",
      (100, 255, 150),
      (self.game.GAME_W // 2, box_y + 80)
    )
    
    # Unlocked skills
    skills = self.level_up_info['skills']
    if skills:
      self.game.draw_text(
        surface,
        "解鎖新技能：",
        (200, 200, 255),
        (self.game.GAME_W // 2, box_y + 120)
      )
      skill_text = "、".join(skills)
      self.game.draw_text(
        surface,
        skill_text,
        (255, 255, 255),
        (self.game.GAME_W // 2, box_y + 155)
      )
    
    # Continue prompt
    self.game.draw_text(
      surface,
      "[按下 Enter 繼續]",
      (180, 180, 180),
      (self.game.GAME_W // 2, box_y + box_height - 30)
    )

  def _teleport_to_village(self):
    """Player died, teleport to village (新手村)"""
    # Find GameWorldState in the state stack
    from src.state.game_world_state import GameWorldState
    
    for state in self.game.state_stack:
      if isinstance(state, GameWorldState):
        # Change map to village (新手村)
        state.map_loader.change_map("village")
        
        # Reset player position to village entry point
        self.game.player.set_position(
          state.map_loader.metadata.entry_x * state.map_loader.map.tilewidth + state.map_loader.map.tilewidth // 2,
          state.map_loader.metadata.entry_y * state.map_loader.map.tileheight + state.map_loader.map.tileheight // 2
        )
        
        # Player respawns with full health (handled in next battle)
        break

  def _remove_defeated_npc(self):
    """Remove the defeated NPC from the current map"""
    from src.state.game_world_state import GameWorldState
    
    for state in self.game.state_stack:
      if isinstance(state, GameWorldState):
        # Remove this NPC from the map's NPC group
        for npc in state.map_loader.npcs:
          if npc.name == self.npc.name:
            state.map_loader.npcs.remove(npc)
            break
        
        # Reload objects to update show_when_boss_dead / hide_when_boss_dead
        self._reload_objects(state.map_loader)
        break

  def _reload_objects(self, map_loader):
    """Reload objects to reflect boss death status"""
    import json
    from src.map_loader import MapObject, MapExit
    
    # Get current map name from path
    # Find the map name by checking map file path
    map_path = None
    for layer in map_loader.map.visible_layers:
      break  # Just need to confirm map is loaded
    
    # Get map name from the map loader's map filename
    map_name = map_loader.map.filename.split("/")[-2]
    
    with open(f"./assets/map/{map_name}/map.meta.json", "r", encoding = "utf-8") as f:
      json_data = json.load(f)
    
    # Get entity data for boss status check
    entity_data = json_data.get("entity", {})
    map_npc_names = entity_data.get("npc", [])
    bosses_alive = any(npc not in self.game.defeated_npcs for npc in map_npc_names)
    
    # Clear existing objects and reload
    map_loader.objects.empty()
    
    for obj_data in json_data.get("object", []):
      show_when_boss_dead = obj_data.get("show_when_boss_dead", False)
      hide_when_boss_dead = obj_data.get("hide_when_boss_dead", False)
      
      # Skip objects based on boss status
      if show_when_boss_dead and bosses_alive:
        continue
      if hide_when_boss_dead and not bosses_alive:
        continue
      
      # Get exit data if present
      obj_exit = None
      if "exit" in obj_data:
        exit_data = obj_data["exit"]
        obj_exit = MapExit(exit_data["dist"], exit_data["dist_x"], exit_data["dist_y"])
      
      map_obj = MapObject(
        obj_data["img"],
        obj_data["x"],
        obj_data["y"],
        obj_data.get("collision", True),
        map_loader.map.tilewidth,
        map_loader.map.tileheight,
        obj_exit
      )
      map_loader.objects.add(map_obj)
