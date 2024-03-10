from arcade.resources import resolve_resource_path
from pathlib import Path


def save_to_file(target_name: Path):
    pass


def load_from_file(target_name: Path):
    pass


class LevelScene:

    def __init__(self, do_auto_instantiate: bool = False):
        self._instantiated: bool = do_auto_instantiate

    def instantiate_level(self):
        pass


class LevelDirector:

    def __init__(self, scene_pack: Path, do_async_load: bool):
        pass
