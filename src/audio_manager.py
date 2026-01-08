import pygame


class AudioManager():
  @staticmethod
  def init():
    pygame.mixer.init()

  @staticmethod
  def play_background_music(name: str):
    pygame.mixer.music.load(f"./assets/audio/{name}.mp3")
    pygame.mixer.music.play(-1)
  
  @staticmethod
  def play_sound(name: str, channel: int = 0, override: bool = False):
    sound = pygame.mixer.Sound(f"./assets/audio/{name}.mp3")
    
    if pygame.mixer.Channel(channel).get_busy():
      if override:
        pygame.mixer.Channel(channel).play(sound)
      else:
        return
    else:
      pygame.mixer.Channel(channel).play(sound)

  @staticmethod
  def stop_sound(channel: int = 0):
    pygame.mixer.Channel(channel).stop()

  @staticmethod
  def stop_background_music():
    pygame.mixer.music.stop()
