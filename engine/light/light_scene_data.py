from typing import Tuple, Dict, Any

from pyglet.math import Vec2


class LightInteractorData:

    def __init__(self):
        pass

    @staticmethod
    def from_data_dict(data: Dict[str, Any]):
        pass


class LightProjectorData:

    def __init__(self):
        pass

    @staticmethod
    def from_data_dict(data: Dict[str, Any]):
        pass


class LightData:

    def __init__(self):
        pass

    @staticmethod
    def from_data_dict(data: Dict[str, Any]):
        pass


class LightSceneData:

    def __init__(self):
        self._interactors: Tuple[LightInteractorData]
        self._projectors: Tuple[LightProjectorData]
        self._capture_zones: Tuple[Any, ...]
        self._lights

    @staticmethod
    def from_data_file(src: str):
        pass