from typing import Tuple

from pyglet.math import Vec2

from engine.scene import SceneObject
from engine.player.player_controller import PlayerController
from engine.player.player_renderer import PlayerRenderer


class PlayerObject(SceneObject):

    def __init__(self, origin: Vec2, components: Tuple[bool, bool, bool]):
        super().__init__(origin, Vec2(1.0, 0.0), components)

    def decompose(self) -> Tuple["SceneObject", ...]:
        raise NotImplementedError()

    def compose(self, sub_objects: Tuple["SceneObject", ...]) -> "SceneObject":
        raise NotImplementedError()


class Player:

    def __init__(self):
        self._active_player_scene_object: PlayerObject | None = None
        self._player_scene_objects: Tuple[PlayerObject, ...] = ()
