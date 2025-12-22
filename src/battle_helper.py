from typing import TYPE_CHECKING, List
from dataclasses import dataclass
import json
import random

if TYPE_CHECKING:
  from src.game import Game
from src.npc import Npc


@dataclass
class SkillEffect:
  type: str
  name: str
  negative: bool
  target: str
  chance: float
  value: int | None
  duration: int

@dataclass
class BattleEffect:
  type: str
  name: str
  negative: bool
  hanging: bool
  value: int | None
  duration: int

@dataclass
class BattleSkill:
  id: str
  name: str
  description: str
  physical_damage: int
  magical_damage: int
  heal: int
  shield: int
  purify: bool
  effect: List[SkillEffect]
  hanging: bool
  cooldown: int
  current_cooldown: int

@dataclass
class BattleEntity:
  name: str
  max_hp: int
  current_hp: int
  shield: int
  physical_buff: int
  magical_buff: int
  frozen: bool
  weakness: int
  skills: dict[str, BattleSkill]
  effects: List[BattleEffect]

class BattleHelper:
  def __init__(self, game: "Game", npc: Npc):
    self.game = game
    
    self.enemy: BattleEntity = BattleHelper._load_npc_battle_data(npc)
    self.player: BattleEntity = BattleHelper._load_player_battle_data()
  
  @staticmethod
  def _load_skills(raw_skills: map) -> dict[str, BattleSkill]:
    with open("./assets/effects.json", "r") as f:
      effect_data = json.load(f)
    
    skills = {}
    
    for skill_id, raw_skill in raw_skills.items():
      effects = []
      
      for raw_effect in raw_skill["effect"]:
        effect_meta = effect_data[raw_effect["type"]]
        
        duration = raw_effect.get("duration", None)
        
        if duration is None:
          duration = effect_meta["duration"]
        
        effects.append(
          SkillEffect(
            type = raw_effect["type"],
            name = effect_meta["name"],
            negative = effect_meta["negative"],
            target = raw_effect["target"],
            chance = raw_effect["chance"],
            value = raw_effect.get("value", None),
            duration = duration
          )
        )

      skills[skill_id] = BattleSkill(
        id = skill_id,
        name = raw_skill["name"],
        description = raw_skill["description"],
        physical_damage = raw_skill["physical_damage"],
        magical_damage = raw_skill["magical_damage"],
        heal = raw_skill["heal"],
        shield = raw_skill["shield"],
        purify = raw_skill["purify"],
        effect = effects,
        hanging = False,
        cooldown = raw_skill["cooldown"],
        current_cooldown = 0
      )
    
    return skills
  
  @staticmethod
  def _load_npc_battle_data(npc: Npc):
    with open(f"./assets/entity/npc/{npc.name}/npc.meta.json", "r") as f:
      data = json.load(f)

    entity = BattleEntity(
      name = data.get("display_name", npc.name),
      max_hp = data["hp"],
      current_hp = data["hp"],
      shield = 0,
      physical_buff = 0,
      magical_buff = 0,
      frozen = False,
      weakness = 0,
      skills = BattleHelper._load_skills(data["skills"]),
      effects = []
    )
    
    return entity
  
  @staticmethod
  def _load_player_battle_data():
    with open("./assets/player.meta.json", "r") as f:
      data = json.load(f)
      
    with open("./assets/skills.json", "r") as f:
      player_skill_meta = json.load(f)
      
    entity = BattleEntity(
      name = "Player",
      max_hp = 100,
      current_hp = 100,
      shield = 0,
      physical_buff = 0,
      magical_buff = 0,
      frozen = False,
      weakness = 0, 
      skills = BattleHelper._load_skills(
        {k: v for k, v in player_skill_meta.items() if k in data["skills"]}
      ),
      effects = []
    )
    
    return entity

  def check_next_round_frozen(self, entity: BattleEntity) -> bool:
    return len(list(filter(lambda e: e.type == "frozen", entity.effects))) > 0

  def check_battle_result(self) -> bool:
    if self.player.current_hp <= 0:
      return False
    if self.enemy.current_hp <= 0:
      return True
    return None

  def _refresh_effects(self, entity: BattleEntity):
    entity.frozen = False
    entity.physical_buff = 0
    entity.magical_buff = 0
    entity.weakness = 0
    
    for effect in entity.effects:
      match effect.type:
        case "burning":
          self._do_damage(entity, entity.current_hp * 0.05)
        case "poisoned":
          self._do_damage(entity, entity.max_hp * 0.1)
        case "frozen":
          entity.frozen = True
        case "weakness":
          entity.weakness = 2
        case "healing":
          entity.current_hp += effect.value
        case "magic_boost":
          entity.magical_buff += effect.value
        case "physical_boost":
          entity.physical_buff += effect.value

  def _do_damage(self, entity: BattleEntity, damage: int):
    remain_shield = round(entity.shield - damage)
    
    if remain_shield <= 0:
      entity.current_hp += remain_shield
      entity.shield = 0
    else:
      entity.shield = remain_shield
    
    entity.current_hp = round(
      max(
        entity.current_hp,
        0
      )
    )

  def _use_skills(self, entity: BattleEntity, opponent: BattleEntity, skill_ids: List[str]):
    if not entity.frozen:
      for skill_id in skill_ids:
        skill = entity.skills[skill_id]
        
        if skill.current_cooldown != 0:
          continue
        
        total_damage = max(
          (
            (skill.physical_damage + entity.physical_buff)
            + (skill.magical_damage + entity.magical_buff)
            - entity.weakness
          ),
          0
        )
        
        self._do_damage(opponent, total_damage)
        
        entity.current_hp = round(
          min(
            entity.max_hp,
            entity.current_hp + skill.heal
          ),
        )
        entity.shield += skill.shield
        
        if skill.purify:
          entity.effects = list(filter(lambda e: not e.negative, entity.effects))
        
        for effect in skill.effect:
          if random.random() <= effect.chance:
            battle_effect = BattleEffect(
              effect.type,
              effect.name,
              effect.negative,
              True,
              effect.value,
              effect.duration
            )
            if effect.target == "self":
              entity.effects.append(battle_effect)
            elif effect.target == "opponent":
              opponent.effects.append(battle_effect)
        
        skill.hanging = True
        skill.current_cooldown = skill.cooldown

  def _tick_effects(self, entity: BattleEntity):
    for effect in entity.effects:
      if effect.hanging:
        effect.hanging = False
      else:
        effect.duration -= 1
    
    entity.effects = list(filter(lambda e: e.duration > 0, entity.effects))

  def _tick_skills(self, entity: BattleEntity):
    for _, skill in entity.skills.items():
      if skill.hanging:
        skill.hanging = False
      elif skill.current_cooldown != 0:
        skill.current_cooldown -= 1

  def execute_player_turn(self, skill_ids: List[str]) -> bool | None:
    self._refresh_effects(self.player)

    self._use_skills(self.player, self.enemy, skill_ids)
    
    self._tick_effects(self.player)
    self._tick_skills(self.player)
    
    print(self.enemy)
    print()
    print(self.player)
    print()
    print()
    print()
    
    return self.check_battle_result()

  def execute_enemy_turn(self) -> bool | None:
    self._refresh_effects(self.enemy)
    
    skill_ids = [k for k, v in self.enemy.skills.items() if v.current_cooldown == 0]

    self._use_skills(self.enemy, self.player, skill_ids)
    
    self._tick_effects(self.enemy)
    self._tick_skills(self.enemy)
    
    print(self.enemy)
    print()
    print(self.player)
    print()
    print()
    print()
    
    return self.check_battle_result()
