from typing import Tuple, Dict, TYPE_CHECKING
from math import pi

from pyglet.math import Vec2
from arcade import Texture, draw_point, draw_polygon_outline

if TYPE_CHECKING:
    from engine.light.light_interactors import LightInteractorManager, LightInteractor


def _get_intersection(o1: Vec2, d1: Vec2, o2: Vec2, d2: Vec2) -> Vec2 | None:
    # If the two directions are parallel then just return None as they won't intersect
    if abs(d1.dot(d2)) == 1.0:
        return None

    # If the second vector has an x of 0 then we can simplify the entire equation down (t2 no longer matters)
    if d2.x == 0.0:
        t1 = (o2.x - o1.x) / d1.x
    else:
        ta = (o1.y - o2.y) - (o1.x - o2.x) * (d2.y / d2.x)
        tb = d1.x * (d2.y / d2.x) - d1.y
        t1 = ta / tb

    return o1 + d1 * t1


def _get_segment_intersection(s1: Vec2, e1: Vec2, s2: Vec2, e2: Vec2, d1: Vec2 | None = None, d2: Vec2 | None = None):
    d1 = d1 or (e1 - s1).normalize()
    d2 = d2 or (e2 - s2).normalize()

    if abs(d1.dot(d2)) == 1.0:
        return None

    if d2.x == 0.0:
        t1 = (s2.x - s1.x) / d1.x
        t2 = ((s1.y - s2.y) + d1.y * t1) / d2.y
    else:
        ta = (s1.y - s2.y) - (s1.x - s2.x) * (d2.y / d2.x)
        tb = d1.x * (d2.y / d2.x) - d1.y
        t1 = ta / tb
        t2 = ((s1.x - s2.x) + t1 * d1.x) / d2.x

    # t1 and t2 must be greater than 0.0 for the two segments to intersect
    if (t1 < 0.0) or (t2 < 0.0):
        return None

    v1 = e1 - s1
    v2 = e2 - s2

    # if t1 and t2 are greater than start to end of either segment then they aren't intersecting.
    if (t1**2 > v1.dot(v1)) or (t2**2 > v2.dot(v2)):
        return None

    return s1 + d1 * t1


class LightEdge:

    def __init__(self, direction: Vec2, source: Vec2, strength: float, length: float, bound: float):
        # The direction of the edge, used to find intersections
        self.direction: Vec2 = direction
        # The normal of the edge direction. Is always rotated anti-clockwise
        self.normal: Vec2 = direction.rotate(pi/2).normalize()
        # The position the light beam starts from
        self.source: Vec2 = source
        # The strength of the beam edge. How many units (pixels) the beam can travel
        self.strength: float = strength
        # The actual length of the beam edge. when the beam interacts with anything the beam is cut short
        self.length: float = length
        # The percentage position along the image of this beam (0.0 - 1.0)
        self.bound: float = bound


class LightBeam:

    def __init__(self,
                 image: Texture,
                 components: Tuple[bool, bool, bool],
                 left: LightEdge,
                 right: LightEdge,
                 origin: Vec2 | None = None,
                 direction: Vec2 | None = None,
                 intersection: Vec2 | None = None
                 ):
        # The texture which will be projected once the beam reaches the end
        self._image: Texture = image
        # The RGB components of the light beam. At least one must be present.
        self._components: Tuple[bool, bool, bool] = components

        # The left and right edges of the beam for interaction detection,
        # and calculating the final sprite.
        self._left_edge: LightEdge = left
        self._right_edge: LightEdge = right

        # The origin is the center of the light Beam
        self._origin: Vec2 = origin or (self._left_edge.source + self._right_edge.source) / 2
        # The direction is the "normal" of the face of the beam. It does not respect the angles of the beam edges.
        self._direction: Vec2 = direction or (self._left_edge.source - self._right_edge.source).rotate(-pi / 2).normalize()
        # The intersection of the two edges. If the two edges are parallel this is None.
        self._intersection: Vec2 | None = intersection

        # When a light beam hits an intractable object it splits into multiple child beams
        # Starting from a projector it is possible get to all sub beams.
        # Unused.
        self._children: Tuple[LightBeam, ...] = ()

    @property
    def origin(self):
        return self._origin

    @property
    def direction(self):
        return self._direction

    @property
    def left(self):
        return self._left_edge

    @property
    def right(self):
        return self._right_edge

    @property
    def colour(self):
        rgb = tuple(255 * c for c in self._components)
        return (rgb[0], rgb[1], rgb[2], 255)

    def propagate_beam(self):
        pass

    def propagate_kill(self):
        pass

    def is_point_in_beam(self, point: Vec2):
        # If the point is "behind" the beam ignore it
        to_point = (point - self._origin)
        if to_point.dot(self._direction) <= 0.0:
            return False

        left_to_point = (point - self._left_edge.source)
        in_front_of_left = self._left_edge.normal.dot(left_to_point) < 0.0

        right_to_point = (point - self._right_edge.source)
        in_front_of_right = self._right_edge.normal.dot(right_to_point) > 0.0

        # If the point is not infront/behind both lines then it isn't within the beam
        if in_front_of_left != in_front_of_right:
            return False

        end_left = self._left_edge.source + self._left_edge.direction * self._left_edge.length
        end_right = self._right_edge.source + self._right_edge.direction * self._left_edge.length
        end_pos = (end_left + end_right) / 2
        is_end_flipped = self._left_edge.normal.dot(end_pos) > 0.0
        end_dir = (end_left - end_right).rotate(pi/2 * (1 - 2*is_end_flipped)).normalize()
        end_to_point = (point - end_pos)

        # If the point is past the end of the beam ignore it.
        if end_dir.dot(end_to_point) <= 0.0:
            return False

        return True

    def is_edge_in_beam(self, start: Vec2, end: Vec2):
        to_start = (start - self._origin)
        to_end = (end - self._origin)

        # If both points are "Behind" the beam then ignore it
        if to_start.dot(self._direction) <= 0.0 and to_end.dot(self._direction) <= 0.0:
            return False

        right_to_start = start - self._right_edge.source
        right_to_end = end - self._right_edge.source
        left_to_start = start - self._left_edge.source
        left_to_end = end - self._left_edge.source

        # If the start or end are within the beam then the edge must intersect
        if (self._right_edge.normal.dot(right_to_start) > 0.0) == (self._left_edge.normal.dot(left_to_start) < 0.0):
            return True

        if (self._right_edge.normal.dot(right_to_end) > 0.0) == (self._left_edge.normal.dot(left_to_end) < 0.0):
            return True

        left_to_beam_end = self._left_edge.source + self._left_edge.direction * self._left_edge.length
        right_to_beam_end = self._right_edge.source + self._right_edge.direction * self._right_edge.length

        edge_dir = (end - start).normalize()

        # If the line intersects the left edge then it is inside the beam
        if _get_segment_intersection(
                start, end,
                self._left_edge.source, left_to_beam_end,
                edge_dir, self._left_edge.direction) is not None:
            return True

        # If the line intersects the right edge then it is inside the beam.
        if _get_segment_intersection(
                start, end,
                self._right_edge.source, right_to_beam_end,
                edge_dir, self._right_edge.direction) is not None:
            return True

        # If the line intersects the end of the beam then it is inside the beam.
        if _get_segment_intersection(
                start, end,
                right_to_beam_end, left_to_beam_end,
                edge_dir) is not None:
            return True

        # If none of the above cases have passed then the line does not intersect the beam.
        return False

    def debug_draw(self):
        colour = self.colour
        start_left = self._left_edge.source
        start_right = self._right_edge.source
        end_left = self._left_edge.source + self._left_edge.direction * self._left_edge.length
        end_right = self._right_edge.source + self._right_edge.direction * self._right_edge.length

        draw_polygon_outline((start_left, end_left, end_right, start_right), colour, 1)

        draw_point(self._origin.x + self._direction.x * 20, self._origin.y + self._direction.y * 20,
                   (0, 255, 255, 255), 5)

        draw_point(
            self._right_edge.source.x + self._right_edge.normal.x * 10,
            self._right_edge.source.y + self._right_edge.normal.y * 10,
            (255, 0, 0, 255),
            3
        )
        draw_point(
            self._left_edge.source.x + self._left_edge.normal.x * 10,
            self._left_edge.source.y + self._left_edge.normal.y * 10,
            (0, 255, 0, 255),
            3
        )


