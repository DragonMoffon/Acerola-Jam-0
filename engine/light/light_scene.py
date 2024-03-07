from typing import Tuple

from engine.scene_renderer import SceneRenderer

from engine.light.light_scene_data import LightSceneData
from engine.light.light_interactors import LightInteractorManager
from engine.light.light_projector import LightProjector


class LightScene:
    """
    The base object which holds everything needed for the lighting calculations
    | - Interaction Manager
    | - Projectors
    | - Capture Zones
    | - Aberration Zones
    | - Lights
    | - light Renderer
    """

    def __init__(self, scene_renderer: SceneRenderer, interaction_manager: LightInteractorManager, projectors: Tuple[LightProjector, ...]):
        self._scene_renderer: SceneRenderer = scene_renderer
        self._interactor_manager: LightInteractorManager = interaction_manager
        self._projectors: Tuple[LightProjector, ...] = projectors

    @staticmethod
    def from_data(data: LightSceneData) -> "LightScene":
        # TODO
        pass

    @property
    def interactor_manager(self):
        return self._interactor_manager

    def draw(self):
        for projector in self._projectors:
            projector.debug_draw()

    def debug_draw(self):
        self._interactor_manager.debug_draw()
        for projector in self._projectors:
            projector.debug_draw()
