from arcade import View, SpriteSolidColor
from arcade.experimental.background import Background

from engine.data import DOWNSCALE_WIDTH, DOWNSCALE_HEIGHT
from engine.get_window import get_window


class GameView(View):

    def __init__(self):
        super().__init__()

    def on_draw(self):
        self.clear()