class LightBeamParent:

    def __init__(self,
                 interactor_manager: "LightInteractorManager",
                 image: Texture,
                 components: Tuple[bool, bool, bool],
                 origin: Vec2,
                 direction: Vec2,
                 width: float,
                 strength: float):
        self._interaction_manager: "LightInteractorManager" = interactor_manager
        self._image: Texture = image
        self._components: Tuple[bool, bool, bool] = components

        self._origin: Vec2 = origin
        self._direction: Vec2 = direction
        self._normal: Vec2 = direction.rotate(pi / 2.0).normalize()
        self._width: float = width
        self._strength: float = strength

        self._children: Tuple[LightBeam] = ()

    def debug_draw(self):
        for child in self._children:
            child.debug_draw()

    def set_direction(self, new_direction: Vec2):
        if new_direction == self._direction:
            return

        self._direction = new_direction
        self.propagate_beam()

    def set_origin(self, new_origin: Vec2):
        if new_origin == self._origin:
            return

        self._origin = new_origin
        self.propagate_beam()

    def set_image(self, new_image: Texture):
        if new_image == self._image:
            return

        self._image = new_image
        self.propagate_beam()

    def set_width(self, new_width: float):
        if new_width == self._width:
            return

        self._width = new_width
        self.propagate_beam()

    def set_strength(self, new_strength: float):
        if new_strength == self._strength:
            return

        self._strength = new_strength
        self.propagate_beam()

    def propagate_beam(self):
        self.propagate_kill()

        _initial_beam = self._generate_initial_beam()

        _intersecting_edges = self._interaction_manager.calculate_intersecting_edges(_initial_beam)

        if not _intersecting_edges:
            self._children = (_initial_beam,)
            return

        left_edge = (
            _initial_beam.left.source,
            _initial_beam.left.source + _initial_beam.left.direction * _initial_beam.left.length,
            _initial_beam.left.direction,
            None
        )

        right_edge = (
            _initial_beam.right.source,
            _initial_beam.right.source + _initial_beam.right.direction * _initial_beam.right.length,
            _initial_beam.right.direction,
            None
        )

        end_edge = (
            right_edge[1], left_edge[1], (left_edge[1] - right_edge[1]).rotate(pi / 2).normalize(), None
        )

    def propagate_kill(self):
        # Safely remove all child beams
        # recursively go into child beams and get them to
        # disconnect from any interactors
        for child in self._children:
            child.propagate_kill()

        self._children = ()

    def _generate_initial_beam(self) -> LightBeam:
        h_width = self._width//2
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

        left_edge = LightEdge(left_dir, proj_left_location, left_strength, left_strength, 1.0)
        right_edge = LightEdge(right_dir, proj_right_location, right_strength, right_strength, 0.0)

        intersection = _get_intersection(proj_left_location, left_dir, proj_right_location, right_dir)

        return LightBeam(
            self._image,
            self._components,
            left_edge,
            right_edge,
            self._origin,
            self._direction,
            intersection
        )


