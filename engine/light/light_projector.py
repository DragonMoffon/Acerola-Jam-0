from typing import Tuple, TYPE_CHECKING
from math import pi

from pyglet.math import Vec2
from arcade import Texture, draw_polygon_outline, draw_line

from engine.light.light_beam import LightBeam, LightEdge

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

        self._children_beams: Tuple[LightBeam, ...] = ()

        self._parent: "LightScene" | None = None
        self._is_on: bool = False

    def update_beams(self):
        for child_beam in self._children_beams:
            child_beam.propagate_kill()

        initial_beam = self.generate_initial_beam()
        self._children_beams = initial_beam.propagate_beam(self._parent.interactor_manager)

    def set_parent(self, parent: "LightScene"):
        self._parent = parent

        if not self._is_on:
            return

        self.update_beams()

    def turn_on(self):
        self._is_on = True

        if self._parent is None:
            return

        self.update_beams()

    def turn_off(self):
        self._is_on = False

        for child_beam in self._children_beams:
            child_beam.propagate_kill()
        self._children_beams = ()

    @property
    def children_beams(self) -> Tuple[LightBeam, ...]:
        return self._children_beams

    @property
    def direction(self):
        return self._direction

    def set_direction(self, new_direction: Vec2):
        self._direction = new_direction

        if not self._is_on or self._parent is None:
            return

        self.update_beams()

    @property
    def origin(self):
        return self._origin

    def set_origin(self, new_origin: Vec2):
        self._origin = new_origin

        if not self._is_on or self._parent is None:
            return

        self.update_beams()

    def debug_draw(self):
        r = Vec2(-self._direction.y, self._direction.x)
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

        for child_beam in self._children_beams:
            child_beam.debug_draw()

    def generate_initial_beam(self):
        if self._parent is None:
            raise ValueError()

        h_width = LightProjector.output_width // 2
        h_img_height = self._image.height // 2
        rotated_dir = self._direction.rotate(pi / 2).normalize()

        image_location = self._origin + self._direction * self._strength
        image_left_location = image_location + rotated_dir * h_img_height
        image_right_location = image_location - rotated_dir * h_img_height

        proj_left_location = self._origin + rotated_dir * h_width
        proj_right_location = self._origin - rotated_dir * h_width

        left_dir = (image_left_location - proj_left_location).normalize()
        left_strength = (image_left_location - proj_left_location).mag

        right_dir = (image_right_location - proj_right_location).normalize()
        right_strength = (image_right_location - proj_right_location).mag

        left_edge = LightEdge(
            proj_left_location,
            image_left_location,
            left_dir,
            left_strength,
            left_strength,
            1.0
        )
        right_edge = LightEdge(
            proj_right_location,
            image_right_location,
            right_dir,
            right_strength,
            right_strength,
            0.0
        )

        return LightBeam(
            self._image,
            self._components,
            self._parent.interactor_manager,
            left_edge,
            right_edge,
            self._origin,
            self._direction
        )