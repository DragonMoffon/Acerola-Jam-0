from typing import List, Tuple, Set
from math import pi
from weakref import WeakSet

from pyglet.math import Vec2
from arcade import draw_line, draw_polygon_outline

from engine.light.light_beam import LightBeam


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
                    intersecting_edges.append((start, end, normal.rotate(-pi / 2).normalize(), interactor))

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
                 components: Tuple[bool, bool, bool] = (True, True, True)
                 ):
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
        normals = tuple(self.normals_adjusted)

        draw_line(self._position.x, self._position.y,
                  self._position.x + self._direction.x * 15,
                  self._position.y + self._direction.y * 15,
                  (255, 255, 255, 255), 1)

        draw_polygon_outline(points, (255, 255, 255, 255), 1)
        for i in range(len(normals)):
            p = points[i]
            n = normals[i]

            draw_line(
                p.x, p.y,
                p.x + n.x * 10,
                p.y + n.y * 10,
                (255, 0, 0, 255),
                1
            )


class LightFilter(LightInteractor):

    def __init__(self, position: Vec2, direction: Vec2, width: float, height: float):
        bounds = (
            Vec2(-width/2, -height/2),
            Vec2(-width/2, height/2),
            Vec2(width/2, height/2),
            Vec2(width/2, -height/2)
        )
        super().__init__(position, direction, bounds)

    def calculate_interaction(self, beam: LightBeam, edge: Tuple[Vec2, Vec2, Vec2, "LightInteractor"]) -> Tuple[LightBeam, ...]:
        if not any(a == b for a, b in zip(beam.components, self._components)):
            return ()

        


class LightConcave(LightInteractor):
    pass


class LightConvex(LightInteractor):
    pass


class LightPrism(LightInteractor):
    pass