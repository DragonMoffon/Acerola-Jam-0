from typing import Tuple, Set, Callable, Dict
from weakref import WeakSet
from pyglet.math import Vec2

from arcade import draw_polygon_outline, draw_point


class SceneObject:

    def __init__(self, origin: Vec2, direction: Vec2, components: Tuple[bool, bool, bool]):
        self._origin: Vec2 = origin
        self._direction: Vec2 = direction
        self._normal: Vec2 = Vec2(-direction.y, direction.x)
        self._components: Tuple[bool, bool, bool] = components

        self._children: Set[SceneObject] = set()

    def __str__(self):
        return f"SceneObj<{self._origin}, {self._direction}, {self._components}>"

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.__str__())

    def __eq__(self, other: "SceneObject"):
        return (
                other.origin == self._origin and
                other.direction == self._direction and
                other.components == self._components
        )

    def set_origin(self, new_origin: Vec2):
        if new_origin == self._origin:
            return

        self._origin = new_origin

        self.propagate_update()

    def set_direction(self, new_direction: Vec2):
        if new_direction == self._direction:
            return

        self._direction = new_direction

        self.propagate_update()

    def set_components(self, new_components: Tuple[bool, bool, bool]):
        if new_components == self._components:
            return

        self._components = new_components

        self.propagate_update()

    def add_child(self, child: "SceneObject"):
        self._children.add(child)

    def has_child(self, child: "SceneObject"):
        return child in self._children

    def remove_child(self, child: "SceneObject"):
        self._children.discard(child)

    def propagate_update(self):
        raise NotImplementedError()

    def kill(self):
        raise NotImplementedError()

    def propagate_kill(self):
        self.kill()

        for child in tuple(self._children):
            child.propagate_kill()
        self._children.clear()

    def debug_draw(self):
        ...

    def get_colour(self, _alpha: int = 255):
        return 255*self._components[0], 255*self._components[1], 255*self._components[2], _alpha

    @property
    def origin(self):
        return self._origin

    @property
    def direction(self):
        return self._direction

    @property
    def normal(self):
        return self._normal

    @property
    def components(self):
        return self._components

    @property
    def is_white(self):
        return all(self._components)

    @property
    def is_black(self):
        return not self.is_white

    @property
    def is_yellow(self):
        return self._components[0] and self._components[1]

    @property
    def is_cyan(self):
        return self._components[1] and self._components[2]

    @property
    def is_magenta(self):
        return self._components[2] and self._components[2]

    @property
    def is_red(self):
        return self._components[0]

    @property
    def is_green(self):
        return self._components[1]

    @property
    def is_blue(self):
        return self._components[2]


class SceneLight(SceneObject):

    def __init__(self, origin: Vec2, direction: Vec2, strength: float, components: Tuple[bool, bool, bool]):
        super().__init__(origin, direction, components)
        self._strength: float = strength

    def propagate_update(self):
        raise NotImplementedError()

    def kill(self):
        raise NotImplementedError()

    def debug_draw(self):
        ...


class LightInteractor(SceneObject):

    def __init__(self, origin: Vec2, direction: Vec2, bounds: Tuple[Vec2, ...], components: Tuple[bool, bool, bool]):
        super().__init__(origin, direction, components)
        if len(bounds) < 3:
            raise ValueError()

        self._bounds: Tuple[Vec2, ...] = bounds
        self._normals: Tuple[Vec2, ...] = tuple(
            (bounds[(i + 1) % len(self._bounds)] - bounds[i]).normalize()
            for i in range(len(bounds))
        )

        self._ingoing_light: WeakSet[SceneLight] = WeakSet()
        self._outgoing_light: WeakSet[SceneLight] = WeakSet()

    def remove_ingoing_light(self, light: SceneLight):
        self._ingoing_light.discard(light)

    def add_ingoing_light(self, light: SceneLight):
        self._ingoing_light.add(light)

    def remove_outgoing_light(self, light: SceneLight):
        self._outgoing_light.discard(light)

    def add_outgoing_light(self, light: SceneLight):
        self._outgoing_light.add(light)

    def get_edge(self, idx: int):
        return self._bounds[idx], self._normals[idx], self._bounds[(idx + 1) % len(self._bounds)]

    def get_edge_adjusted(self, idx: int):
        return (
            self._origin + self._bounds[idx].rotate(self._normal.heading),
            self._normals[idx].rotate(self._normal.heading),
            self._origin + self._bounds[(idx + 1) % len(self._bounds)].rotate(self._normal.heading)
        )

    def get_edges(self):
        return tuple(
            (self._bounds[idx], self._normals[idx], self._bounds[(idx + 1) % len(self._bounds)])
            for idx in range(len(self._bounds))
        )

    def get_edges_adjusted(self):
        return tuple(
            (
                self._origin + self._bounds[idx].rotate(self._normal.heading),
                self._normals[idx].rotate(self._normal.heading),
                self._origin + self._bounds[(idx + 1) % len(self._bounds)].rotate(self._normal.heading)
            )
            for idx in range(len(self._bounds))
        )

    def get_bounds_adjusted(self):
        return tuple(self._origin + self._bounds[idx].rotate(self._normal.heading) for idx in range(len(self._bounds)))

    def get_normals_adjusted(self):
        return tuple(normal.rotate(self._normal.heading) for normal in self._normals)

    @property
    def bounds(self):
        return self._bounds

    @property
    def normals(self):
        return self._normals

    def calculate_interaction(self, edge_idx: int, start_point: Vec2, start_dir: Vec2, end_point: Vec2, end_dir: Vec2):
        raise NotImplementedError()

    def propagate_update(self):
        raise NotImplementedError()

    def kill(self):
        raise NotImplementedError()

    def propagate_kill(self):
        self.kill()

        for child in tuple(self._children):
            child.propagate_kill()
        self._children.clear()

    def debug_draw(self):
        _p = self.get_edges_adjusted()

        draw_polygon_outline(_p, self.get_colour(), 1)
        draw_point(self._origin.x, self._origin.y, self.get_colour(), 2)


class PlayerInteractor(SceneObject):

    def __init__(self, origin: Vec2, direction: Vec2,
                 interaction_callback: Callable,
                 interaction_kwargs: Dict,
                 interaction_state: Dict,
                 components: Tuple[bool, bool, bool]
                 ):
        super().__init__(origin, direction, components)
        self._callback: Callable = interaction_callback
        self._kwargs: Dict = interaction_kwargs
        self._state: Dict = interaction_state

        self._interacting: bool = False

    def begin_interaction(self):
        raise NotImplementedError()

    def end_interaction(self):
        raise NotImplementedError()

    def propagate_update(self):
        raise NotImplementedError()

    def kill(self):
        raise NotImplementedError()

    def debug_draw(self):
        draw_point(self._origin.x, self._origin.y, self.get_colour(), 4)


