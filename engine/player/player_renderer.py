from typing import Tuple

from engine.scene.scene_object_types import SceneObject, SceneObjectRenderer


from arcade import Sprite


class PlayerRenderer(SceneObjectRenderer):

    def __init__(self, player_object: SceneObject):
        super().__init__(player_object)

        self._player_sprite: Sprite = Sprite(":r:Ace_top_down.png")

    def _redraw(self):
        self._player_sprite.position = self._target.origin
        self._player_sprite.radians = self._target.direction.heading
        self._player_sprite.color = self._target.get_colour()

    def _render(self):
        self._player_sprite.draw(pixelated=True)

    def decompose(self, decomp: Tuple[SceneObject, ...]):
        raise NotImplementedError()
