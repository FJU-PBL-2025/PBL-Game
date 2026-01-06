import pygame


class AudioManager():
  def __init__(self):
    pygame.mixer.init()

  def play_background_music(self, name: str):
    pygame.mixer.music.load(f"./assets/audio/{name}.mp3")
    pygame.mixer.music.play(-1)
  
  def play_sound(self, name: str, channel: int = 0, override: bool = False):
    sound = pygame.mixer.Sound(f"./assets/audio/{name}.mp3")
    
    if pygame.mixer.Channel(channel).get_busy():
      if override:
        pygame.mixer.Channel(channel).play(sound)
      else:
        return
    else:
      pygame.mixer.Channel(channel).play(sound)

  def stop_sound(self, channel: int = 0):
    pygame.mixer.Channel(channel).stop()

  def stop_background_music(self):
    pygame.mixer.music.stop()
