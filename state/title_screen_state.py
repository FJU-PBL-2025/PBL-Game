from state.state import State

class TitleScreenState(State):
  def __init__(self, game):
    State.__init__(self, game)

  def update(self, delta_time, actions):
    if actions["return"]:
      new_state = ... # S/L State or Game World State
      new_state.enter_state()
    self.game.reset_keys()

  def render(self, display):
    display.fill((255,255,255))
    self.game.draw_text(
      display,
      "PBL Game",
      (0, 0, 0),
      self.game.GAME_W / 2,
      self.game.GAME_H / 2
    )
