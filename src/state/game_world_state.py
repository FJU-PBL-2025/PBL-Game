from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
  from src.game import Game
from src.state.state import State
from src.tile_render import TiledMapRenderer


class GameWorldState(State):
  def __init__(self, game: "Game"):
    State.__init__(self, game)
    
    self.map_renderer: TiledMapRenderer = TiledMapRenderer("test-map")

  def update(self, delta_time: float):
    i_m = self.game.input_manager
    
    self.game.player.update(delta_time)
    hit_tiles = self.game.player.handle_movement(
      delta_time,
      i_m,
      self.map_renderer.tiles,
      self.map_renderer.metadata
    )
    
    hit_exit_tiles = list(
      filter(
        lambda t: self.map_renderer.metadata.exits.get((t.x, t.y)) is not None,
        hit_tiles
      )
    )
    
    if len(hit_exit_tiles) == 0:
      self.game.player.in_exit = False
    elif not self.game.player.in_exit:
      exit_tile = hit_exit_tiles[0]
      hit_exit = self.map_renderer.metadata.exits.get(
        (exit_tile.x, exit_tile.y)
      )
      
      self.map_renderer.change_map(hit_exit.dist)
      self.game.player.set_position(
        hit_exit.dist_x * self.map_renderer.map.tilewidth + self.map_renderer.map.tilewidth / 2,
        hit_exit.dist_y * self.map_renderer.map.tileheight + self.map_renderer.map.tileheight / 2
      )
      self.game.player.in_exit = True
      self.game.input_manager.pause(0.05)
    
    if i_m.is_key_down_once(pygame.K_ESCAPE):
      self.exit_state()

  def render(self, surface: pygame.Surface):
    surface.fill((255, 255, 255))
    self.map_renderer.render(surface)
    self.game.player.render(surface)
