import pygame

from state.game_world_state import GameWorldState
from state.state import State


class CharacterSelectionState(State):
  def __init__(self, game):
    super().__init__(game)
    self.options = ["Knight", "Magician"]
    self.index = 0

  def update(self, delta_time: float, actions: dict):
    # 處理選項間的上下移動
    if actions.get(pygame.K_w) or actions.get(pygame.K_UP):
      self.index = (self.index - 1) % len(self.options)
    elif actions.get(pygame.K_s) or actions.get(pygame.K_DOWN):
      self.index = (self.index + 1) % len(self.options)

    # 處理確認選擇或返回
    if actions.get(pygame.K_RETURN):
      selected_character = self.options[self.index].lower()
      # 在 game 物件中設定玩家的角色類型
      # 假設您的 Player class 可以根據這個值來改變外觀和行為
      self.game.player.set_character(selected_character)
      
      # 進入遊戲世界
      new_state = GameWorldState(self.game)
      new_state.enter_state()

    elif actions.get(pygame.K_ESCAPE):
      self.exit_state() # 返回主選單

    self.game.reset_keys()

  def render(self, surface: pygame.Surface):
    surface.fill((255, 255, 255)) # 白色背景
    self.game.draw_text(
      surface,
      "Choose your character",
      (0, 0, 0),
      self.game.GAME_W / 2,
      self.game.GAME_H / 4
    )

    # 顯示選項
    for i, option in enumerate(self.options):
      text = f"> {option}" if self.index == i else option
      self.game.draw_text(
        surface,
        text,
        (0, 0, 0),
        self.game.GAME_W / 2,
        self.game.GAME_H / 2 + i * 40
      )
