from typing import Dict, Set
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
        self._object_map: Dict[str, WeakSet] = dict()

        self._lights: None
        self._light_interactors: None
        self._player_interactables: None

    def instantiate_level(self):
        pass

    def draw(self):
        pass

    def update(self):
        pass


class SubScene:
    """
    A sub scene is a group of object comprised together than can be manipulated as a single SceneObject.
    Used by ProjectorLights to create intractable environments that can be manipulated like the rest of the scene,
    """

    def __init__(self):
        pass


class LevelPack:

    def __init__(self, path: Path):
        self._levels: Dict[str, Dict] = dict()

        self._loaded_levels: Set[str] = set()



class LevelDirector:

    def __init__(self, level_pack: Path | None = None, do_async_load: bool = True):
        self._pack: LevelPack = LevelPack(level_pack or Path("default.zip"))
        self._loaded_scenes: Dict[str, LevelScene] = dict()
        self._active_scene: LevelScene | None = None

    @property
    def active_scene(self):
        return self._active_scene

    def update(self):
        if self._active_scene is None:
            return

        self._active_scene.update()

    def draw(self):
        if self._active_scene is None:
            return

        self._active_scene.draw()
