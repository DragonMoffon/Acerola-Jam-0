from arcade import View

from engine.scene import LevelDirector


class GameView(View):

    def __init__(self):
        super().__init__()

        self._director: LevelDirector = LevelDirector()

    @property
    def level_director(self) -> LevelDirector:
        return self._director

    def on_draw(self):
        self.clear()
