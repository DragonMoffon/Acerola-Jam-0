from typing import Tuple, TYPE_CHECKING
from math import pi

from pyglet.math import Vec2
from arcade import Texture, draw_polygon_outline, draw_line

from engine.light.light_beam import LightBeamParent

if TYPE_CHECKING:
    from engine.light.light_scene import LightScene


class LightProjector:
    output_width: int = 14

    def __init__(self, image: Texture, components: Tuple[bool, bool, bool], strength: float,
                 origin: Vec2, direction: Vec2):
        self._image: Texture = image
        self._components: Tuple[bool, bool, bool] = components
        self._strength: float = strength

        self._origin: Vec2 = origin
        self._direction: Vec2 = direction

        self._light_beam: LightBeamParent | None = None

        self._parent: "LightScene" | None = None
        self._is_on: bool = False

    def set_parent(self, parent: "LightScene"):
        self._parent = parent

        if self._light_beam is None:
            self._light_beam = LightBeamParent(
                parent.interactor_manager,
                self._image,
                self._components,
                self._origin,
                self._direction,
                LightProjector.output_width,
                self._strength
            )

    def turn_on(self):
        self._is_on = True

        if self._parent is None:
            return

        if self._light_beam is None:
            self._light_beam = LightBeamParent(
                self._parent.interactor_manager,
                self._image,
                self._origin,
                self._direction,
                LightProjector.output_width,
                self._strength
            )

        self._light_beam.propagate_beam()

    def turn_off(self):
        self._is_on = False

        if self._light_beam is not None:
            self._light_beam.propagate_kill()

    @property
    def light_beam(self):
        return self._light_beam

    @property
    def direction(self):
        return self._direction

    def set_direction(self, new_direction: Vec2):
        self._direction = new_direction

        self.light_beam.set_direction(new_direction)

    @property
    def origin(self):
        return self._origin

    def set_origin(self, new_origin: Vec2):
        self._origin = new_origin

        self._light_beam.set_origin(new_origin)

    def debug_draw(self):
        r = self._direction.rotate(pi / 2)
        p = (
            self._origin + r * (LightProjector.output_width / 2),
            self._origin - r * (LightProjector.output_width / 2),
            self._origin - r * (LightProjector.output_width / 2) - self._direction * 32,
            self._origin + r * (LightProjector.output_width / 2) - self._direction * 32
        )

        draw_polygon_outline(p, (255, 255, 255, 255), 1.0)

        draw_line(
            self._origin.x, self._origin.y,
            self._origin.x + self._direction.x * 15,
            self._origin.y + self._direction.y * 15,
            (255, 255, 255, 255),
            1
        )

        self._light_beam.debug_draw()