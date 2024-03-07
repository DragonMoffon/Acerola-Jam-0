from arcade import Window, Sprite, SpriteList
from arcade.experimental.clock.clock import Clock
from arcade.camera import Camera2D

from engine.upscale_buffer import UpscaleBuffer
from engine.light.light_scene import LightScene
from engine.light.test_scene import generate_test_scene

from pyglet.math import Vec2

APP_WIDTH: int = 800
APP_HEIGHT: int = 600

DOWNSCALE_WIDTH: int = APP_WIDTH // 2
DOWNSCALE_HEIGHT: int = APP_HEIGHT // 2


class App(Window):

    def __init__(self):
        self.clock = Clock()
        super().__init__(width=APP_WIDTH, height=APP_HEIGHT, title="Ace's Chroma Chaos")
        self._base_upscale_buffer: UpscaleBuffer = UpscaleBuffer(DOWNSCALE_WIDTH, DOWNSCALE_HEIGHT)
        self._base_camera: Camera2D = Camera2D(
            position=(0.0, 0.0),
            viewport=(0, 0, DOWNSCALE_WIDTH, DOWNSCALE_HEIGHT),
            projection=(-DOWNSCALE_WIDTH//2, DOWNSCALE_WIDTH//2, -DOWNSCALE_HEIGHT//2, DOWNSCALE_HEIGHT//2)
        )

        self._light_scene_test: LightScene = generate_test_scene()

    def _dispatch_updates(self, delta_time: float):
        self.clock.tick(delta_time)
        self.dispatch_event('on_update', delta_time)

    def on_update(self, delta_time: float):
        #t = tuple(self._light_scene_test.interactor_manager._active_interactors)[0]
        #t.set_direction(t.direction.rotate(delta_time * 3.14159 * 0.05))

        p = self._light_scene_test._projectors[0]
        p.set_direction(p.direction.rotate(delta_time * 3.14159 * 0.15))

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