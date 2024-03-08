from typing import List, Tuple, Set
from math import pi
from weakref import WeakSet

from pyglet.math import Vec2
from arcade import draw_line, draw_polygon_outline

from engine.light.light_beam import LightBeam, LightEdge


class LightInteractorManager:

    def __init__(self):
        self._active_interactors: Set["LightInteractor"] = set()
        self._inactive_interactors: Set["LightInteractor"] = set()

    def calculate_intersecting_edges(self, beam: LightBeam) -> Tuple[Tuple[Vec2, Vec2, Vec2, "LightInteractor"]]:
        intersecting_edges: List[Tuple[Vec2, Vec2, Vec2, "LightInteractor"]] = []

        for interactor in tuple(self._active_interactors):
            for i in range(len(interactor.bounds)):
                start, end, normal = interactor.get_edge_adjusted(i)
                is_intersecting = beam.is_edge_in_beam(start, end)
                if is_intersecting:
                    intersecting_edges.append((start, end, Vec2(normal.y, -normal.x), interactor))

        return tuple(intersecting_edges)

    def add_interactor(self, interactor: "LightInteractor", is_active: bool = True):
        if interactor in self._active_interactors or interactor in self._inactive_interactors:
            return

        if is_active:
            self._active_interactors.add(interactor)
        else:
            self._inactive_interactors.add(interactor)

    def activate_interactor(self, interactor: "LightInteractor"):
        if interactor not in self._inactive_interactors:
            return

        raise NotImplementedError()

    def deactivate_interactor(self, interactor: "LightInteractor"):
        if interactor not in self._active_interactors:
            return

        raise NotImplementedError()

    def debug_draw(self):
        for interactor in tuple(self._active_interactors):
            interactor.debug_draw()


class LightInteractor:

    def __init__(self,
                 position: Vec2,
                 direction: Vec2,
                 bounding_points: Tuple[Vec2, ...],
                 parent: LightInteractorManager,
                 components: Tuple[bool, bool, bool] = (True, True, True)
                 ):
        self._parent: LightInteractorManager = parent

        self._position: Vec2 = position
        self._direction: Vec2 = direction
        # The bounds should be stored clockwise and be relative to the center position
        self._bounds: Tuple[Vec2, ...] = bounding_points
        # Relying on the bounds being clockwise calculate the normals to each bound face.
        self._normals: Tuple[Vec2, ...] = tuple(
            (self._bounds[(i + 1) % len(self._bounds)] - self._bounds[i]).rotate(pi / 2).normalize()
            for i in range(len(self._bounds))
        )

        self._components = components

        # Weakly reference the beams coming and going from the light interactor.
        # When the interactor changes the outgoing beams can all be killed,
        # and the incoming beams can be told to propagate.
        # if a beam gets killed another way (which shouldn't happen) then it
        # softly disappears from here.
        self._incoming_beams: WeakSet = WeakSet()
        self._outgoing_beams: WeakSet = WeakSet()

    def remove_incoming_beam(self, beam: LightBeam):
        if beam not in self._incoming_beams:
            return

        self._incoming_beams.remove(beam)

    def remove_out_going_beam(self, beam: LightBeam):
        if beam not in self._outgoing_beams:
            return

        self._outgoing_beams.remove(beam)

    @property
    def position(self):
        return self._position

    def set_position(self, new_position: Vec2):
        pass

    @property
    def direction(self):
        return self._direction

    def set_direction(self, new_direction: Vec2):
        self._direction = new_direction

    @property
    def bounds(self):
        return self._bounds

    @property
    def bounds_adjusted(self):
        return tuple(self.position + bound.rotate(self.direction.heading) for bound in self._bounds)

    @property
    def normals(self):
        return self._normals

    @property
    def normals_adjusted(self):
        return (normal.rotate(self._direction.heading) for normal in self._normals)

    @property
    def components(self):
        return self._components

    def set_components(self, new_components: Tuple[bool, bool, bool]):
        if new_components == self._components:
            return

        self._components = new_components

    def get_edge(self, index: int):
        return self._bounds[index], self._bounds[(index + 1) % len(self._bounds)], self._normals[index]

    def get_edge_adjusted(self, index: int) -> Tuple[Vec2, Vec2, Vec2]:
        start = self.position + self._bounds[index].rotate(self.direction.heading)
        end = self.position + self._bounds[(index + 1) % len(self._bounds)].rotate(self.direction.heading)
        normal = self._normals[index].rotate(self.direction.heading)

        return start, end, normal

    def calculate_interaction(self, beam: LightBeam, edge: Tuple[Vec2, Vec2, Vec2, "LightInteractor"]) -> Tuple[LightBeam, ...]:
        """
        Calculate the subsequent beams of light caused by the source beam interacting with
        the interactor.

        If the returned tuple is not empty the interactor should weakly add the beam as an interacting beam.
        If any important property of the interactor is changed (origin, direction, component)
        then the children beams can be calculated.
        """
        raise NotImplementedError()

    def debug_draw(self):
        points = tuple(self.bounds_adjusted)

        colour = (255 * self._components[0], 255 * self._components[1], 255 * self._components[2], 255)

        draw_line(self._position.x, self._position.y,
                  self._position.x + self._direction.x * 15,
                  self._position.y + self._direction.y * 15,
                  colour, 1)

        draw_polygon_outline(points, colour, 1)


class LightFilter(LightInteractor):

    def __init__(self,
                 position: Vec2,
                 direction: Vec2,
                 width: float,
                 height: float,
                 parent: LightInteractorManager,
                 components: Tuple[bool, bool, bool] = (True, True, True)
                 ):
        bounds = (
            Vec2(-width/2, -height/2),
            Vec2(-width/2, height/2),
            Vec2(width/2, height/2),
            Vec2(width/2, -height/2)
        )
        super().__init__(position, direction, bounds, parent, components)

    def calculate_interaction(self, beam: LightBeam, edge: Tuple[Vec2, Vec2, Vec2, "LightInteractor"]) -> Tuple[LightBeam, ...]:
        component_mix: Tuple[bool, bool, bool] = tuple(a and b for a, b in zip(beam.components, self._components))

        if not any(component_mix):
            return ()

        left_strength = beam.left.strength - beam.left.length
        right_strength = beam.right.strength - beam.right.length

        left_pos = beam.left.source + beam.left.direction * beam.left.length
        right_pos = beam.right.source + beam.right.direction * beam.right.length

        left_edge = LightEdge(
            beam.left.direction,
            left_pos,
            left_strength,
            left_strength,
            beam.left.bound
        )

        right_edge = LightEdge(
            beam.right.direction,
            right_pos,
            right_strength,
            right_strength,
            beam.right.bound
        )

        origin = (left_pos + right_pos) / 2
        direction = beam.direction

        next_beam = LightBeam(
            beam.image,
            component_mix,
            self._parent,
            left_edge,
            right_edge,
            origin,
            direction,
            None
        )

        beam.add_child(next_beam)

        return next_beam,


class LightConcave(LightInteractor):
    pass


class LightConvex(LightInteractor):
    pass


class LightPrism(LightInteractor):
    pass