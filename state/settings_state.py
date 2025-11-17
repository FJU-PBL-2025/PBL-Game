import pygame

from state.state import State


class SettingsState(State):
  def __init__(self, game):
    super().__init__(game)
    self.menu_options = {
      "Language": ["English", "中文"],
      "Volume": list(range(0, 101, 10)),
      "X Sensitivity": [i / 10.0 for i in range(1, 21)], # 0.1 to 2.0
      "Y Sensitivity": [i / 10.0 for i in range(1, 21)], # 0.1 to 2.0
    }
    self.option_keys = list(self.menu_options.keys())
    self.option_keys.append("Back") # Add a back option
    self.index = 0 # To navigate between different settings like "Language", "Volume", etc.

    # Initialize setting indices if they don't exist
    if 'setting_indices' not in self.game.settings:
        self.game.settings['setting_indices'] = {
            "Language": 0,
            "Volume": 5, # Default to 50
            "X Sensitivity": 9, # Default to 1.0
            "Y Sensitivity": 9, # Default to 1.0
        }

  def update(self, delta_time: float, actions: dict):
    # Navigate up and down the menu
    if actions.get(pygame.K_w) or actions.get(pygame.K_UP):
      self.index = (self.index - 1) % len(self.option_keys)
    elif actions.get(pygame.K_s) or actions.get(pygame.K_DOWN):
      self.index = (self.index + 1) % len(self.option_keys)

    current_option_key = self.option_keys[self.index]

    # Handle "Back" option or ESC key
    if (current_option_key == "Back" and actions.get(pygame.K_RETURN)) or actions.get(pygame.K_ESCAPE):
      self.exit_state() # Go back to the previous state (Title Screen)
    
    # Change setting values with left/right keys
    elif current_option_key in self.menu_options:
      option_values = self.menu_options[current_option_key]
      current_value_index = self.game.settings['setting_indices'][current_option_key]

      if actions.get(pygame.K_a) or actions.get(pygame.K_LEFT):
        new_index = (current_value_index - 1) % len(option_values)
        self.game.settings['setting_indices'][current_option_key] = new_index
        # Update the actual setting value in the game object
        self.game.settings[current_option_key.lower().replace(' ', '_')] = option_values[new_index]

      elif actions.get(pygame.K_d) or actions.get(pygame.K_RIGHT):
        new_index = (current_value_index + 1) % len(option_values)
        self.game.settings['setting_indices'][current_option_key] = new_index
        # Update the actual setting value in the game object
        self.game.settings[current_option_key.lower().replace(' ', '_')] = option_values[new_index]

    self.game.reset_keys()

  def render(self, surface: pygame.Surface):
    surface.fill((255, 255, 255))
    self.game.draw_text(
      surface,
      "Settings",
      (0, 0, 0),
      self.game.GAME_W / 2,
      self.game.GAME_H / 4
    )

    y_offset = 0
    for i, key in enumerate(self.option_keys):
      # Display the setting name
      text = f"> {key}" if self.index == i else key
      
      # Display the current value for the setting
      if key in self.menu_options:
        current_value_index = self.game.settings['setting_indices'][key]
        value = self.menu_options[key][current_value_index]
        
        # Format volume as a percentage
        value_text = f"< {value}% >" if key == "Volume" else f"< {value} >"
        
        # Render setting name (left aligned)
        self.game.draw_text(
            surface, text, (0, 0, 0), self.game.GAME_W / 3, self.game.GAME_H / 2 + y_offset, align="left"
        )
        # Render setting value (right aligned)
        self.game.draw_text(
            surface, value_text, (0, 0, 0), self.game.GAME_W * 2 / 3, self.game.GAME_H / 2 + y_offset, align="right"
        )
      else: # For "Back" button (centered)
        self.game.draw_text(
            surface, text, (0, 0, 0), self.game.GAME_W / 2, self.game.GAME_H / 2 + y_offset
        )
      y_offset += 40
