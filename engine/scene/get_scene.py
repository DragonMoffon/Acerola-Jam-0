from typing import TYPE_CHECKING, Tuple

from engine.get_window import get_window
from engine.views import GameView

if TYPE_CHECKING:
    from engine.scene import LevelDirector, LevelScene
    from engine.scene.scene_object_types import SceneObject


def get_director() -> LevelDirector:
    win = get_window()
    if type(win.view) != GameView:
        raise ValueError("Game View is now currently showing cannot get director")

    return win.view.level_director


def get_active_scene(scene_name: str) -> LevelScene:
    return get_director().active_scene


def get_objects_with_id(str_id: str) -> Tuple[SceneObject, ...]:
    return get_director().active_scene.get_objects_with_id(str_id)
