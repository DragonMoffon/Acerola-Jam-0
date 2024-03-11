from arcade.resources import resolve_resource_path
from pathlib import Path
from weakref import WeakSet

from engine.scene.scene_object_types import SceneObject


def save_to_file(target_name: Path):
    pass


def load_from_file(target_name: Path):
    pass


class LevelScene:

    def __init__(self, do_auto_instantiate: bool = False):
        self._name: str

        self._instantiated: bool = False

        self._all_objects: WeakSet[SceneObject] = WeakSet()

        self._lights: None
        self._light_interactors: None
        self._player_interactables: None

    def instantiate_level(self):
        pass


class SubScene:
    """
    A sub scene is a group of object comprised together than can be manipulated as a single SceneObject.
    Used by ProjectorLights to create intractable environments that can be manipulated like the rest of the scene,
    """


    def __init__(self):
        pass


class LevelDirector:

    def __init__(self, scene_pack: Path, do_async_load: bool):
        pass
