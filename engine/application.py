from typing import Optional, Tuple

from arcade import Window
from arcade.experimental.clock.clock import Clock
from arcade.camera import Camera2D
from arcade.types import RGBA255OrNormalized

from engine.upscale_buffer import UpscaleBuffer
from engine.light.light_scene import LightScene
from engine.light.test_scene import generate_test_scene

from engine.views import EditorView, GameView, MenuView, SplashView
from engine.data import APP_WIDTH, APP_HEIGHT, DOWNSCALE_WIDTH, DOWNSCALE_HEIGHT


class App(Window):

    def __init__(self):
        super().__init__(width=APP_WIDTH, height=APP_HEIGHT, title="Ace's Chroma Chaos",
                         vsync=False, update_rate=1/5000)
        self._base_upscale_buffer: UpscaleBuffer = UpscaleBuffer(DOWNSCALE_WIDTH, DOWNSCALE_HEIGHT)
        self._base_camera: Camera2D = Camera2D(
            position=(0.0, 0.0),
            viewport=(0, 0, DOWNSCALE_WIDTH, DOWNSCALE_HEIGHT),
            projection=(-DOWNSCALE_WIDTH//2, DOWNSCALE_WIDTH//2, -DOWNSCALE_HEIGHT//2, DOWNSCALE_HEIGHT//2)
        )
        self._base_upscale_buffer.use()
        self._base_camera.use()

        self._clock: Clock = Clock()

        self._editor_view: EditorView
        self._game_view: GameView = GameView()
        self._menu_view: MenuView

        splash_view: SplashView

        self.show_view(self._game_view)


    @property
    def upscale_buffer(self) -> UpscaleBuffer:
        return self._base_upscale_buffer

    @property
    def base_camera(self) -> Camera2D:
        return self._base_camera

    @property
    def clock(self):
        return self._clock

    def _dispatch_updates(self, delta_time: float):
        self.clock.tick(delta_time)
        self.dispatch_event('on_update', delta_time)

    def on_update(self, delta_time: float):
        from math import pi, sin, cos, floor
        self._base_camera.position = (cos(self._clock.elapsed * 0.5 * pi) * 30, sin(self._clock.elapsed * 0.5 * pi) * 30)

    def clear(
            self,
            color: Optional[RGBA255OrNormalized] = None,
            normalized: bool = False,
            viewport: Optional[Tuple[int, int, int, int]] = None,
    ):
        color = color if color is not None else self.background_color
        self.ctx.screen.clear(color, normalized=normalized, viewport=viewport)
        self._base_upscale_buffer.clear()

    def on_draw(self):
        with self.ctx.screen.activate() as fbo:
            fbo.clear()
            self._base_upscale_buffer.draw()

        self._base_camera.use()


class App_OLD(Window):

    def __init__(self):
        self.clock = Clock()
        super().__init__(width=APP_WIDTH, height=APP_HEIGHT, title="Ace's Chroma Chaos",
                         vsync=False, update_rate=1/5000)
        self._base_upscale_buffer: UpscaleBuffer = UpscaleBuffer(DOWNSCALE_WIDTH, DOWNSCALE_HEIGHT)
        self._base_camera: Camera2D = Camera2D(
            position=(0.0, 0.0),
            viewport=(0, 0, DOWNSCALE_WIDTH, DOWNSCALE_HEIGHT),
            projection=(-DOWNSCALE_WIDTH//2, DOWNSCALE_WIDTH//2, -DOWNSCALE_HEIGHT//2, DOWNSCALE_HEIGHT//2)
        )

        self._light_scene_test: LightScene = generate_test_scene()

        self._test_dir = 1
        self._test_t = 0.0

    def on_key_press(self, symbol: int, modifiers: int):
        self._test_dir = 1 - self._test_dir

    def _dispatch_updates(self, delta_time: float):
        self.clock.tick(delta_time)
        self.dispatch_event('on_update', delta_time)

    def on_update(self, delta_time: float):
        print(1/delta_time)
        t = tuple(self._light_scene_test.interactor_manager._active_interactors)[0]
        t.set_direction(t.direction.rotate(delta_time * 3.14159 * 0.05))

        p = self._light_scene_test._projectors[0]
        p.set_direction(p.direction.rotate((2*self._test_dir - 1) * delta_time * 3.14159 * 0.01))

    def on_draw(self):
        self.clear()
        with self._base_upscale_buffer.activate() as fbo:
            fbo.clear()
            with self._base_camera.activate():
                self._light_scene_test.debug_draw()
        self._base_upscale_buffer.draw()


def launch_window():
    app = App()
    app.run()