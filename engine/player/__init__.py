from typing import Tuple

from pyglet.math import Vec2

from engine.scene.scene_object_types import SimpleObject
from engine.player.player_controller import PlayerController
from engine.player.player_renderer import PlayerRenderer


class Player:

    def __init__(self):
        self._active_player_scene_object: SimpleObject | None = None
        self._player_scene_objects: Tuple[SimpleObject, ...] = ()
        self._player_renderers: Tuple[PlayerRenderer, ...] = ()

    def set_player_renderers(self, renderers: Tuple[PlayerRenderer, ...]):
        for renderer in self._player_renderers:
            if renderer not in renderers:
                renderer.kill()

        self._player_renderers = renderers

