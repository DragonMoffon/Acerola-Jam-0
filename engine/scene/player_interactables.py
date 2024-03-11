from typing import Tuple
from weakref import WeakMethod

from pyglet.math import Vec2

from engine.scene.scene_object_types import PlayerInteractor, SceneObject


class PushBlock(PlayerInteractor):

    def __init__(self, origin: Vec2, direction: Vec2,
                 is_vertical: bool, is_horizontal: bool, size: int,
                 components: Tuple[bool, bool, bool]):
        super().__init__(origin, direction, components)


class Switch(PlayerInteractor):
    pass


class Button(PlayerInteractor):
    pass


class Slider(PlayerInteractor):
    pass
